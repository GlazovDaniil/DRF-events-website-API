import datetime
from django.http import HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema
from .models import Profile, Meeting, Timetable, Place, Tags
from .serializers import (MeetingSerializer, ProfileSerializer, MeetingCreateSerializer, MeetingProfileListSerializer,
                          TimetableSerializer, UserSerializer, ProfileCreateSerializer, UserAddMeetingSerializer,
                          TagsSerializer, PlaceSerializer)
from .permissions import IsAuthorOrReadonlyMeeting, IsAuthorOrReadonlyProfile
from rest_framework import generics, views, response
from django.contrib.auth import logout
from .pagination import MeetingProfilesPagination, MeetingsPagination
from .castom_exeptions import MyCustomException
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from calendar import calendar
import json


class MeetingProfileListAPIView(generics.RetrieveAPIView):
    # список участников мероприятия (нужен id мероприятия)
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
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            if request.POST.get("seats") == '' or int(request.POST.get("seats")) < 0:
                id_timetable = request.POST.get("timetable")
                timetable = Timetable.objects.get(id=id_timetable).place

                id_place = Place.objects.get(office=timetable).id

                places = Place.objects.get(id=id_place)
                max_participant = places.max_participant
                request.data._mutable = True
                request.data['seats'] = max_participant
                request.data._mutable = False

            # автовписывание автора поста (авторизованный пользователь)
            request.data._mutable = True
            request.data['author'] = request.user.id
            request.data._mutable = False

            return self.create(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"Error": "Введены некорректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    # изменение мероприятия или просто его просмотр (если не автор)
    permission_classes = (IsAuthorOrReadonlyMeeting,)
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer


class ProfileAPIView(generics.ListAPIView):
    # список профилей
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)


class ProfileCreateAPIView(generics.CreateAPIView):
    # создание доп информации профиля
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # автовписывание пользователя (авторизованный пользователь)
        request.data._mutable = True
        request.data['user'] = request.user.id
        request.data._mutable = False
        return self.create(request, *args, **kwargs)


class ProfileDetail(generics.RetrieveUpdateAPIView):
    # изменение доп информации о пользователе
    permission_classes = (IsAuthorOrReadonlyProfile,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class TimetableCreate(generics.CreateAPIView):
    # запись мероприятия в расписание
    permission_classes = (IsAuthenticated,)
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
        if start < end:
            marker = False
            counter = 0
            for timetable in timetables:
                print(timetable)
                counter += 1
                if not ((timetable.start_time <= start <= timetable.end_time)
                        or (timetable.start_time <= end <= timetable.end_time)
                        or (start <= timetable.start_time and end >= timetable.end_time)):
                    marker = True
                    break
            if marker or counter == 0:
                return self.create(request, *args, **kwargs)
            else:
                raise MyCustomException(detail={"Error": "Невозможно записать на эту дату и время, так как они заняты"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise MyCustomException(detail={"Error": "Некорректно введены дата и время"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TimetableUpdate(generics.UpdateAPIView):
    # изменение мероприятия в расписание
    permission_classes = (IsAuthenticated,)  # IsAuthorOrReadonlyTimetable
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

    def put(self, request, *args, **kwargs):
        place = int(request.POST.get("place"))
        event_date = request.POST.get("event_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        timetables = Timetable.objects.filter(place=place, event_date=event_date)

        s_t = start_time.split(':')
        e_t = end_time.split(':')

        start = datetime.time(int(s_t[0]), int(s_t[1]))
        end = datetime.time(int(e_t[0]), int(e_t[1]))

        if start < end:
            marker = False
            counter = 0
            for timetable in timetables:
                counter += 1
                if (not ((timetable.start_time <= start <= timetable.end_time)
                         or (timetable.start_time <= end <= timetable.end_time)
                         or (start <= timetable.start_time and end >= timetable.end_time))
                        or timetable.id == kwargs['pk']):
                    marker = True
                    break
            if marker or counter == 0:
                return self.update(request, *args, **kwargs)
            else:
                raise MyCustomException(
                    detail={"Error": "Невозможно записать на эту дату и время, так как они заняты"},
                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise MyCustomException(detail={"Error": "Некорректно введены дата и время"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    tags=["YourModel tag"],
    operation_id="Write here smth",
    operation_description="GET request",
)
class CreateUserView(generics.CreateAPIView):
    # регистрация нового пользователя
    model = get_user_model()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


'''
class UserRetrieveAPIView(generics.RetrieveAPIView):
    # просмотр пользователя
    model = get_user_model()
    permission_classes = [AllowAny]
    serializer_class = UserPrifileSerializer
'''


class UserInfoByToken(views.APIView):

    def post(self, request, format=None):
        print(request.user)
        data = {
            "id": str(request.user.id),
            "username": str(request.user.username),
            "first_name": str(request.user.first_name),
            "last_name": str(request.user.last_name)
        }
        return response.Response(data, status=status.HTTP_201_CREATED)


class UserAddMeetingAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # добавляет выбранные мероприятия из списка мероприятий пользователя
    model = Profile
    permission_classes = (IsAuthorOrReadonlyProfile,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            add_id_meeting = request.POST.get('meetings')
            profile = Profile.objects.get(id=request.user.id)
            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values()[i]["id"]))
            for add_id in add_id_meeting:
                meetings_list.append(add_id)
            # print(meetings_list)

            request.data._mutable = True
            request.data.pop("meetings")
            for meeting in meetings_list:
                request.data.appendlist('meetings', meeting)  # request.data.appendlist('meetings', add_id_meeting)
            # print(request.data)
            request.data._mutable = False
            return self.update(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"Error": "Введены не корректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class UserRemoveMeetingAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # убирает выбранные мероприятия из списка мероприятий пользователя
    model = Profile
    permission_classes = (IsAuthorOrReadonlyProfile,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            # print(request.data["meetings"])
            profile = Profile.objects.get(id=request.user.id)
            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values()[i]["id"]))

            new_meetings_list = list(set(meetings_list) - set(request.data.getlist('meetings')))

            request.data._mutable = True
            # изменение списка мероприятий
            request.data.pop("meetings")
            for meeting in new_meetings_list:
                request.data.appendlist('meetings', meeting)
            request.data._mutable = False

            return self.update(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"Error": "Введены не корректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TagsAPIView(generics.ListAPIView):
    # выводит список всех тегов без пагинации (для форм)
    model = Tags
    permission_classes = (IsAuthenticated,)
    serializer_class = TagsSerializer
    pagination_class = None
    queryset = Tags.objects.all()


class PlaceAPIView(generics.ListAPIView):
    # выводит список всех мест проведения без пагинации (для форм)
    model = Place
    permission_classes = (IsAuthenticated,)
    serializer_class = PlaceSerializer
    pagination_class = None
    queryset = Place.objects.all()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/api-authlogin/')


def accounts_profile_redirect(request):
    return HttpResponseRedirect('/meeting-api/v1/users/')
