from django.urls import path
from .views import MeetingAPIView, ProfileAPIView, MeetingDetail, ProfileDetail

urlpatterns = [
    path('meeting/<int:pk>/', MeetingDetail.as_view()),
    path('meeting/', MeetingAPIView.as_view()),
    path('users/<int:pk>/', ProfileDetail.as_view()),
    path('users/', ProfileAPIView.as_view()),
]