import logging
import random
from datetime import date
from django.core.management.base import BaseCommand
from gamification.models import ChallengeTemplate, DailyChallenge

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates randomized daily challenges for the platform'

    def handle(self, *args, **options):
        today = date.today()
        
        # Check if already generated today
        if DailyChallenge.objects.filter(date=today).exists():
            self.stdout.write(self.style.WARNING(f"Challenges already generated for {today}"))
            return

        templates = list(ChallengeTemplate.objects.filter(is_active=True))

        if len(templates) < 2:
            warning_msg = "Not enough active ChallengeTemplates! Please add more in the admin panel."
            logger.warning(warning_msg)
            self.stdout.write(self.style.ERROR(warning_msg))
            return
            
        count = random.randint(2, 3)
        selected = random.sample(templates, min(count, len(templates)))

        created_count = 0
        for i, template in enumerate(selected, start=1):
            DailyChallenge.objects.create(
                template=template,
                date=today,
                order=i
            )
            created_count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {created_count} challenges for {today}"))
