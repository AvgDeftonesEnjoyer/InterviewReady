from .models import Question, AnswerOption, UserAnswer
from gamification.services import XPService
from users.models import User

class LearningService:
    @staticmethod
    def get_daily_questions(user: User):
        # Simplistic implementation: return 10 random active questions 
        # ideally we'd exclude questions user already answered correctly recently
        answered_q_ids = UserAnswer.objects.filter(user=user, is_correct=True).values_list('question_id', flat=True)
        return Question.objects.filter(is_active=True).exclude(id__in=answered_q_ids).order_by('?')[:10]

    @staticmethod
    def submit_answer(user: User, question_id: int, option_id: int):
        question = Question.objects.get(id=question_id)
        option = AnswerOption.objects.get(id=option_id, question=question)
        
        is_correct = option.is_correct
        
        user_answer = UserAnswer.objects.create(
            user=user,
            question=question,
            selected_option=option,
            is_correct=is_correct
        )

        # Gamification logic
        xp_earned = 0
        if is_correct:
            xp_earned = 10
            XPService.add_xp(user, xp_earned)

        return {
            "is_correct": is_correct,
            "explanation": question.explanation,
            "xp_earned": xp_earned
        }
