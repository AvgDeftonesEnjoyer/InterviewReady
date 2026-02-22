from django.core.management.base import BaseCommand
from learning.models import Topic, Question, AnswerOption

class Command(BaseCommand):
    help = 'Fixes the localized text fields that were incorrectly assigned to text_en instead of text_uk'

    def handle(self, *args, **kwargs):
        topics_fixed = 0
        questions_fixed = 0
        options_fixed = 0

        for t in Topic.objects.all():
            # If the original name looks Ukrainian/Cyrillic, we should move it
            # Actually, since all original content was Ukrainian, just move it to _uk
            # But ONLY if _uk is empty and _en equals the original text
            if t.name_en == t.name and not t.name_uk:
                t.name_uk = t.name
                t.name_en = ''  # Clear English so it falls back to empty or needs translation
                t.save()
                topics_fixed += 1

        for q in Question.objects.all():
            if q.text_en == q.text and not q.text_uk:
                q.text_uk = q.text
                q.text_en = ''
                
                if q.explanation_en == (q.explanation or ''):
                    q.explanation_uk = q.explanation or ''
                    q.explanation_en = ''
                q.save()
                questions_fixed += 1

        for opt in AnswerOption.objects.all():
            if opt.text_en == opt.text and not opt.text_uk:
                opt.text_uk = opt.text
                opt.text_en = ''
                opt.save()
                options_fixed += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Migration fix complete! Fixed {topics_fixed} topics, {questions_fixed} questions, {options_fixed} options.'))
