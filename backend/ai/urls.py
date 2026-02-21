from django.urls import path
from .views import EvaluateView

urlpatterns = [
    path('evaluate/', EvaluateView.as_view(), name='ai_evaluate'),
]
