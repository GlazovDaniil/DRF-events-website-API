from django.urls import path
from .views import (MeetingAPIView, ProfileAPIView, MeetingDetail, ProfileDetail, MeetingCreateAPIView,
                    MeetingProfileListAPIView, TimetableCreate)

urlpatterns = [
    path('timetable_create/', TimetableCreate.as_view()),
    path('meeting/prifils/<int:pk>/', MeetingProfileListAPIView.as_view()),
    path('meeting/<int:pk>/', MeetingDetail.as_view()),
    path('meeting_create/', MeetingCreateAPIView.as_view()),
    path('meeting/', MeetingAPIView.as_view()),
    path('users/<int:pk>/', ProfileDetail.as_view()),
    path('users/', ProfileAPIView.as_view()),
]