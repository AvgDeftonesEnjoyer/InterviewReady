from django.urls import path
from .views import ProgressStatsView

urlpatterns = [
    path('stats/', ProgressStatsView.as_view(), name='progress_stats'),
]
