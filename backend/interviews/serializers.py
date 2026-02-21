from rest_framework import serializers
from .models import InterviewSession, InterviewMessage

class StartInterviewSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=InterviewSession.TYPE_CHOICES)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewMessage
        fields = ('id', 'role', 'text', 'created_at')

class InterviewSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = InterviewSession
        fields = ('id', 'type', 'status', 'score', 'started_at', 'finished_at', 'messages')

class SendMessageSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    text = serializers.CharField()

class FinishSessionSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
