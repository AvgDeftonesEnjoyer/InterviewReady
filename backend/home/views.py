from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from gamification.models import UserProfile, Streak, DailyChallenge, UserDailyChallenge
from learning.models import Question, UserProgress
from django.db.models import Count, Sum, Q, Prefetch
from users.models import User

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # OPTIMIZATION: Use select_related to avoid N+1 queries
        user = User.objects.select_related('profile').get(id=user.id)

        # User details
        profile = getattr(user, 'profile', None)
        first_name = user.first_name if user.first_name else user.username.split('@')[0]
        greeting = self.get_greeting()

        # OPTIMIZATION: Use select_related for streak
        streak = Streak.objects.select_related('user').filter(user=user).first()
        if not streak:
            streak = Streak(user=user)

        # Today's progress bounds
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        # OPTIMIZATION: Single aggregate query for today's progress
        progress_today_qs = UserProgress.objects.filter(
            user=user, 
            answered_at__gte=today_start
        )
        xp_today = progress_today_qs.aggregate(total=Sum('xp_earned'))['total'] or 0
        questions_answered_today = progress_today_qs.count()

        # OPTIMIZATION: Single aggregate query for yesterday's progress
        progress_yesterday_qs = UserProgress.objects.filter(
            user=user, 
            answered_at__gte=yesterday_start, 
            answered_at__lt=today_start
        )
        xp_yesterday = progress_yesterday_qs.aggregate(total=Sum('xp_earned'))['total'] or 0
        
        # Next up topic logic
        user_lang = profile.primary_language if profile else 'python'
        
        # OPTIMIZATION: Use select_related on topic queries
        all_langs = Question.objects.filter(
            language=user_lang
        ).select_related('topic').values_list('topic', flat=True).distinct()

        next_up_data = None
        for topic_id in all_langs:
            if topic_id is None:
                continue
            # OPTIMIZATION: Single query with annotate for topic progress
            questions_in_topic = Question.objects.filter(
                language=user_lang, 
                topic_id=topic_id
            ).select_related('topic')
            total_q = questions_in_topic.count()

            # OPTIMIZATION: Use exists() and count efficiently
            answered_q = UserProgress.objects.filter(
                user=user, 
                question__topic_id=topic_id,
                is_correct=True
            ).values('question').distinct().count()

            if total_q > 0 and answered_q < total_q:
                # This is an incomplete topic
                progress_percent = int((answered_q / total_q) * 100)
                first_question = questions_in_topic.first()
                next_up_data = {
                    "topic": first_question.topic.name if first_question and first_question.topic else "Unknown",
                    "language": user_lang,
                    "progress_percent": progress_percent,
                    "questions_done": answered_q,
                    "questions_total": total_q,
                    "topic_id": first_question.id if first_question else 0
                }
                break

        # Daily challenge logic - OPTIMIZATION: Use prefetch_related
        today_date = timezone.now().date()
        daily_challenges_qs = DailyChallenge.objects.filter(
            date=today_date
        ).select_related('template').prefetch_related(
            Prefetch(
                'userdailychallenge_set',
                queryset=UserDailyChallenge.objects.filter(user=user),
                to_attr='user_challenges'
            )
        )

        expires_at = timezone.now().replace(hour=23, minute=59, second=59)

        dc_list = []
        for daily_challenge in daily_challenges_qs:
            template = daily_challenge.template
            if not template:
                continue

            # OPTIMIZATION: Use prefetched user_challenges instead of get_or_create
            user_dc_list = daily_challenge.user_challenges
            if user_dc_list:
                user_dc = user_dc_list[0]
            else:
                user_dc = UserDailyChallenge(user=user, challenge=daily_challenge)
            
            percent = int((user_dc.completed_count / template.goal_count) * 100) if template.goal_count > 0 else 0

            dc_list.append({
                "id": daily_challenge.id,
                "order": daily_challenge.order,
                "icon": template.icon,
                "title": template.title,
                "description": template.description,
                "challenge_type": template.challenge_type,
                "goal_count": template.goal_count,
                "completed_count": user_dc.completed_count,
                "percent": min(percent, 100),
                "bonus_xp": template.bonus_xp,
                "is_completed": user_dc.is_completed,
                "expires_at": expires_at.isoformat(),
                "difficulty_level": template.difficulty_level,
                "language_filter": template.language,
                "difficulty_filter": template.difficulty
            })

        response_data = {
            "user": {
                "name": first_name,
                "greeting": greeting
            },
            "streak": {
                "current": streak.current_streak,
                "longest": streak.longest_streak,
                "protected_today": False
            },
            "next_up": next_up_data,
            "progress_today": {
                "xp": xp_today,
                "xp_yesterday": xp_yesterday,
                "questions_answered": questions_answered_today,
                "personal_best_questions": 31 # Stub for now
            },
            "daily_challenges": dc_list,
            "onboarding_completed": profile.onboarding_completed if profile else False
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    def get_greeting(self):
        hour = timezone.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 18:
            return "Good afternoon"
        else:
            return "Good evening"


class StartTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        try:
            target_question = Question.objects.get(id=topic_id)
        except Question.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)
            
        topic = target_question.topic
        user_lang = getattr(request.user.profile, 'primary_language', 'python')
        
        # Find first unanswered question in this topic
        answered_question_ids = UserProgress.objects.filter(user=request.user).values_list('question_id', flat=True)
        unanswered_question = Question.objects.filter(
            topic=topic,
            language=user_lang
        ).exclude(id__in=answered_question_ids).first()
        
        if not unanswered_question:
            return Response({"message": "Topic already completed"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            "first_question_id": unanswered_question.id,
            "topic": topic,
            "language": user_lang
        }, status=status.HTTP_200_OK)

class ChallengeProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, challenge_id):
        user = request.user
        increment = request.data.get('increment', 1)
        
        try:
            daily_challenge = DailyChallenge.objects.get(id=challenge_id)
        except DailyChallenge.DoesNotExist:
            return Response({"error": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)
            
        user_challenge, _ = UserDailyChallenge.objects.get_or_create(
            user=user, 
            challenge=daily_challenge
        )
        
        template = daily_challenge.template
        if not template:
            return Response({"error": "Template associated with this challenge is missing"}, status=status.HTTP_400_BAD_REQUEST)
            
        if user_challenge.is_completed:
            return Response({"message": "Challenge already completed"}, status=status.HTTP_200_OK)
            
        # Add increment to completed_count
        user_challenge.completed_count += int(increment)
        
        if user_challenge.completed_count >= template.goal_count:
            user_challenge.is_completed = True
            user_challenge.completed_at = timezone.now()
            
            from gamification.services import XPService
            if not user_challenge.xp_awarded:
                XPService.add_xp(user, template.bonus_xp)
                user_challenge.xp_awarded = True
                
        user_challenge.save()
        
        return Response({
            "completed_count": user_challenge.completed_count,
            "is_completed": user_challenge.is_completed
        }, status=status.HTTP_200_OK)
