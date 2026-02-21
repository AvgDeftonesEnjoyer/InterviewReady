from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from gamification.services import XPService

class ProgressStatsView(APIView):
    def get(self, request, *args, **kwargs):
        profile = XPService.get_or_create_profile(request.user)
        data = {
            "target_role": profile.target_role,
            "experience_level": profile.experience_level,
            "readiness_score": profile.readiness_score,
            "total_xp": profile.total_xp,
            "current_level": profile.current_level,
            "streak_days": profile.streak_days,
            "last_activity_date": profile.last_activity_date,
        }
        return Response(data, status=status.HTTP_200_OK)
