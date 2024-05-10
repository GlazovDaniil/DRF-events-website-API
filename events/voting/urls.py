from django.urls import path
from views import (VotingAPIView, FieldCreateAPIView, FieldAddVoteAPIView, FieldRemoveVoteAPIView, FieldDestroyAPIView,
                   FieldRetrieveAPIView, FieldRenameAPIView, VotingRenameAPIView, VotingDestroyAPIView,
                   VotingCreateAPIView)


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
]