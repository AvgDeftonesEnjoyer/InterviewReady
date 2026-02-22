from django.urls import path
from .views import DashboardView, StartTopicView, ChallengeProgressView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('start-topic/<int:topic_id>/', StartTopicView.as_view(), name='start_topic'),
    path('challenges/<int:challenge_id>/progress/', ChallengeProgressView.as_view(), name='challenge_progress'),
]
