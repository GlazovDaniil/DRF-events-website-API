from django.urls import path
from .views import MeetingAPIView, AllUserAPIView

urlpatterns=[
    path('meeting/', MeetingAPIView.as_view()),
    path('users/', AllUserAPIView.as_view()),
]