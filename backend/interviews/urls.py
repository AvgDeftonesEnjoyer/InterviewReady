from django.urls import path
from .views import (
    QuotaView,
    StartInterviewView,
    SendMessageView,
    HistoryView,
    TranscribeView,
)

urlpatterns = [
    path('quota/', QuotaView.as_view(), name='interview_quota'),
    path('start/', StartInterviewView.as_view(), name='interview_start'),
    path('<int:session_id>/message/', SendMessageView.as_view(), name='interview_message'),
    path('<int:session_id>/history/', HistoryView.as_view(), name='interview_history'),
    path('transcribe/', TranscribeView.as_view(), name='interview_transcribe'),
]
