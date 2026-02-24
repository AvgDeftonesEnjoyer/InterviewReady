from django.utils import timezone
from django.conf import settings
from subscriptions.services import SubscriptionService
from users.models import User
from .models import AIUsage
import openai
import logging

logger = logging.getLogger(__name__)


class AIUsageService:
    @staticmethod
    def get_or_create_usage(user: User) -> AIUsage:
        usage, _ = AIUsage.objects.get_or_create(user=user)
        return usage

    @staticmethod
    def can_use_ai(user: User) -> bool:
        AIUsageService.reset_if_new_day(user)
        usage = AIUsageService.get_or_create_usage(user)

        if SubscriptionService.is_pro(user):
            return True

        return usage.used_today < usage.daily_limit

    @staticmethod
    def increment_usage(user: User):
        usage = AIUsageService.get_or_create_usage(user)
        if not SubscriptionService.is_pro(user):
            usage.used_today += 1
            usage.save()

    @staticmethod
    def reset_if_new_day(user: User):
        usage = AIUsageService.get_or_create_usage(user)
        today = timezone.now().date()
        if usage.last_reset != today:
            usage.used_today = 0
            usage.last_reset = today
            usage.save()

    @staticmethod
    def reset_all_daily_usage():
        today = timezone.now().date()
        AIUsage.objects.exclude(last_reset=today).update(used_today=0, last_reset=today)


class AIService:
    """
    AI service for evaluating answers and generating questions.
    Uses configurable OpenAI model via OPENAI_EVALUATION_MODEL setting.
    """
    
    @staticmethod
    def _get_openai_client():
        """Create OpenAI client."""
        return openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30
        )
    
    @staticmethod
    def generate_hr_question() -> str:
        """Generate HR interview question using AI."""
        try:
            client = AIService._get_openai_client()
            response = client.chat.completions.create(
                model=settings.OPENAI_EVALUATION_MODEL,
                messages=[
                    {'role': 'system', 'content': 'You are an HR interviewer. Generate one behavioral interview question.'},
                    {'role': 'user', 'content': 'Generate one HR interview question about teamwork or leadership.'}
                ],
                max_tokens=100,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate HR question: {str(e)}")
            return "Can you tell me about a time you overcame a technical challenge?"

    @staticmethod
    def evaluate_answer(question: str, user_answer: str) -> str:
        """
        Evaluate user's answer using AI.
        Uses OPENAI_EVALUATION_MODEL setting.
        """
        try:
            client = AIService._get_openai_client()
            response = client.chat.completions.create(
                model=settings.OPENAI_EVALUATION_MODEL,
                messages=[
                    {'role': 'system', 'content': 'You are a technical interviewer. Evaluate the candidate\'s answer concisely and provide constructive feedback.'},
                    {'role': 'user', 'content': f'Question: {question}\n\nAnswer: {user_answer}\n\nPlease evaluate this answer and provide brief feedback.'}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to evaluate answer: {str(e)}")
            return f"Your answer was received. (AI evaluation temporarily unavailable)"

    @staticmethod
    def generate_followup(previous_message: str) -> str:
        """Generate follow-up question based on previous exchange."""
        try:
            client = AIService._get_openai_client()
            response = client.chat.completions.create(
                model=settings.OPENAI_EVALUATION_MODEL,
                messages=[
                    {'role': 'system', 'content': 'You are an interviewer. Generate a concise follow-up question.'},
                    {'role': 'user', 'content': f'Previous exchange: {previous_message}\n\nGenerate one brief follow-up question.'}
                ],
                max_tokens=80,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate followup: {str(e)}")
            return "Interesting. Can you elaborate on that?"
