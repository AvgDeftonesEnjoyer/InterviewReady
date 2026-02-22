from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # App URLs will be added here as we implement them
    path('api/home/', include('home.urls')),
    path('auth/', include('users.urls')),
    path('learning/', include('learning.urls')),
    path('interviews/', include('interviews.urls')),
    path('ai/', include('ai.urls')),
    path('progress/', include('progress.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('webhooks/', include('payments.urls')),
]
