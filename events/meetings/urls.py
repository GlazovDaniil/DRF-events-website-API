from django.urls import path
# from django.conf.urls import (handler400, handler403, handler404, handler500)
from .views import (MeetingAPIView, ProfileAPIView, MeetingDetail, ProfileDetail, MeetingCreateAPIView,
                    MeetingProfileListAPIView, TimetableCreate, CreateUserView, ProfileCreateAPIView, TimetableUpdate,
                    UserInfoByToken, UserAddMeetingAPIView, UserRemoveMeetingAPIView, TagsAPIView, PlaceAPIView,
                    ChatAPIView, ChatCreateAPIView, MessageCreateAPIView, ChatMessageAPIView, MessagesAPIView,
                    ProfileChatAddAPIView, ProfileChatRemoveAPIView, MeetingChatAddAPIView, VotingAPIView,
                    VotingCreateAPIView, VotingDestroyAPIView, FieldCreateAPIView, FieldAddVoteAPIView,
                    FieldRemoveVoteAPIView, FieldDestroyAPIView, FieldRetrieveAPIView, RecommendedMeetingsForTags,
                    error404, TimetableListAPIView, ProfileUpdate, FieldRenameAPIView, VotingRenameAPIView,
                    MeetingKickUser)

# handler404 = error404

urlpatterns = [

    path('meeting/<str:pk>/voting/create/', VotingCreateAPIView.as_view()),
    path('meeting/voting/<str:pk>/delete/', VotingDestroyAPIView.as_view()),
    path('field/<str:pk>/rename/', FieldRenameAPIView.as_view()),  # new
    path('field/<str:pk>/remove_vote/', FieldRemoveVoteAPIView.as_view()),
    path('field/<str:pk>/add_vote/', FieldAddVoteAPIView.as_view()),
    path('field/<str:pk>/', FieldRetrieveAPIView.as_view()),
    path('voting/<str:pk>/add_field/', FieldCreateAPIView.as_view()),
    path('voting/<str:pk>/rename/', VotingRenameAPIView.as_view()),  # new
    path('voting/destroy_field/<str:pk>/', FieldDestroyAPIView.as_view()),
    path('votings/', VotingAPIView.as_view()),

    path('messages/', MessagesAPIView.as_view()),
    path('chat/<int:pk>/create_message/', MessageCreateAPIView.as_view()),
    path('chat/<int:pk>/', ChatMessageAPIView.as_view()),
    path('chat_create/', ChatCreateAPIView.as_view()),
    path('chat_list/', ChatAPIView.as_view()),

    path('places_list/', PlaceAPIView.as_view()),

    path('tags_list/', TagsAPIView.as_view()),

    path('user/recommended_meetings/', RecommendedMeetingsForTags.as_view()),
    path('user/<str:pk>/remove_chat/', ProfileChatRemoveAPIView.as_view()),
    path('user/<str:pk>/add_chat/', ProfileChatAddAPIView.as_view()),
    path('user/<str:pk>/remove_meeting/', UserRemoveMeetingAPIView.as_view()),
    path('user/<str:pk>/add_meeting/', UserAddMeetingAPIView.as_view()),
    path('user_by_token/', UserInfoByToken.as_view()),  # user_by_token/
    path('user_register/', CreateUserView.as_view()),
    path('user_create/', ProfileCreateAPIView.as_view()),
    path('users/<str:pk>/update/', ProfileUpdate.as_view()),
    path('users/<str:pk>/', ProfileDetail.as_view()),
    path('users/', ProfileAPIView.as_view()),

    path('timetable_list/', TimetableListAPIView.as_view()),
    path('timetable_update/<int:pk>/', TimetableUpdate.as_view()),
    path('timetable_create/', TimetableCreate.as_view()),

    path('meeting/<str:meeting_id>/kick_user/<str:pk>/', MeetingKickUser.as_view()),  # new
    path('meeting/<str:pk>/add_chat/', MeetingChatAddAPIView.as_view()),
    # path('meeting/<str:pk>/delete_user/<str:user>',),
    path('meeting/prifils/<str:pk>/', MeetingProfileListAPIView.as_view()),
    path('meeting/<str:pk>/', MeetingDetail.as_view()),
    path('meeting_create/', MeetingCreateAPIView.as_view()),
    path('meeting/', MeetingAPIView.as_view()),
]
