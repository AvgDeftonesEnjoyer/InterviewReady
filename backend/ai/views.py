from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from .serializers import EvaluateSerializer
from .services import AIService, AIUsageService

class EvaluateView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai_requests'

    def post(self, request, *args, **kwargs):
        if not AIUsageService.can_use_ai(request.user):
            return Response({"error": "AI usage limit reached for today."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EvaluateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']
        answer = serializer.validated_data['answer']
        
        evaluation = AIService.evaluate_answer(question, answer)
        followup = AIService.generate_followup(evaluation)

        AIUsageService.increment_usage(request.user)
        
        return Response({
            "evaluation": evaluation,
            "followup": followup
        }, status=status.HTTP_200_OK)
