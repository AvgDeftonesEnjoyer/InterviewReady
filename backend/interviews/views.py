from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404, aget_object_or_404
from django.utils import timezone
from asgiref.sync import sync_to_async, async_to_sync
import logging

from .models import InterviewSession
from .services import get_quota
from .prompts import build_prompt
from .openai_client import aget_ai_response, atranscribe_audio

logger = logging.getLogger(__name__)


class QuotaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        quota = get_quota(user)
        return Response(quota)


class StartInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return async_to_sync(self._async_post)(request)

    async def _async_post(self, request):
        # Safely get the user in async context
        user = await sync_to_async(lambda: request.user)()

        # 1. Check quota
        quota = await sync_to_async(get_quota)(user)
        if not quota['can_start']:
            return Response({
                'error': 'quota_exceeded',
                'quota': quota,
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Validate mode
        mode = request.data.get('mode')
        valid_modes = [c[0] for c in InterviewSession.Mode.choices]
        if mode not in valid_modes:
            return Response({'error': f'Invalid mode. Use: {", ".join(valid_modes)}'}, status=400)

        language = request.data.get('language', '')
        if mode in [InterviewSession.Mode.TECH, InterviewSession.Mode.COMBINED] and not language:
            return Response({'error': 'Language required for tech/combined mode'}, status=400)

        # 3. Question count: 10 / 15 / 20
        count = int(request.data.get('question_count', 10))
        if count not in [10, 15, 20]:
            count = 10

        # 4. Generate first message from AI
        # (Errors like OpenAITimeoutError are caught globally via custom_exception_handler)
        system_prompt = build_prompt(mode, language, count)
        first_message = await aget_ai_response(system_prompt, [
            {'role': 'user', 'content': 'Start the interview.'}
        ])

        # 5. Create session asynchronously
        session = await InterviewSession.objects.acreate(
            user=user,
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
            'quota': await sync_to_async(get_quota)(user),
        }, status=status.HTTP_201_CREATED)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        return async_to_sync(self._async_post)(request, session_id)

    async def _async_post(self, request, session_id):
        user = await sync_to_async(lambda: request.user)()

        session = await aget_object_or_404(
            InterviewSession,
            id=session_id,
            user=user,
            status=InterviewSession.Status.ACTIVE
        )

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Empty message'}, status=400)

        # Add user message
        session.messages.append({'role': 'user', 'content': content})

        # Build prompt and get AI response
        # (Errors like OpenAITimeoutError are caught globally via custom_exception_handler)
        system_prompt = build_prompt(
            session.mode,
            session.language,
            session.question_count_target,
            current_question=session.question_count
        )
        ai_response = await aget_ai_response(system_prompt, session.messages)

        # Check completion signal
        is_complete = '[INTERVIEW_COMPLETE]' in ai_response
        ai_response = ai_response.replace('[INTERVIEW_COMPLETE]', '').strip()

        session.messages.append({'role': 'assistant', 'content': ai_response})

        if not is_complete:
            session.question_count += 1
        else:
            session.status = InterviewSession.Status.COMPLETED
            session.finished_at = timezone.now()

        await session.asave()

        return Response({
            'message': ai_response,
            'is_complete': is_complete,
            'question_count': session.question_count,
            'total': session.question_count_target,
        })


class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        user = request.user
        session = get_object_or_404(
            InterviewSession,
            id=session_id,
            user=user
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
        return async_to_sync(self._async_post)(request)

    async def _async_post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({'error': 'No audio file provided'}, status=400)
        
        # Validate file type
        allowed_types = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/webm', 'audio/mp4']
        content_type = getattr(audio_file, 'content_type', '')
        if content_type and content_type not in allowed_types:
            logger.warning(f"Invalid audio file type: {content_type}")
            return Response({
                'error': 'invalid_file_type',
                'message': 'Please upload a valid audio file (MP3, WAV, WebM, or MP4)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 25MB for Whisper)
        max_size = 25 * 1024 * 1024  # 25MB
        file_size = getattr(audio_file, 'size', 0)
        if file_size > max_size:
            logger.warning(f"Audio file too large: {file_size} bytes")
            return Response({
                'error': 'file_too_large',
                'message': 'Audio file must be less than 25MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Errors handled globally via custom_exception_handler
        text = await atranscribe_audio(audio_file)
        return Response({'text': text})
