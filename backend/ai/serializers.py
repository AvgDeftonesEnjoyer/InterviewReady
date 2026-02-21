from rest_framework import serializers

class EvaluateSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()
