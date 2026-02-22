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

from .models import Question, Topic, AnswerOption, UserProgress
from .serializers import (
    QuestionSerializer, SubmitAnswerSerializer, 
    TopicProgressSerializer
)
from .services import LearningService
from subscriptions.services import SubscriptionService

def get_user_lang(request):
    try:
        return request.user.profile.ui_language or 'en'
    except:
        return 'en'

class DailyQuestionsView(APIView):
    def get(self, request, *args, **kwargs):
        questions = LearningService.get_daily_questions(request.user)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.filter(is_active=True)
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['difficulty', 'specialization', 'language', 'topic']

class SubmitAnswerView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = LearningService.submit_answer(
                user=request.user,
                question_id=serializer.validated_data['question_id'],
                option_id=serializer.validated_data['option_id']
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        return Topic.objects.filter(
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
        
        # We don't filter out answered questions here anymore, because 
        # the session might want to include them for practice, 
        # and the frontend handles the unique session flow.
        questions_list = list(Question.objects.filter(
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
        question = get_object_or_404(Question, id=question_id)
        
        if question.question_type in ['multiple_choice', 'true_false']:
            answer_option_id = request.data.get('answer_option_id')
            selected = get_object_or_404(AnswerOption, id=answer_option_id)
            is_correct = selected.is_correct
            correct_option = question.options.filter(is_correct=True).first()
        elif question.question_type == 'text':
            answer_text = request.data.get('answer_text', '').strip().lower()
            correct = question.options.filter(is_correct=True).first()
            is_correct = (answer_text == correct.text.lower()) if correct else False
            correct_option = correct
        else:
            return Response({"error": "Unsupported question type"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if the user has already answered this question correctly before
        previously_answered_correctly = UserProgress.objects.filter(
            user=request.user,
            question=question,
            is_correct=True
        ).exists()

        if previously_answered_correctly:
            xp_earned = 0
        else:
            xp_earned = question.xp_reward if is_correct else 0
        
        # Always record progress for the session so that session summaries are accurate.
        # XP manipulation is prevented because xp_earned is 0 if previously answered.
        session_id = request.data.get('session_id')
        UserProgress.objects.create(
            user=request.user,
            question=question,
            is_correct=is_correct,
            xp_earned=xp_earned,
            session_id=session_id
        )
        
        if xp_earned > 0:
            from gamification.services import XPService
            XPService.add_xp(request.user, xp_earned)
        
        from django.utils import timezone
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        total_xp = UserProgress.objects.filter(
            user=request.user,
            answered_at__gte=today_start
        ).aggregate(total=Sum('xp_earned'))['total'] or 0
        
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
            'previously_answered': previously_answered_correctly
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
