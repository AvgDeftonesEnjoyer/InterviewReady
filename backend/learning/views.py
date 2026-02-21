from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Question
from .serializers import QuestionSerializer, SubmitAnswerSerializer
from .services import LearningService
from subscriptions.services import SubscriptionService

class DailyQuestionsView(APIView):
    def get(self, request, *args, **kwargs):
        questions = LearningService.get_daily_questions(request.user)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListView(generics.ListAPIView):
    queryset = Question.objects.filter(is_active=True)
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['difficulty', 'category', 'language']

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
