import datetime
import uuid

from rest_framework import generics, views, response, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model, logout
from drf_yasg.utils import swagger_auto_schema

from .models import Profile, Meeting, Timetable, Place, Tags, Chat, Message, User, Voting, Field
from .serializers import (MeetingSerializer, ProfileSerializer, MeetingCreateSerializer, MeetingProfileListSerializer,
                          TimetableSerializer, UserSerializer, ProfileCreateSerializer, UserAddMeetingSerializer,
                          TagsSerializer, PlaceSerializer, ChatSerializer, MessageSerializer, ChatMessageSerializer,
                          ProfileChatSerializer, MeetingChatCreateSerializer, VotingSerializer, FieldSerializer,
                          FieldVotingSerializer, TimetableListSerializer, ProfileUpdateSerializer,
                          FieldForVoteSerializer)
from .permissions import (IsAuthorOrReadonlyAuthor, IsAuthorOrReadonlyUser, IsAuthorMeetingOrUser,
                          PermissionCreateObjects)
from .pagination import MeetingProfilesPagination, MeetingsPagination
from .castom_exeptions import MyCustomException


class MeetingProfileListAPIView(generics.RetrieveAPIView):
    # список участников мероприятия (нужен id мероприятия)
    queryset = Meeting.objects.all()
    pagination_class = MeetingProfilesPagination
    serializer_class = MeetingProfileListSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            Meeting.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор мероприятия",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingAPIView(generics.ListAPIView):
    # список по всеми мероприятиями + поиск
    model = Meeting
    serializer_class = MeetingSerializer
    pagination_class = MeetingsPagination
    permission_classes = (AllowAny,)

    filter_backends = [OrderingFilter]
    ordering = ['-seats_bool']

    def get_queryset(self):
        search = self.request.query_params.get("search")
        print(search)
        if search:
            queryset = self.model.objects.filter(title__icontains=search)
        else:
            queryset = self.model.objects.all()
        return queryset


class MeetingCreateAPIView(generics.CreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingCreateSerializer
    permission_classes = (PermissionCreateObjects, )

    def post(self, request, *args, **kwargs):
        """Обработка создания мероприятия"""
        try:
            if type(request.data) is dict:
                request.data['author'] = request.user.id
                request.data['seats_bool'] = True
                id_timetable = request.data['timetable']
            else:
                id_timetable = request.POST.get("timetable")
                request.data._mutable = True
                request.data['author'] = request.user.id
                request.data['seats_bool'] = True
                request.data._mutable = False

            timetable = Timetable.objects.get(id=id_timetable)

            id_place = Place.objects.get(office=timetable.place).id

            places = Place.objects.get(id=id_place)
            max_participant = places.max_participant
            if type(request.data) is dict:
                request.data['seats'] = max_participant
            else:
                request.data._mutable = True
                request.data['seats'] = max_participant
                request.data._mutable = False

            timetable.used = True
            timetable.save()

            return self.create(request, *args, **kwargs)
        except Exception as e:
            raise MyCustomException(detail={e.__str__()},
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """Переопределение метода создания"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # автодобавление автора в участники мероприятия
        profile_author = Profile.objects.get(user=request.user.id)
        meeting = Meeting.objects.get(title=serializer.data['title'],
                                      author=serializer.data['author'],
                                      created_at=serializer.data['created_at'])
        profile_author.meetings.add(meeting)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MeetingDetail(generics.RetrieveDestroyAPIView):
    # изменение мероприятия или просто его просмотр (если не автор)
    permission_classes = (IsAuthorOrReadonlyAuthor,)
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def get(self, request, *args, **kwargs):
        """Просмотр мероприятия"""
        try:
            meeting = Meeting.objects.get(pk=kwargs['pk'])
            if not meeting.past_bool and meeting.timetable.event_date >= datetime.date.today() and \
                    meeting.timetable.start_time >= datetime.datetime.now().time():
                meeting.past_bool = True
                meeting.save()
            return self.retrieve(request, *args, **kwargs)
        except Exception as e:
            print(e)
            raise MyCustomException(detail="Введен неверный идентификатор мероприятия",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthorOrReadonlyAuthor,)
    queryset = Meeting.objects.all()
    serializer_class = MeetingCreateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
        """Автоматическое вписывание пользователя при создании профиля (авторизованный пользователь)"""
        if type(request.data) is dict:
            request.data['user'] = request.user.id
        else:
            request.data._mutable = True
            request.data['user'] = request.user.id
            request.data._mutable = False
        return self.create(request, *args, **kwargs)


class ProfileDetail(generics.RetrieveAPIView):
    # изменение доп информации о пользователе
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


class TimetableCreate(generics.CreateAPIView):
    # запись мероприятия в расписание
    permission_classes = (PermissionCreateObjects,)
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

    def post(self, request, *args, **kwargs):
        """Создание записи в расписании"""
        try:
            dict_marker = False
            if type(request.data) is dict:
                place = request.data["place"]
                event_date = request.data["event_date"]
                start_time = request.data["start_time"]
                end_time = request.data["end_time"]
                dict_marker = True
            else:
                place = request.POST.get("place")
                event_date = request.POST.get("event_date")
                start_time = request.POST.get("start_time")
                end_time = request.POST.get("end_time")

            if dict_marker:
                date_tuple = tuple(map(int, event_date.split('.')))
                event_date = datetime.date(date_tuple[2], date_tuple[1], date_tuple[0])
            else:
                date_tuple = tuple(map(int, event_date.split('-')))
                event_date = datetime.date(date_tuple[0], date_tuple[1], date_tuple[2])

            if event_date < datetime.date.today():
                raise MyCustomException(detail="Это не машина времени, уже ничего не изменить(((",
                                        status_code=status.HTTP_400_BAD_REQUEST)

            timetables = Timetable.objects.filter(place=place, event_date=event_date)

            s_t = start_time.split(':')
            e_t = end_time.split(':')

            start = datetime.time(int(s_t[0]), int(s_t[1]))
            end = datetime.time(int(e_t[0]), int(e_t[1]))
            if start < end:
                marker = False
                counter = 0
                for timetable in timetables:
                    # print(timetable)
                    counter += 1
                    if not ((timetable.start_time <= start <= timetable.end_time)
                            or (timetable.start_time <= end <= timetable.end_time)
                            or (start <= timetable.start_time and end >= timetable.end_time)):
                        marker = True
                    else:
                        marker = False
                        break
                if marker or counter == 0:
                    if dict_marker:
                        request.data['used'] = False
                        request.data['author'] = request.user.id
                    else:
                        request.data._mutable = True
                        request.data['used'] = False
                        request.data['author'] = request.user.id
                        request.data._mutable = False
                    return self.create(request, *args, **kwargs)
                else:
                    raise MyCustomException(detail="Невозможно записать на эту дату и время, так как они заняты",
                                            status_code=status.HTTP_400_BAD_REQUEST)
            else:
                raise MyCustomException(detail="Некорректно введены дата и время",
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise MyCustomException(detail={e.__str__()},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TimetableUpdate(generics.UpdateAPIView, generics.RetrieveAPIView):
    # изменение мероприятия в расписание
    permission_classes = (IsAuthorOrReadonlyAuthor,)
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

    def put(self, request, *args, **kwargs):
        try:
            timetable = Timetable.objects.get(pk=kwargs['pk'])
            dict_marker = False
            if type(request.data) is dict:
                place = request.data["place"]
                event_date = request.data["event_date"]
                start_time = request.data["start_time"]
                end_time = request.data["end_time"]
                request.data["used"] = timetable.used
                dict_marker = True
            else:
                place = int(request.POST.get("place"))
                event_date = request.POST.get("event_date")
                start_time = request.POST.get("start_time")
                end_time = request.POST.get("end_time")

                request.data._mutable = True
                request.data["used"] = timetable.used
                request.data._mutable = False

            if dict_marker:
                date_tuple = tuple(map(int, event_date.split('.')))
                event_date = datetime.date(date_tuple[2], date_tuple[1], date_tuple[0])

            if event_date < datetime.date.today():
                raise MyCustomException(detail="Это не машина времени, уже ничего не изменить(((",
                                        status_code=status.HTTP_400_BAD_REQUEST)
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
                    else:
                        marker = False
                        break
                if marker or counter == 0:
                    return self.update(request, *args, **kwargs)
                else:
                    raise MyCustomException(
                        detail="Невозможно записать на эту дату и время, так как они заняты",
                        status_code=status.HTTP_400_BAD_REQUEST)
            else:
                raise MyCustomException(detail="Некорректно введены дата и время",
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise MyCustomException(detail=e.__str__(),
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TimetableListAPIView(generics.ListAPIView):
    model = Timetable
    serializer_class = TimetableListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        queryset = self.model.objects.filter(author=self.request.user.id, used=False,
                                             event_date__gte=datetime.date.today())
        return queryset


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
    # добавляет выбранные мероприятия из списка мероприятий пользователя
    model = Profile
    permission_classes = (IsAuthorMeetingOrUser,)
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
            query_marker = False
            meeting_id = None
            if request.query_params.get("meeting_id"):
                meeting_id = request.query_params.get("meeting_id")
                query_marker = True

            if not query_marker:
                kwargs['pk'] = request.user.id
            # print(f'Получили {request.data}')
            profile = Profile.objects.get(user=request.user.id)

            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values()[i]["id"]))

            if type(request.data) is dict:
                add_meeting = request.data['meetings'] if not query_marker else meeting_id
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
    # убирает выбранные мероприятия из списка мероприятий пользователя
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


class TagsAPIView(generics.ListAPIView):
    # выводит список всех тегов без пагинации (для форм)
    model = Tags
    permission_classes = (IsAuthenticated,)
    serializer_class = TagsSerializer
    pagination_class = None
    queryset = Tags.objects.all()

    def get_queryset(self):
        search = self.request.query_params.get("search")
        if search:
            queryset = self.model.objects.filter(tag_name__icontains=search)[:10]
        else:
            queryset = self.model.objects.all()[:10]
        return queryset


class PlaceAPIView(generics.ListAPIView):
    # выводит список всех мест проведения без пагинации (для форм)
    model = Place
    permission_classes = (IsAuthenticated,)
    serializer_class = PlaceSerializer
    pagination_class = None
    queryset = Place.objects.all()


class ChatAPIView(generics.ListAPIView):
    # список всех чатов
    model = Chat
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class ChatCreateAPIView(generics.CreateAPIView):
    model = Chat
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def post(self, request, *args, **kwargs):
        """Создание чата с автоопределением автора"""
        # profile_author.chats.add()
        if type(request.data) is dict:
            request.data['author'] = request.user.id
        else:
            request.data._mutable = True
            request.data['author'] = request.user.id
            request.data._mutable = False
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Сохранение чата с автодобавлением автора в участники чата"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # автодобавление автора в участники чата
        profile_author = Profile.objects.get(user=request.user.id)
        chat = Chat.objects.get(name=serializer.data['name'],
                                author=serializer.data['author'],
                                created_at=serializer.data['created_at'])
        profile_author.chats.add(chat)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageCreateAPIView(generics.CreateAPIView):
    model = Message
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def post(self, request, *args, **kwargs):
        """Создание сообщения"""
        try:
            Chat.objects.get(pk=kwargs['pk'])
            if type(request.data) is dict:
                request.data['chat'] = kwargs['pk']
                request.data['user'] = request.user.id
            else:
                request.data._mutable = True
                request.data['chat'] = kwargs['pk']
                request.data['user'] = request.user.id
                request.data._mutable = False
        except:
            raise MyCustomException(detail="Введен не корректный индификатор чата",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.create(request, *args, **kwargs)


class MessagesAPIView(generics.ListAPIView):
    # список всех сообщений
    model = Message
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    pagination_class = MeetingsPagination
    filter_backends = [OrderingFilter]
    ordering = ['-created_at']

    def get(self, request, *args, **kwargs):
        # сделать с фильтром по чату
        return self.list(request, *args, **kwargs)


class ChatMessageAPIView(generics.RetrieveAPIView):
    # выводит информацию о чате
    model = Chat
    pagination_class = MeetingsPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatMessageSerializer
    queryset = Chat.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            Chat.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор чата",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class ProfileChatAddAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # добавление списка (или одного) мероприятий в профиль пользователя
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор профиля",
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        # проверка на честность
        profile_author = Profile.objects.get(user=request.user.id)
        kwargs['pk'] = profile_author

        try:
            chats_list = []
            for i in range(profile_author.chats.count()):
                chats_list.append(str(profile_author.chats.values()[i]["id"]))
            if type(request.data) is dict:
                request.data['chats'] = chats_list
            else:
                request.data._mutable = True
                # изменение списка мероприятий
                for chats in chats_list:
                    request.data.appendlist('chats', chats)
                request.data._mutable = False
        except:
            raise MyCustomException(detail="Введены не корректные данные",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


class ProfileChatRemoveAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthorOrReadonlyUser,)

    def get(self, request, *args, **kwargs):
        """Получение списка мероприятий профиля"""
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор профиля",
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """Удаление списка (или одного) мероприятий из профиля пользователя"""
        # на честность отправителя :)
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)
        kwargs['pk'] = profile_author

        try:
            profile = Profile.objects.get(id=request.user.id)
            chats_list = []
            for i in range(profile.chats.count()):
                chats_list.append(str(profile.chats.values('id')[i]["id"]))
            # print(chats_list)
            new_chats_list = list(set(chats_list) - set(request.data.getlist('chats')))

            if type(request.data) is dict:
                request.data['chats'] = new_chats_list
            else:
                request.data._mutable = True
                # изменение списка мероприятий
                request.data.pop('chats')
                for chats in new_chats_list:
                    request.data.appendlist('chats', chats)
                request.data._mutable = False
            # print(request.data)
        except:
            raise MyCustomException(detail="Введены не корректные данные",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


class MeetingChatAddAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    """Добавление чата для мероприятия"""
    model = Meeting
    serializer_class = MeetingChatCreateSerializer
    pagination_class = MeetingsPagination
    queryset = Meeting.objects.all()
    permission_classes = (PermissionCreateObjects, )

    def get(self, request, *args, **kwargs):
        try:
            Meeting.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор мероприятия",
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if Meeting.objects.get(id=kwargs['pk']).chat is None:
            try:
                chat = Chat()
                chat.name = Meeting.objects.get(id=kwargs['pk']).title
                chat.author = request.user  # в будущем возможен баг (если id User и id Profile будут разные)
                chat.save()

                new_chat = Chat.objects.get(created_at=chat.created_at, author=request.user.id)
                Profile.objects.get(user=request.user).chats.add(new_chat)

                request.data._mutable = True
                request.data['chat'] = new_chat.id
                request.data._mutable = False
                return self.update(request, *args, **kwargs)
            except:
                MyCustomException(detail="Возникла ошибка во время создания чата",
                                  status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise MyCustomException(detail="У этого мероприятия уже есть чат",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingKickUser(generics.UpdateAPIView):
    model = Profile
    permission_classes = (IsAuthenticated,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def put(self, request, *args, **kwargs):
        """
            Удаление создателем мероприятия пользователя
        """
        meeting = Meeting.objects.get(id=kwargs['meeting_id'])
        kicking_user = Profile.objects.get(user=User.objects.get(id=kwargs['pk']))

        if meeting.author == request.user and meeting in kicking_user.meetings.all():
            meetings_list = []
            for i in range(kicking_user.meetings.count()):
                meetings_list.append(str(kicking_user.meetings.values('id')[i]["id"]))
            try:
                if type(request.data) is dict:
                    timetable = Timetable.objects.get(id=meeting.timetable.id)
                    max_seats = Place.objects.get(id=timetable.place.id)
                    if meeting.seats < max_seats.max_participant:
                        new_meetings_list = list(set(meetings_list) - {str(meeting.id)})
                        request.data['meetings'] = new_meetings_list

                        meeting.seats += 1
                        if meeting.seats >= 1:
                            meeting.seats_bool = True
                        meeting.save()
                    else:
                        raise MyCustomException(detail="Нельзя выйти из мероприятия, алярм!",
                                                status_code=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                raise MyCustomException(detail=e.__str__(),
                                        status_code=status.HTTP_400_BAD_REQUEST)
            else:
                return self.update(request, *args, **kwargs)


class MeetingAddQR(views.APIView):
    """
        Реализация присоединения к мероприятию через qr-код
    """
    def post(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user.id)
            meeting = Meeting.objects.get(id=kwargs['pk'])
            if meeting.seats > 0:
                meeting.seats -= 1
                meeting.save()
                profile.meetings.add(meeting)
                profile.save()
            else:
                return response.Response({"detail": "В мероприятии нет мест"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response({"detail": f"Не удалось присоединиться к мероприятию ({e.__str__()})"},
                                     status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"detail": "Удачно"}, status=status.HTTP_201_CREATED)


class VotingAPIView(generics.ListAPIView):
    """Лист всех голосований"""
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()


class VotingRenameAPIView(generics.UpdateAPIView):
    """Переименование голосования"""
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class VotingCreateAPIView(generics.CreateAPIView):
    # создание голосования
    model = Voting
    permission_classes = (PermissionCreateObjects,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def post(self, request, *args, **kwargs):
        """Создание голосования"""
        try:
            author = Meeting.objects.get(id=kwargs['pk']).author

            if request.user.id == author.id:
                if type(request.data) is dict:
                    request.data['meeting'] = kwargs['pk']
                    request.data['author'] = request.user.id
                else:
                    request.data._mutable = True
                    request.data['meeting'] = kwargs['pk']
                    request.data['author'] = request.user.id
                    request.data._mutable = False
            else:
                raise MyCustomException(detail="Вы не являетесь создателем мероприятия",
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except:
            raise MyCustomException(detail="Введен неверный индификатор голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.create(request, *args, **kwargs)


class VotingDestroyAPIView(generics.DestroyAPIView):
    # удаление голосования
    model = Voting
    permission_classes = (IsAuthenticated,)  # изменить (может только автор)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def delete(self, request, *args, **kwargs):
        """Удаление голосования"""
        try:
            Voting.objects.get(pk=kwargs['pk'])
            return self.destroy(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldCreateAPIView(generics.CreateAPIView):
    # создание поля голосования
    model = Field
    permission_classes = (PermissionCreateObjects,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    @staticmethod
    def create_fields_from_list(vote, names):
        """Создание полей из списка"""
        for i in names:
            name = ' '.join(i.split('_'))
            field = Field.objects.create(
                name=name,
                vote=Voting.objects.get(id=vote),
                count_votes=0,
            )
            field.save()

    def post(self, request, *args, **kwargs):
        """Создание поля в голосовании"""
        try:
            if type(request.data) is dict:
                names = request.data['name'].split(' ')
                self.create_fields_from_list(kwargs['pk'], names)
                return Response(status=status.HTTP_200_OK)
            else:
                request.data._mutable = True
                request.data['vote'] = kwargs['pk']
                request.data['count_votes'] = 0
                request.data._mutable = False
                return self.create(request, *args, **kwargs)
        except Exception as excep:
            raise MyCustomException(detail=f"{excep}",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldRetrieveAPIView(generics.RetrieveAPIView):
    # просмотр информации поля голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def get(self, request, *args, **kwargs):
        """Получение поля голосования"""
        try:
            Field.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldDestroyAPIView(generics.DestroyAPIView):
    """Удаление поля для голосования"""
    model = Field
    permission_classes = (PermissionCreateObjects,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            field = Field.objects.get(pk=kwargs['pk'])
            vote = Voting.objects.get(id=field.vote.id)
            vote.all_votes -= field.count_votes
            vote.save()
            return self.destroy(request, *args, **kwargs)
        except Exception as ex:
            raise MyCustomException(detail=f"Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldRenameAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    model = Field
    permission_classes = (PermissionCreateObjects,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def patch(self, request, *args, **kwargs):
        """Для изменения имени"""
        return self.partial_update(request, *args, **kwargs)


class FieldAddVoteAPIView(generics.UpdateAPIView):
    # реализация голосования пользователем за данный вариант ответа
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldForVoteSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            id_new_user = request.user.id
            field = Field.objects.get(id=kwargs['pk'])

            users_list = []
            count_votes = field.count_votes
            print(count_votes)
            for id_user in range(count_votes):
                users_list.append(field.users.values('id')[id_user]['id'])

            if id_new_user not in users_list:
                users_list.append(id_new_user)
                print(users_list)
                count_votes += 1
                vote = Voting.objects.get(id=field.vote.id)
                vote.all_votes += 1
                vote.save()

            if type(request.data) is dict:
                request.data['users'] = users_list
                request.data['count_votes'] = count_votes
            else:
                request.data._mutable = True
                if request.data.getlist('users'):
                    request.data.pop('users')
                for i in range(count_votes):
                    request.data.appendlist('users', users_list[i])
                request.data['count_votes'] = count_votes
                request.data._mutable = False

        except Exception as e:
            raise MyCustomException(detail=f"Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


class FieldRemoveVoteAPIView(generics.UpdateAPIView):
    # реализация удаления голоса
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldForVoteSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            id_user = request.user.id
            field = Field.objects.get(id=kwargs['pk'])

            users_list = []
            count_users = field.users.count()
            for user in range(count_users):
                users_list.append(field.users.values('id')[user]['id'])

            if id_user in users_list:
                users_list.remove(id_user)
                count_users -= 1
                vote = Voting.objects.get(id=field.vote.id)
                vote.all_votes -= 1
                vote.save()
            else:
                raise MyCustomException(detail="Вы не голосовали в этом голосовании",
                                        status_code=status.HTTP_400_BAD_REQUEST)

            if type(request.data) is dict:
                request.data['users'] = users_list
                request.data['count_votes'] = count_users
            else:
                request.data._mutable = True
                if request.data.getlist('users'):
                    request.data.pop('users')
                for i in range(count_users):
                    request.data.appendlist('users', users_list[i])
                request.data['count_votes'] = count_users
                request.data._mutable = False
        except:
            raise MyCustomException(detail="Введен неверный идентификатор  поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


class RecommendedMeetingsForTags(generics.ListAPIView):
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

        queryset = self.model.objects.filter(tags__in=list_tags_user,
                                             seats_bool=True, timetable__in=timetable_list).distinct()
        return queryset


clients = {}
chats = []


class ChatWebSocket(AsyncJsonWebsocketConsumer):
    """
    Обмен сообщениями происходит через передачу сообщений notify,
    сами сообщения передаются в виде json-объектов с типом kind="message"
    для обычного сообщения или kind="notification" для системных уведомлений.
    Текст сообщения всегда отправляется в поле text.
    """

    async def connect(self):
        global clients
        clients[self.scope["user"]] = self.channel_name
        self.send_json({"type": "welcome"})

        async def disconnect(self):
            pass

    async def receive_json(self, content, **kwargs):
        global chats, clients
        if content["type"] == "invite":
            chat = str(uuid.uuid4())
            chats.append(chat)
            for member in content["members"]:
                self.channel_layer.send(clients[member], {
                    "type": "invite",
                    "id": chat
                })
        if content["type"] == "disconnect":
            self.channel_layer.group_send(content["id"], {
                "type": "disconnect",
                "id": content["id"]
            })
            chats.remove(content["id"])
        if content["type"] == "notify":
            # входящее сообщение от клиента
            self.channel_layer.group_send(content["id"], {
                "type": "notify",
                "kind": content.kind,
                "message": content.message,
                "sender": self.channel_name
            })

    async def chat_message(self, event):
        # пересылаем клиенту внутреннее сообщение о приглашении в группу
        if event["type"] == "invite":
            #  добавимся так же в группу
            await self.group_add(event["id"], self.channel_name)
            self.send_json(event)
        if event["type"] == "disconnect":
            # отключаемся от группы
            await self.group_discard(event["id"], self.channel_name)
        if event["type"] == "notify":
            if event["sender"] != self.channel_name:
                self.send_json(event)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/api-authlogin/')


def accounts_profile_redirect(request):
    return HttpResponseRedirect('/meeting-api/v1/users/')
