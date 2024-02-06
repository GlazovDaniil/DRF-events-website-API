import datetime

from django.http import HttpResponseRedirect, HttpResponseNotFound

from .models import Profile, Meeting, Timetable, Place
from .serializers import MeetingSerializer, ProfileSerializer, MeetingCreateSerializer
from .permissions import IsAuthorOrReadonlyMeeting, IsAuthorOrReadonlyProfile
from rest_framework import generics, permissions
from django.contrib.auth import logout
from rest_framework import status
from .pagination import StandardResultsSerPagination, LargeResultsSerPagination
from .castom_exeptions import MyCustomExcpetion

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
    # список по всем мероприятиям
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = StandardResultsSerPagination


class MeetingCreateAPIView(generics.CreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingCreateSerializer

    def post(self, request, *args, **kwargs):
        place = int(request.POST.get("place"))
        event_date = request.POST.get("event_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        timetables = Timetable.objects.filter(place=place, event_date=event_date)

        s_t = start_time.split(':')
        e_t = end_time.split(':')

        start = datetime.time(int(s_t[0]), int(s_t[1]))
        end = datetime.time(int(e_t[0]), int(e_t[1]))
        marker = False
        counter = 0
        for timetable in timetables:
            counter += 1
            if not ((timetable.start_time <= start <= timetable.end_time)
                    or (timetable.start_time <= end <= timetable.end_time)
                    or (start <= timetable.start_time and end >= timetable.end_time)):
                marker = True
                break
        if marker or counter == 0:
            time_place = Place.objects.get(id=place)
            timetable = Timetable()
            timetable.place = time_place
            timetable.event_date = event_date
            timetable.start_time = start_time
            timetable.end_time = end_time
            timetable.save()
            return self.create(request, *args, **kwargs)
        else:
            raise MyCustomExcpetion(detail={"Error": "Невозможно записать на эту дату и время, так как они заняты"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


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
