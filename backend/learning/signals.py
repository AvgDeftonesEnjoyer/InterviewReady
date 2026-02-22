from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date
from learning.models import UserProgress
from gamification.models import DailyChallenge, UserDailyChallenge
from gamification.services import XPService

@receiver(post_save, sender=UserProgress)
def check_daily_challenges(sender, instance, created, **kwargs):
    if not created:
        return
        
    user = instance.user
    today = date.today()
    
    # Evaluate all challenges for today
    today_challenges = DailyChallenge.objects.filter(date=today)
    
    for daily in today_challenges:
        template = daily.template
        if not template:
            continue
            
        user_challenge, _ = UserDailyChallenge.objects.get_or_create(
            user=user,
            challenge=daily
        )
        
        if user_challenge.is_completed:
            continue
            
        # Specific counters based on challenge type
        if template.challenge_type == 'answer_questions':
            count = UserProgress.objects.filter(
                user=user,
                answered_at__date=today
            ).count()
            
        elif template.challenge_type == 'answer_hard':
            count = UserProgress.objects.filter(
                user=user,
                answered_at__date=today,
                question__difficulty='hard'
            ).count()
            
        elif template.challenge_type == 'perfect_score':
            # Count only correct answers
            count = UserProgress.objects.filter(
                user=user,
                answered_at__date=today,
                is_correct=True
            ).count()
            
        elif template.challenge_type == 'streak_protect':
            # Need at least 1 overall activity
            count = UserProgress.objects.filter(user=user, answered_at__date=today).count()
            
        elif template.challenge_type == 'complete_topic':
            # For this, just use generic count increment for the specific topic or evaluate it differently depending on custom logic.
            # Here we default to simple completed questions for the topic
            target_topic = template.language or "general"
            count = UserProgress.objects.filter(user=user, answered_at__date=today, question__topic=target_topic).count()
            
        else:
            count = user_challenge.completed_count
        
        user_challenge.completed_count = count
        
        # Check completion
        if count >= template.goal_count:
            user_challenge.is_completed = True
            user_challenge.completed_at = timezone.now()
            
            # Award XP if not already awarded
            if not user_challenge.xp_awarded:
                XPService.add_xp(user, template.bonus_xp)
                user_challenge.xp_awarded = True
        
        user_challenge.save()
