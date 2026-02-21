from django.utils import timezone
from .models import InterviewSession, InterviewMessage
from learning.models import Question
from ai.services import AIService, AIUsageService
from users.models import User
import random

class InterviewService:
    @staticmethod
    def start_session(user: User, interview_type: str) -> InterviewSession:
        if interview_type == 'AI':
            if not AIUsageService.can_use_ai(user):
                raise ValueError("AI usage limit reached for today.")
                
        session = InterviewSession.objects.create(
            user=user,
            type=interview_type
        )

        initial_msg = ""
        if interview_type == 'SCRIPTED':
            question = Question.objects.filter(is_active=True).order_by('?').first()
            initial_msg = question.text if question else "Can you describe your experience?"
        else: # AI
            initial_msg = AIService.generate_hr_question()
            AIUsageService.increment_usage(user)

        InterviewMessage.objects.create(
            session=session,
            role='BOT',
            text=initial_msg
        )
        return session

    @staticmethod
    def process_answer(session: InterviewSession, user_message: str) -> InterviewMessage:
        if session.status != 'ACTIVE':
            raise ValueError("Cannot send messages to a finished session.")

        if session.type == 'AI':
            if not AIUsageService.can_use_ai(session.user):
                raise ValueError("AI usage limit reached for today.")

        InterviewMessage.objects.create(
            session=session,
            role='USER',
            text=user_message
        )

        bot_reply = ""
        if session.type == 'SCRIPTED':
            next_question = Question.objects.filter(is_active=True).order_by('?').first()
            bot_reply = next_question.text if next_question else "Thank you for the answer."
        else:
            # We pass the last BOT question here, for contextual mock
            last_bot_msg = session.messages.filter(role='BOT').last()
            prev_bot_text = last_bot_msg.text if last_bot_msg else "Question"
            evaluation = AIService.evaluate_answer(prev_bot_text, user_message)
            followup = AIService.generate_followup(evaluation)
            bot_reply = f"{evaluation}\n\n{followup}"
            AIUsageService.increment_usage(session.user)

        bot_message = InterviewMessage.objects.create(
            session=session,
            role='BOT',
            text=bot_reply
        )
        return bot_message

    @staticmethod
    def finish_session(session: InterviewSession) -> InterviewSession:
        if session.status == 'FINISHED':
            return session
            
        session.status = 'FINISHED'
        session.finished_at = timezone.now()
        # Mock score calculation based on random or messages length
        session.score = random.randint(60, 100)
        session.save()
        return session
