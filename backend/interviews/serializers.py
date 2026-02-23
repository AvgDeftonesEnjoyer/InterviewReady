from rest_framework import serializers
from .models import InterviewSession


class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ('id', 'mode', 'language', 'status', 'question_count', 'question_count_target', 'started_at', 'finished_at', 'messages')
