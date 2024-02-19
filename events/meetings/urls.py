from django.urls import path
from .views import (MeetingAPIView, ProfileAPIView, MeetingDetail, ProfileDetail, MeetingCreateAPIView,
                    MeetingProfileListAPIView, TimetableCreate, CreateUserView, ProfileCreateAPIView, TimetableUpdate,
                    UserInfoByToken, UserAddMeetingAPIView, UserRemoveMeetingAPIView, TagsAPIView, PlaceAPIView,
                    ChatAPIView, ChatCreateAPIView, MessageCreateAPIView, ChatMessageAPIView, MessagesAPIView,
                    ProfileChatAddAPIView, ProfileChatRemoveAPIView)

urlpatterns = [
    path('messages/', MessagesAPIView.as_view()),
    path('chat/<int:pk>/create_message/', MessageCreateAPIView.as_view()),
    path('chat/<int:pk>/', ChatMessageAPIView.as_view()),
    path('chat_create/', ChatCreateAPIView.as_view()),
    path('chat_list/', ChatAPIView.as_view()),

    path('places_list/', PlaceAPIView.as_view()),

    path('tags_list/', TagsAPIView.as_view()),

    path('user_remove_chat/<int:pk>/', ProfileChatRemoveAPIView.as_view()),
    path('user_add_chat/<int:pk>/', ProfileChatAddAPIView.as_view()),
    path('user_remove_meeting/<int:pk>/', UserRemoveMeetingAPIView.as_view()),
    path('user_add_meeting/<int:pk>/', UserAddMeetingAPIView.as_view()),
    path('user_by_token/', UserInfoByToken.as_view()),  # user_by_token/
    path('user_register/', CreateUserView.as_view()),
    path('user_create/', ProfileCreateAPIView.as_view()),
    path('users/<int:pk>/', ProfileDetail.as_view()),
    path('users/', ProfileAPIView.as_view()),

    path('timetable_update/<int:pk>/', TimetableUpdate.as_view()),
    path('timetable_create/', TimetableCreate.as_view()),

    path('meeting/prifils/<int:pk>/', MeetingProfileListAPIView.as_view()),
    path('meeting/<int:pk>/', MeetingDetail.as_view()),
    path('meeting_create/', MeetingCreateAPIView.as_view()),
    path('meeting/', MeetingAPIView.as_view()),
]
