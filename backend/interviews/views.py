from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import InterviewSession
from .serializers import (
    StartInterviewSerializer,
    InterviewSessionSerializer,
    SendMessageSerializer,
    FinishSessionSerializer,
    MessageSerializer
)
from .services import InterviewService

class StartInterviewView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StartInterviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            session = InterviewService.start_session(
                user=request.user,
                interview_type=serializer.validated_data['type']
            )
            return Response(InterviewSessionSerializer(session).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InterviewMessageView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = get_object_or_404(InterviewSession, id=serializer.validated_data['session_id'], user=request.user)
        
        try:
            bot_message = InterviewService.process_answer(
                session=session,
                user_message=serializer.validated_data['text']
            )
            return Response(MessageSerializer(bot_message).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FinishInterviewView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FinishSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = get_object_or_404(InterviewSession, id=serializer.validated_data['session_id'], user=request.user)
        
        session = InterviewService.finish_session(session)
        return Response(InterviewSessionSerializer(session).data, status=status.HTTP_200_OK)
