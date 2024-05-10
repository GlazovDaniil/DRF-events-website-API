from django.urls import path
from .views import (ProfileAPIView, ProfileCreateAPIView, ProfileDetail, ProfileUpdate,CreateUserView, UserInfoByToken,
                    UserAddMeetingAPIView, UserRemoveMeetingAPIView, RecommendedMeetingsForTags)

urlpatterns = [
    path('user/recommended_meetings/', RecommendedMeetingsForTags.as_view()),
    # path('user/<str:pk>/remove_chat/', ProfileChatRemoveAPIView.as_view()),
    # path('user/<str:pk>/add_chat/', ProfileChatAddAPIView.as_view()),
    path('user/<str:pk>/remove_meeting/', UserRemoveMeetingAPIView.as_view()),
    path('user/<str:pk>/add_meeting/', UserAddMeetingAPIView.as_view()),
    path('user/by_token/', UserInfoByToken.as_view()),  # user_by_token/
    path('user/register/', CreateUserView.as_view()),
    path('user/create/', ProfileCreateAPIView.as_view()),
    path('user/<str:pk>/update/', ProfileUpdate.as_view()),
    path('user/<str:pk>/', ProfileDetail.as_view()),
    path('user/', ProfileAPIView.as_view()),
]
