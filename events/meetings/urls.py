from django.urls import path
from .views import MeetingAPIView, ProfileAPIView

urlpatterns = [
    path('meeting/', MeetingAPIView.as_view()),
    path('users/', ProfileAPIView.as_view()),
]