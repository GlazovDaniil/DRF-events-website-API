from django.urls import path
from .views import (MeetingAPIView, ProfileAPIView, MeetingDetail, ProfileDetail, MeetingCreateAPIView,
                    MeetingProfileListAPIView, TimetableCreate, CreateUserView, ProfileCreateAPIView, TimetableUpdate,
                    UserInfoByToken, UserAddMeetingAPIView, UserRemoveMeetingAPIView)

urlpatterns = [
    path('user_remove_meeting/<int:pk>/', UserRemoveMeetingAPIView.as_view()),
    path('user_add_meeting/<int:pk>/', UserAddMeetingAPIView.as_view()),
    path('user_by_token/', UserInfoByToken.as_view()),  # user_by_token/
    path('user_register/', CreateUserView.as_view()),
    path('user_create/', ProfileCreateAPIView.as_view()),
    path('timetable_update/<int:pk>/', TimetableUpdate.as_view()),
    path('timetable_create/', TimetableCreate.as_view()),
    path('meeting/prifils/<int:pk>/', MeetingProfileListAPIView.as_view()),
    path('meeting/<int:pk>/', MeetingDetail.as_view()),
    path('meeting_create/', MeetingCreateAPIView.as_view()),
    path('meeting/', MeetingAPIView.as_view()),
    path('users/<int:pk>/', ProfileDetail.as_view()),
    path('users/', ProfileAPIView.as_view()),
]
