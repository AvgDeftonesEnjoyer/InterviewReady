from django.urls import path
from .views import (
    DailyQuestionsView, QuestionListView,
    TopicListView, TopicQuestionsView, AnswerQuestionView, SessionSummaryView
)

urlpatterns = [
    path('', QuestionListView.as_view(), name='question_list'),  # DEPRECATED: Not used
    path('daily/', DailyQuestionsView.as_view(), name='daily_questions'),  # DEPRECATED: Old daily questions
    path('topics/', TopicListView.as_view(), name='topic_list'),
    path('topics/<int:topic_id>/questions/', TopicQuestionsView.as_view(), name='topic_questions'),
    path('answer/', AnswerQuestionView.as_view(), name='answer_question'),  # ✅ CURRENT
    path('session/summary/', SessionSummaryView.as_view(), name='session_summary'),
]
