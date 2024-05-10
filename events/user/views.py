from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.urls import views
from events.meetings.permissions import IsAuthorOrReadonlyUser
from events.meetings.castom_exeptions import MyCustomException
from events.meetings.models import Meeting, Timetable, Place
from events.meetings.serializers import MeetingSerializer
from events.meetings.pagination import MeetingsPagination
from .models import Profile
from .serializers import (ProfileCreateSerializer, ProfileSerializer, ProfileUpdateSerializer, UserSerializer,
                          UserAddMeetingSerializer)
import datetime


class ProfileAPIView(generics.ListAPIView):
    """Список профилей"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)


class ProfileCreateAPIView(generics.CreateAPIView):
    """Создание доп информации профиля"""
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """Автоматическое вписывание пользователя при создании профиля (авторизованный пользователь)"""
        if type(request.data) is dict:
            request.data['user'] = request.user.id
        else:
            request.data._mutable = True
            request.data['user'] = request.user.id
            request.data._mutable = False
        return self.create(request, *args, **kwargs)


class ProfileDetail(generics.RetrieveAPIView):
    """Изменение доп информации о пользователе"""
    permission_classes = (IsAuthorOrReadonlyUser,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        """Проверка на честность"""
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except Exception as e:
            raise MyCustomException(detail="Данного пользователя не существует",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class ProfileUpdate(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthorOrReadonlyUser,)
    serializer_class = ProfileUpdateSerializer

    def put(self, request, *args, **kwargs):
        """Ни Х* Я"""
        return self.update(request, *args, **kwargs)


@swagger_auto_schema(
    tags=["YourModel tag"],
    operation_id="Write here smth",
    operation_description="GET request",
)
class CreateUserView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
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
    """Предоставляет информацию о пользователе по его токену"""
    def post(self, request, format=None):
        # print(request.user)
        try:
            profile = Profile.objects.get(user=request.user.id)
            id_profile = profile.id
            # print(profile.id)
        except:
            id_profile = None
        data = {
            "id": str(request.user.id),
            "username": str(request.user.username),
            "first_name": str(request.user.first_name),
            "last_name": str(request.user.last_name),
            "id_profile": str(id_profile),
        }
        return response.Response(data, status=status.HTTP_201_CREATED)


class UserAddMeetingAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    """Добавляет выбранные мероприятия из списка мероприятий пользователя"""
    model = Profile
    permission_classes = (IsAuthorOrReadonlyUser,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор профиля",
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            kwargs['pk'] = request.user.id
            # print(f'Получили {request.data}')
            profile = Profile.objects.get(user=request.user.id)

            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values()[i]["id"]))

            if type(request.data) is dict:
                add_meeting = request.data['meetings']
                meeting = Meeting.objects.get(id=add_meeting)

                list_meetings = profile.meetings.all()

                if meeting.seats_bool:
                    if add_meeting not in list_meetings:
                        meetings_list.append(str(add_meeting))
                        request.data['meetings'] = meetings_list
                        meeting.seats -= 1
                        if meeting.seats == 0:
                            meeting.seats_bool = False
                        meeting.save()
                    else:
                        raise MyCustomException(detail="Вы уже записаны на это мероприятие",
                                                status_code=status.HTTP_400_BAD_REQUEST)
                else:
                    raise MyCustomException(detail="На мероприятии нет мест",
                                            status_code=status.HTTP_400_BAD_REQUEST)

            else:
                add_id_meeting = request.data.getlist('meetings')

                for add_id in add_id_meeting:
                    meetings_list.append(add_id)

                    meeting = Meeting.objects.get(id=add_id)
                    if meeting.seats_bool:
                        meeting.seats -= 1
                        if meeting.seats == 0:
                            meeting.seats_bool = False
                        meeting.save()
                    else:
                        raise MyCustomException(detail="На мероприятии нет мест",
                                                status_code=status.HTTP_400_BAD_REQUEST)

                request.data._mutable = True
                request.data.pop("meetings")
                for meeting in meetings_list:
                    request.data.appendlist('meetings', meeting)
                request.data._mutable = False

            # print(f'Записали {add_id_meeting}')

            return self.update(request, *args, **kwargs)
        except Exception as e:
            raise MyCustomException(detail={e.__str__()},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class UserRemoveMeetingAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    """Убирает выбранные мероприятия из списка мероприятий пользователя"""
    model = Profile
    permission_classes = (IsAuthorOrReadonlyUser,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор профиля",
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """Убирает выбранные мероприятия из списка мероприятий пользователя"""
        try:
            profile = Profile.objects.get(user=request.user.id)
            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values('id')[i]["id"]))

            try:
                if type(request.data) is dict:
                    remove_id_meeting = request.data['meetings']
                    remove_meeting = [*remove_id_meeting]

                    meeting = Meeting.objects.get(id=remove_id_meeting)
                    timetable = Timetable.objects.get(id=meeting.timetable.id)
                    # print(timetable.place.id)
                    max_seats = Place.objects.get(id=timetable.place.id)
                    # print(f'{meeting.seats} <= {max_seats.max_participant}')
                    if meeting.seats < max_seats.max_participant:
                        new_meetings_list = list(set(meetings_list) - set(remove_meeting))
                        # print(f'new_meetings_list = list(set({meetings_list}) - set({remove_meeting})')
                        request.data['meetings'] = new_meetings_list
                        # print(request.data['meetings'])

                        meeting.seats += 1
                        if meeting.seats >= 1:
                            meeting.seats_bool = True
                        meeting.save()
                    else:
                        raise MyCustomException(detail="Нельзя выйти из мероприятия, алярм!",
                                                status_code=status.HTTP_400_BAD_REQUEST)
                else:
                    remove_id_meeting = request.data.getlist('meetings')
                    new_meetings_list = list(set(meetings_list) - set(remove_id_meeting))

                    request.data._mutable = True
                    # изменение списка мероприятий
                    request.data.pop("meetings")
                    for meeting in new_meetings_list:
                        request.data.appendlist('meetings', meeting)
                    request.data._mutable = False

                    for remove_id in remove_id_meeting:
                        meetings_list.append(remove_id)

                        meeting = Meeting.objects.get(id=remove_id)
                        timetable = Timetable.objects.get(id=meeting.timetable.id)
                        max_seats = Place.objects.get(id=timetable.place.id)
                        if meeting.seats < max_seats.max_participant:
                            meeting.seats += 1
                            if meeting.seats >= 1:
                                meeting.seats_bool = True
                            meeting.save()
            except Exception as e:
                raise MyCustomException(detail=e.__str__(),
                                        status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise MyCustomException(detail=e.__str__(),
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


class RecommendedMeetingsForTags(generics.ListAPIView):
    """Подборка мероприятий по тегам пользователя"""
    model = Meeting
    permission_classes = (IsAuthenticated,)
    serializer_class = MeetingSerializer
    pagination_class = MeetingsPagination

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        tags_user = profile.get_tags_list().values()
        list_tags_user = []
        for i in range(profile.get_tags_list().count()):
            list_tags_user.append(tags_user[i]['id'])

        today = datetime.date.today()
        next_six_month = (today + datetime.timedelta(days=184))  # мероприятия на пол года вперед
        timetable = Timetable.objects.filter(
            event_date__range=[today, next_six_month])
        timetable_list = []
        for i in range(timetable.count()):
            timetable_list.append(timetable[i].id)

        for i in range(profile.get_tags_list().count()):
            list_tags_user.append(tags_user[i]['id'])

        queryset = self.model.objects.filter(tags__in=list_tags_user, seats_bool=True, timetable__in=timetable_list)
        return queryset

