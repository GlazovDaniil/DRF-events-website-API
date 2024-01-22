from .models import Profile, Meeting
from .serializers import MeetingSerializer, ProfileSerializer
from django.contrib.auth.models import User
from rest_framework import generics


class MeetingAPIView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class ProfileAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
