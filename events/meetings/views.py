import datetime
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .models import Profile, Meeting, Timetable, Place
from .serializers import (MeetingSerializer, ProfileSerializer, MeetingCreateSerializer, MeetingProfileListSerializer,
                          TimetableSerializer)
from .permissions import IsAuthorOrReadonlyMeeting, IsAuthorOrReadonlyProfile
from rest_framework import generics, permissions
from django.contrib.auth import logout
from .pagination import StandardResultsSerPagination, MeetingProfilesPagination, MeetingsPagination
from .castom_exeptions import MyCustomExcpetion
from rest_framework import status
from rest_framework.permissions import AllowAny


class MeetingProfileListAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meeting.objects.all()
    pagination_class = MeetingProfilesPagination
    serializer_class = MeetingProfileListSerializer
    permission_classes = (AllowAny,)


class MeetingAPIView(generics.ListAPIView):
    # список по всем мероприятиям
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = MeetingsPagination
    permission_classes = (AllowAny,)


class MeetingCreateAPIView(generics.CreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingCreateSerializer

    def post(self, request, *args, **kwargs):
        if request.POST.get("seats") == '':
            id_timetable = request.POST.get("timetable")
            timetable = Timetable.objects.get(id=id_timetable).place

            id_place = Place.objects.get(office=timetable).id

            places = Place.objects.get(id=id_place)
            max_participant = places.max_participant
            request.data._mutable = True
            request.data['seats'] = max_participant
            request.data._mutable = False

        # добавить автовписывание автора поста (авторизованный пользователь)
        request.data._mutable = True
        request.data['author'] = request.user.id
        request.data._mutable = False

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


class TimetableCreate(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

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
            return self.create(request, *args, **kwargs)
        else:
            raise MyCustomExcpetion(detail={"Error": "Невозможно записать на эту дату и время, так как они заняты"},
                                    status_code=status.HTTP_400_BAD_REQUEST)




def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/api-authlogin/')


def accounts_profile_redirect(request):
    return HttpResponseRedirect('/meeting-api/v1/users/')
