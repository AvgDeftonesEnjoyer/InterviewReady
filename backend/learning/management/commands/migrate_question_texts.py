from django.core.management.base import BaseCommand
from learning.models import Question, AnswerOption

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for q in Question.objects.all():
            if not q.text_en and hasattr(q, 'text'):
                q.text_en = q.text
                q.explanation_en = q.explanation or ''
                q.save()

        for opt in AnswerOption.objects.all():
            if not opt.text_en and hasattr(opt, 'text'):
                opt.text_en = opt.text
                opt.save()

        self.stdout.write('✅ Migration complete!')
