from django.http import HttpResponseRedirect

from .models import Profile, Meeting
from .serializers import MeetingSerializer, ProfileSerializer
from .permissions import IsAuthorOrReadonlyMeeting, IsAuthorOrReadonlyProfile
from rest_framework import generics, permissions
from django.contrib.auth import logout


class MeetingAPIView(generics.ListCreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorOrReadonlyMeeting,)
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class ProfileAPIView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorOrReadonlyProfile,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/api-authlogin/')

def accounts_profile_redirect(request):
    return HttpResponseRedirect('/meeting-api/v1/users/')
