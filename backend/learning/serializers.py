from rest_framework import serializers
from .models import Question, AnswerOption, Topic, UserProgress

class TopicProgressSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    completed_questions = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        lang = self.context.get('lang', 'en')
        return obj.get_name(lang)

    def get_total_questions(self, obj):
        return obj.questions.filter(is_active=True).count()

    def get_completed_questions(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        return UserProgress.objects.filter(
            user=user,
            question__topic=obj,
            is_correct=True
        ).values('question').distinct().count()

    def get_progress_percent(self, obj):
        total = self.get_total_questions(obj)
        if total == 0:
            return 0
        done = self.get_completed_questions(obj)
        return round((done / total) * 100)

    def get_is_completed(self, obj):
        return self.get_progress_percent(obj) == 100

    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'icon', 'language',
            'total_questions', 'completed_questions',
            'progress_percent', 'is_completed'
        ]

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    is_answered = serializers.SerializerMethodField()
    
    def get_text(self, obj):
        lang = self.context.get('lang', 'en')
        return obj.get_text(lang)

    def get_options(self, obj):
        lang = self.context.get('lang', 'en')
        return [
            {
                'id': opt.id,
                'text': opt.get_text(lang),
                'order': opt.order
            }
            for opt in obj.options.all()
        ]

    def get_is_answered(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return False
            
        return UserProgress.objects.filter(
            user=user,
            question=obj,
            is_correct=True
        ).exists()

    class Meta:
        model = Question
        fields = [
            'id', 'text', 'question_type',
            'difficulty', 'xp_reward',
            'options', 'is_answered'
        ]

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
