from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging

from .models import InterviewSession
from .services import get_quota
from .prompts import build_prompt
from .openai_client import get_ai_response, transcribe_audio, OpenAIError, OpenAIRateLimitError, OpenAITimeoutError, OpenAIConnectionError, OpenAIServerError

logger = logging.getLogger(__name__)


class QuotaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_quota(request.user))


class StartInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Check quota
        quota = get_quota(request.user)
        if not quota['can_start']:
            return Response({
                'error': 'quota_exceeded',
                'quota': quota,
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Validate mode
        mode = request.data.get('mode')
        if mode not in ['hr', 'tech', 'combined']:
            return Response({'error': 'Invalid mode. Use: hr, tech, combined'}, status=400)

        language = request.data.get('language', '')
        if mode in ['tech', 'combined'] and not language:
            return Response({'error': 'Language required for tech/combined mode'}, status=400)

        # 3. Question count: 10 / 15 / 20
        count = int(request.data.get('question_count', 10))
        if count not in [10, 15, 20]:
            count = 10

        # 4. Generate first message from AI with error handling
        try:
            system_prompt = build_prompt(mode, language, count)
            first_message = get_ai_response(system_prompt, [
                {'role': 'user', 'content': 'Start the interview.'}
            ])
        except OpenAIRateLimitError as e:
            logger.warning(f"Rate limit error when starting interview: {str(e)}")
            return Response({
                'error': 'ai_rate_limit',
                'message': str(e)
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except OpenAITimeoutError as e:
            logger.error(f"Timeout error when starting interview: {str(e)}")
            return Response({
                'error': 'ai_timeout',
                'message': str(e)
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except OpenAIConnectionError as e:
            logger.error(f"Connection error when starting interview: {str(e)}")
            return Response({
                'error': 'ai_connection_error',
                'message': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except OpenAIServerError as e:
            logger.error(f"Server error when starting interview: {str(e)}")
            return Response({
                'error': 'ai_server_error',
                'message': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except OpenAIError as e:
            logger.error(f"OpenAI error when starting interview: {str(e)}")
            return Response({
                'error': 'ai_error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error when starting interview: {str(e)}")
            return Response({
                'error': 'unexpected_error',
                'message': 'Failed to start interview. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 5. Create session
        session = InterviewSession.objects.create(
            user=request.user,
            mode=mode,
            language=language,
            question_count_target=count,
            messages=[{'role': 'assistant', 'content': first_message}],
            question_count=1,
        )

        return Response({
            'session_id': session.id,
            'message': first_message,
            'question_count': session.question_count,
            'total': count,
            'quota': get_quota(request.user),
        }, status=status.HTTP_201_CREATED)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(
            InterviewSession,
            id=session_id,
            user=request.user,
            status='active'
        )

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Empty message'}, status=400)

        # Add user message
        session.messages.append({'role': 'user', 'content': content})

        # Build prompt and get AI response with error handling
        try:
            system_prompt = build_prompt(
                session.mode,
                session.language,
                session.question_count_target,
                current_question=session.question_count
            )
            ai_response = get_ai_response(system_prompt, session.messages)
        except OpenAIRateLimitError as e:
            logger.warning(f"Rate limit error in SendMessageView: {str(e)}")
            return Response({
                'error': 'ai_rate_limit',
                'message': str(e)
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except OpenAITimeoutError as e:
            logger.error(f"Timeout error in SendMessageView: {str(e)}")
            return Response({
                'error': 'ai_timeout',
                'message': str(e)
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except OpenAIConnectionError as e:
            logger.error(f"Connection error in SendMessageView: {str(e)}")
            return Response({
                'error': 'ai_connection_error',
                'message': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except OpenAIServerError as e:
            logger.error(f"Server error in SendMessageView: {str(e)}")
            return Response({
                'error': 'ai_server_error',
                'message': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except OpenAIError as e:
            logger.error(f"OpenAI error in SendMessageView: {str(e)}")
            return Response({
                'error': 'ai_error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in SendMessageView: {str(e)}")
            # Remove the user message since we couldn't get a response
            session.messages.pop()
            return Response({
                'error': 'unexpected_error',
                'message': 'Failed to process message. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check completion signal
        is_complete = '[INTERVIEW_COMPLETE]' in ai_response
        ai_response = ai_response.replace('[INTERVIEW_COMPLETE]', '').strip()

        session.messages.append({'role': 'assistant', 'content': ai_response})

        if not is_complete:
            session.question_count += 1

        if is_complete:
            session.status = 'completed'
            session.finished_at = timezone.now()

        session.save()

        return Response({
            'message': ai_response,
            'is_complete': is_complete,
            'question_count': session.question_count,
            'total': session.question_count_target,
        })


class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(
            InterviewSession,
            id=session_id,
            user=request.user
        )
        return Response({
            'session_id': session.id,
            'mode': session.mode,
            'language': session.language,
            'status': session.status,
            'messages': session.messages,
            'question_count': session.question_count,
            'total': session.question_count_target,
            'started_at': session.started_at,
            'finished_at': session.finished_at,
        })


class TranscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({'error': 'No audio file provided'}, status=400)
        
        # Validate file type
        allowed_types = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/webm', 'audio/mp4']
        content_type = audio_file.content_type if hasattr(audio_file, 'content_type') else ''
        if content_type and content_type not in allowed_types:
            logger.warning(f"Invalid audio file type: {content_type}")
            return Response({
                'error': 'invalid_file_type',
                'message': 'Please upload a valid audio file (MP3, WAV, WebM, or MP4)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 25MB for Whisper)
        max_size = 25 * 1024 * 1024  # 25MB
        file_size = audio_file.size if hasattr(audio_file, 'size') else 0
        if file_size > max_size:
            logger.warning(f"Audio file too large: {file_size} bytes")
            return Response({
                'error': 'file_too_large',
                'message': 'Audio file must be less than 25MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            text = transcribe_audio(audio_file)
            return Response({'text': text})
        except OpenAIRateLimitError as e:
            logger.warning(f"Rate limit error in TranscribeView: {str(e)}")
            return Response({
                'error': 'ai_rate_limit',
                'message': str(e)
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except OpenAITimeoutError as e:
            logger.error(f"Timeout error in TranscribeView: {str(e)}")
            return Response({
                'error': 'ai_timeout',
                'message': str(e)
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except OpenAIConnectionError as e:
            logger.error(f"Connection error in TranscribeView: {str(e)}")
            return Response({
                'error': 'ai_connection_error',
                'message': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except OpenAIError as e:
            logger.error(f"OpenAI error in TranscribeView: {str(e)}")
            return Response({
                'error': 'ai_error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in TranscribeView: {type(e).__name__} - {str(e)}")
            return Response({
                'error': 'transcription_failed',
                'message': 'Failed to transcribe audio. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
