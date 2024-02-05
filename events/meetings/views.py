from django.http import HttpResponseRedirect, HttpResponseNotFound

from .models import Profile, Meeting
from .serializers import MeetingSerializer, ProfileSerializer, MeetingCreateSerializer
from .permissions import IsAuthorOrReadonlyMeeting, IsAuthorOrReadonlyProfile
from rest_framework import generics, permissions
from django.contrib.auth import logout
from calendar import calendar
from .pagination import StandardResultsSerPagination, LargeResultsSerPagination


'''
def meeting_view(request, id):
    try:
        if request.method == "POST":
            meeting = Meeting.objects.get(id=id)
            meeting.delete()
    except Meeting.DoesNotExist:
        return HttpResponseNotFound("<h2>Автор не найден</h2>")
'''

class MeetingAPIView(generics.ListAPIView):
    #список по всем мероприятиям
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = StandardResultsSerPagination

class MeetingCreateAPIView(generics.CreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingCreateSerializer
    def post(self, request, *args, **kwargs):
        place = request.POST.get("place")
        event_date = request.POST.get("event_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        print(place, event_date, start_time, end_time)
        #calendar(place, event_date, start_time, end_time)
        return self.create(request, *args, **kwargs)

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
