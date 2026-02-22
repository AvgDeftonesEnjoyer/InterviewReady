import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gamification.models import ChallengeTemplate

def create_templates():
    ChallengeTemplate.objects.get_or_create(
        title="Python Practice",
        description="Answer 5 Python questions",
        challenge_type="answer_questions",
        language="python",
        goal_count=5,
        bonus_xp=150,
        icon="🐍"
    )
    ChallengeTemplate.objects.get_or_create(
        title="Hard Mode",
        description="Answer 2 hard questions",
        challenge_type="answer_hard",
        goal_count=2,
        bonus_xp=300,
        icon="🔥"
    )
    ChallengeTemplate.objects.get_or_create(
        title="Perfect Score",
        description="Get a perfect score today",
        challenge_type="perfect_score",
        goal_count=5,
        bonus_xp=250,
        icon="🎯"
    )
    print("Templates created successfully!")

if __name__ == "__main__":
    create_templates()
