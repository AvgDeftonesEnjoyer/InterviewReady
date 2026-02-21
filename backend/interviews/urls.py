from django.urls import path
from .views import StartInterviewView, InterviewMessageView, FinishInterviewView

urlpatterns = [
    path('start/', StartInterviewView.as_view(), name='start_interview'),
    path('message/', InterviewMessageView.as_view(), name='interview_message'),
    path('finish/', FinishInterviewView.as_view(), name='finish_interview'),
]
