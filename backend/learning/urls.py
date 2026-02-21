from django.urls import path
from .views import DailyQuestionsView, QuestionListView, SubmitAnswerView

urlpatterns = [
    path('', QuestionListView.as_view(), name='question_list'),
    path('daily/', DailyQuestionsView.as_view(), name='daily_questions'),
    path('submit/', SubmitAnswerView.as_view(), name='submit_answer'),
]
