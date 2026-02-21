from django.utils import timezone
from subscriptions.services import SubscriptionService
from users.models import User
from .models import AIUsage

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
    """Mock integration for AI"""
    @staticmethod
    def generate_hr_question() -> str:
        return "Can you tell me about a time you overcame a technical challenge?"

    @staticmethod
    def evaluate_answer(question: str, user_answer: str) -> str:
        # Mock evaluation
        return f"Your answer to '{question}' was good, but could be improved by adding more specific metrics."

    @staticmethod
    def generate_followup(previous_message: str) -> str:
        return "Interesting. How did that impact the team's overall delivery?"
