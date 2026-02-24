from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import date
import random
import logging

from .models import Question, Topic, AnswerOption, UserProgress
from .serializers import (
    QuestionSerializer, SubmitAnswerSerializer,
    TopicProgressSerializer
)
from .services import LearningService
from subscriptions.services import SubscriptionService

logger = logging.getLogger(__name__)

def get_user_lang(request):
    try:
        return request.user.profile.ui_language or 'en'
    except Exception:
        return 'en'


class DailyQuestionsView(APIView):
    def get(self, request, *args, **kwargs):
        questions = LearningService.get_daily_questions(request.user)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionListView(generics.ListAPIView):
    # OPTIMIZATION: Use select_related to avoid N+1 queries
    # DEPRECATED: Not used by frontend, kept for backward compatibility
    queryset = Question.objects.select_related('topic').filter(is_active=True)
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['difficulty', 'specialization', 'language', 'topic']


class TopicListView(generics.ListAPIView):
    """
    GET /api/learning/topics/
    Returns topics filtered by user's primary language.
    """
    serializer_class = TopicProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            language = self.request.user.profile.primary_language
        except Exception:
            language = 'python'
        # OPTIMIZATION: Add select_related for related questions
        return Topic.objects.select_related().filter(
            language=language,
            is_active=True
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = get_user_lang(self.request)
        return ctx


class TopicQuestionsView(generics.ListAPIView):
    """
    GET /api/learning/topics/{id}/questions/
    Returns questions for a specific topic, unanswered first.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        topic_id = self.kwargs['topic_id']
        user = self.request.user

        # OPTIMIZATION: Use select_related and prefetch_related
        questions_list = list(Question.objects.select_related(
            'topic'
        ).prefetch_related(
            'options'
        ).filter(
            topic_id=topic_id,
            is_active=True
        ))

        random.shuffle(questions_list)
        return questions_list

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = get_user_lang(self.request)
        return ctx

class AnswerQuestionView(APIView):
    """
    POST /api/learning/answer/
    Answers a question and returns XP/progress.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question_id = request.data.get('question_id')
        # OPTIMIZATION: Use select_related to fetch topic with question
        question = get_object_or_404(
            Question.objects.select_related('topic'), 
            id=question_id
        )

        if question.question_type in ['multiple_choice', 'true_false']:
            answer_option_id = request.data.get('answer_option_id')
            # OPTIMIZATION: Fetch options with select_related
            selected = get_object_or_404(
                AnswerOption.objects.select_related('question'), 
                id=answer_option_id
            )
            is_correct = selected.is_correct
            correct_option = question.options.filter(is_correct=True).first()
        elif question.question_type == 'text':
            answer_text = request.data.get('answer_text', '').strip().lower()
            correct = question.options.filter(is_correct=True).first()
            is_correct = (answer_text == correct.text.lower()) if correct else False
            correct_option = correct
        else:
            logger.warning(f"Unsupported question type: {question.question_type}")
            return Response(
                {"error": "Unsupported question type"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # SECURITY: Check if the user has already answered this question correctly today
        # This prevents XP farming by answering the same question repeatedly
        from django.utils import timezone
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        previously_answered_correctly_today = UserProgress.objects.filter(
            user=request.user,
            question=question,
            is_correct=True,
            answered_at__gte=today_start
        ).exists()

        if previously_answered_correctly_today:
            xp_earned = 0
            logger.info(f"User {request.user.id} already answered question {question_id} correctly today - no XP awarded")
        else:
            xp_earned = question.xp_reward if is_correct else 0

        # Record progress for the session
        session_id = request.data.get('session_id')
        UserProgress.objects.create(
            user=request.user,
            question=question,
            is_correct=is_correct,
            xp_earned=xp_earned,
            session_id=session_id
        )

        # Only award XP if not previously answered correctly today
        if xp_earned > 0:
            from gamification.services import XPService
            XPService.add_xp(request.user, xp_earned)
            logger.info(f"User {request.user.id} earned {xp_earned} XP for question {question_id}")

        # Calculate today's total XP
        total_xp = UserProgress.objects.filter(
            user=request.user,
            answered_at__gte=today_start
        ).aggregate(total=Sum('xp_earned'))['total'] or 0

        # OPTIMIZATION: Calculate topic progress efficiently
        topic = question.topic
        topic_progress = 0
        if topic:
            total_q = topic.questions.count()
            done_q = UserProgress.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).values('question').distinct().count()
            topic_progress = round((done_q / total_q) * 100) if total_q else 0

        lang = get_user_lang(request)
        return Response({
            'is_correct': is_correct,
            'correct_option_id': correct_option.id if correct_option else None,
            'explanation': question.get_explanation(lang),
            'xp_earned': xp_earned,
            'total_xp_today': total_xp,
            'topic_progress': topic_progress,
            'previously_answered': previously_answered_correctly_today
        })

class SessionSummaryView(APIView):
    """
    GET /api/learning/session/summary/?topic_id=5
    Returns summary stats for the current session.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        qs = UserProgress.objects.filter(
            user=request.user,
            session_id=session_id
        )
        
        total = qs.count()
        correct = qs.filter(is_correct=True).count()
        xp = qs.aggregate(Sum('xp_earned'))['xp_earned__sum'] or 0
        
        return Response({
            'total_answered': total,
            'correct': correct,
            'accuracy': round((correct/total)*100) if total else 0,
            'xp_earned': xp,
        })
