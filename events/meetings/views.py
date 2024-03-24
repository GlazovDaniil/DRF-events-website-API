import datetime
import uuid

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.http import HttpResponseRedirect, Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from .models import Profile, Meeting, Timetable, Place, Tags, Chat, Message, User, Voting, Field
from .serializers import (MeetingSerializer, ProfileSerializer, MeetingCreateSerializer, MeetingProfileListSerializer,
                          TimetableSerializer, UserSerializer, ProfileCreateSerializer, UserAddMeetingSerializer,
                          TagsSerializer, PlaceSerializer, ChatSerializer, MessageSerializer, ChatMessageSerializer,
                          ProfileChatSerializer, MeetingChatCreateSerializer, VotingSerializer, FieldSerializer,
                          FieldVotingSerializer)
from .permissions import IsAuthorOrReadonlyAuthor, IsAuthorOrReadonlyUser
from rest_framework import generics, views, response, status
from django.contrib.auth import logout
from .pagination import MeetingProfilesPagination, MeetingsPagination
from .castom_exeptions import MyCustomException
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.filters import OrderingFilter


def error404(request, exception):
    raise NotFound(detail="Error 404, page not found", code=404)


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
            raise MyCustomException(detail={"detail": "Введен неверный индификатор мероприятия"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingAPIView(generics.ListAPIView):
    # список по всем мероприятиям
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = MeetingsPagination
    permission_classes = (AllowAny,)

    filter_backends = [OrderingFilter]
    ordering = ['-seats_bool']


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
            # user = User.objects.get(id=request.user.id)
            # profile_author = Profile.objects.get(user=user.id)

            request.data._mutable = True
            request.data['author'] = request.user.id
            request.data._mutable = False

            return self.create(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введены некорректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
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


class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    # изменение мероприятия или просто его просмотр (если не автор)
    permission_classes = (IsAuthorOrReadonlyAuthor,)
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def get(self, request, *args, **kwargs):
        try:
            meeting = Meeting.objects.get(pk=kwargs['pk'])
            """user = Profile.objects.get(user=request.user)
            user_registered = False
            meetings_list = []
            for i in range(user.meetings.count()):
                meetings_list.append(str(user.meetings.values('id')[i]["id"]))
            print(meeting.id)
            print(meetings_list)
            if str(meeting.id) in meetings_list:
                user_registered = True
            print(user_registered)
            request.data['user_registered'] = user_registered

            serializer = self.get_serializer(data=request.data)
            serializer.context["user_registered"] = request.data['user_registered']
            # serializer.is_valid(raise_exception=True)"""

            return self.retrieve(request, *args, **kwargs)
        except Exception as e:
            print(e)
            raise MyCustomException(detail={"error": "Введен неверный индификатор мероприятия"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


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
        # print(request.data)
        if type(request.data) is dict:
            request.data['user'] = request.user.id
        else:
            request.data._mutable = True
            request.data['user'] = request.user.id
            request.data._mutable = False
        return self.create(request, *args, **kwargs)


class ProfileDetail(generics.RetrieveUpdateAPIView):
    # изменение доп информации о пользователе
    permission_classes = (IsAuthorOrReadonlyUser,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор профиля"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TimetableCreate(generics.CreateAPIView):
    # запись мероприятия в расписание
    permission_classes = (IsAuthenticated,)
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

    def post(self, request, *args, **kwargs):
        try:
            place = request.POST.get("place")
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
                    # print(timetable)
                    counter += 1
                    if not ((timetable.start_time <= start <= timetable.end_time)
                            or (timetable.start_time <= end <= timetable.end_time)
                            or (start <= timetable.start_time and end >= timetable.end_time)):
                        marker = True
                        break
                if marker or counter == 0:
                    request.data._mutable = True
                    request.data['author'] = request.user.id
                    request.data._mutable = False
                    return self.create(request, *args, **kwargs)
                else:
                    raise MyCustomException(detail={"error": "Невозможно записать на эту дату и время, так как они заняты"},
                                            status_code=status.HTTP_400_BAD_REQUEST)
            else:
                raise MyCustomException(detail={"error": "Некорректно введены дата и время"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise MyCustomException(detail={"error": e.__str__()},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TimetableUpdate(generics.UpdateAPIView):
    # изменение мероприятия в расписание
    permission_classes = (IsAuthorOrReadonlyAuthor,)
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

    def put(self, request, *args, **kwargs):
        try:
            Timetable.objects.get(pk=kwargs['pk'])

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
                        detail={"error": "Невозможно записать на эту дату и время, так как они заняты"},
                        status_code=status.HTTP_400_BAD_REQUEST)
            else:
                raise MyCustomException(detail={"error": "Некорректно введены дата и время"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор расписания"},
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
    permission_classes = (IsAuthorOrReadonlyUser,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор профиля"},
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

                if meeting.seats > 0:
                    if add_meeting not in list_meetings:
                        meetings_list.append(str(add_meeting))
                        request.data['meetings'] = meetings_list
                        meeting.seats -= 1
                        if meeting.seats == 0:
                            meeting.seats_bool = False
                        meeting.save()
                    else:
                        raise MyCustomException(detail={"error": "Вы уже записаны на это мероприятие"},
                                                status_code=status.HTTP_400_BAD_REQUEST)
                else:
                    raise MyCustomException(detail={"error": "На мероприятии нет мест"},
                                            status_code=status.HTTP_400_BAD_REQUEST)

            else:
                add_id_meeting = request.data.getlist('meetings')

                for add_id in add_id_meeting:
                    meetings_list.append(add_id)

                    meeting = Meeting.objects.get(id=add_id)
                    if meeting.seats > 0:
                        meeting.seats -= 1
                        if meeting.seats == 0:
                            meeting.seats_bool = False
                        meeting.save()
                    else:
                        raise MyCustomException(detail={"error": "На мероприятии нет мест"},
                                                status_code=status.HTTP_400_BAD_REQUEST)

                request.data._mutable = True
                request.data.pop("meetings")
                for meeting in meetings_list:
                    request.data.appendlist('meetings', meeting)
                request.data._mutable = False

            # print(f'Записали {add_id_meeting}')

            return self.update(request, *args, **kwargs)
        except Exception as e:
            raise MyCustomException(detail={"error": e.__str__()},
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
            raise MyCustomException(detail={"error": "Введен неверный индификатор профиля"},
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            # print(request.data["meetings"])
            profile = Profile.objects.get(user=request.user.id)
            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values('id')[i]["id"]))

            try:
                if type(request.data) is dict:
                    remove_id_meeting = request.data['meetings']

                    meeting = Meeting.objects.get(id=remove_id_meeting)
                    timetable = Timetable.objects.get(id=meeting.timetable)
                    max_seats = Place.objects.get(id=timetable.place)
                    if meeting.seats < max_seats.max_participant:
                        new_meetings_list = list(set(meetings_list) - set(remove_id_meeting))
                        request.data['meetings'] = new_meetings_list
                        print(request.data['meetings'])

                        meeting.seats += 1
                        if meeting.seats >= 1:
                            meeting.seats_bool = True
                        meeting.save()
                    else:
                        raise MyCustomException(detail={"error": "На мероприятии нет мест"},
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

                        meeting = Meeting.objects.get(id=remove_id_meeting)
                        timetable = Timetable.objects.get(id=meeting.timetable)
                        max_seats = Place.objects.get(id=timetable.place)
                        if meeting.seats < max_seats.max_participant:
                            meeting.seats += 1
                            if meeting.seats >= 1:
                                meeting.seats_bool = True
                            meeting.save()
                        else:
                            raise MyCustomException(detail={"error": "На мероприятии нет мест"},
                                                    status_code=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                raise MyCustomException(detail={"error": e.__str__()},
                                        status_code=status.HTTP_400_BAD_REQUEST)

            return self.update(request, *args, **kwargs)
        except Exception as e:
            raise MyCustomException(detail={"error": e.__str__()},
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


class ChatAPIView(generics.ListAPIView):
    # список всех чатов
    model = Chat
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class ChatCreateAPIView(generics.CreateAPIView):
    # создание чата
    model = Chat
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def post(self, request, *args, **kwargs):
        # profile_author.chats.add()

        request.data._mutable = True
        request.data['author'] = request.user.id
        request.data._mutable = False
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
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
    # создание сообщения
    model = Message
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            Chat.objects.get(pk=kwargs['pk'])
            request.data._mutable = True
            request.data['chat'] = kwargs['pk']
            request.data['user'] = request.user.id
            request.data._mutable = False
            return self.create(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен не корректный индификатор чата"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


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
            raise MyCustomException(detail={"error": "Введен неверный индификатор чата"},
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
            raise MyCustomException(detail={"error": "Введен неверный индификатор профиля"},
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        # проверка на честность
        profile_author = Profile.objects.get(user=request.user.id)
        kwargs['pk'] = profile_author

        # print(profile.chats.values())
        try:
            chats_list = []
            for i in range(profile_author.chats.count()):
                chats_list.append(str(profile_author.chats.values()[i]["id"]))
            # print(chats_list)
            request.data._mutable = True

            # изменение списка мероприятий
            # request.data.pop("chats")
            for chats in chats_list:
                request.data.appendlist('chats', chats)
            request.data._mutable = False
            # print(request.data)
            return self.update(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введены не корректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class ProfileChatRemoveAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # удаление списка (или одного) мероприятий из профиля пользователя
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthorOrReadonlyUser,)

    def get(self, request, *args, **kwargs):
        try:
            Profile.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор профиля"},
                                    status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
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

            request.data._mutable = True
            # изменение списка мероприятий
            request.data.pop('chats')
            for chats in new_chats_list:
                request.data.appendlist('chats', chats)
            request.data._mutable = False
            # print(request.data)
            return self.update(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введены не корректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingChatAddAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # добавление чата для мероприятия
    model = Meeting
    serializer_class = MeetingChatCreateSerializer
    pagination_class = MeetingsPagination
    queryset = Meeting.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            Meeting.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор мероприятия"},
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
                MyCustomException(detail={"error": "Возникла ошибка во время создания чата"},
                                  status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise MyCustomException(detail={"error": "У этого мероприятия уже есть чат"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class VotingAPIView(generics.ListAPIView):
    # лист всех голосований
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()


class VotingCreateAPIView(generics.CreateAPIView):
    # создание голосования
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            author = Meeting.objects.get(id=kwargs['pk']).author

            if request.user.id == author.id:
                request.data._mutable = True
                request.data['meeting'] = kwargs['pk']
                request.data['author'] = request.user.id
                request.data._mutable = False
                return self.create(request, *args, **kwargs)
            else:
                raise MyCustomException(detail={"e": "Вы не являетесь создателем мероприятия"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор голосования"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class VotingDestroyAPIView(generics.DestroyAPIView):
    # удаление голосования
    model = Voting
    permission_classes = (IsAuthenticated,)  # изменить (может только автор)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            Voting.objects.get(pk=kwargs['pk'])
            return self.destroy(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор голосования"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldCreateAPIView(generics.CreateAPIView):
    # создание поля голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['vote'] = kwargs['pk']
        request.data['count_votes'] = 0
        request.data._mutable = False
        return self.create(request, *args, **kwargs)


class FieldRetrieveAPIView(generics.RetrieveAPIView):
    # просмотр информации поля голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            Field.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор поля для голосования"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldDestroyAPIView(generics.DestroyAPIView):
    # удаление поля для голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            Field.objects.get(pk=kwargs['pk'])
            return self.destroy(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор поля для голосования"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldAddVoteAPIView(generics.UpdateAPIView):
    # реализация голосования пользователем за данный вариант ответа
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            id_new_user = request.user.id
            field = Field.objects.get(id=kwargs['pk'])

            users_list = []
            for id_user in range(field.users.count()):
                users_list.append(field.users.values('id')[id_user]['id'])

            if id_new_user not in users_list:
                users_list.append(id_new_user)

            request.data._mutable = True
            if request.data.getlist('users'):
                request.data.pop('users')
            for i in range(len(users_list)):
                request.data.appendlist('users', users_list[i])
            request.data['count_votes'] = len(request.data.getlist('users'))
            request.data._mutable = False

            return self.update(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор поля для голосования"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldRemoveVoteAPIView(generics.UpdateAPIView):
    # реализация удаления голоса
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            id_user = request.user.id
            field = Field.objects.get(id=kwargs['pk'])

            users_list = []
            for user in range(field.users.count()):
                users_list.append(field.users.values('id')[user]['id'])

            if id_user in users_list:
                users_list.remove(id_user)

            request.data._mutable = True
            if request.data.getlist('users'):
                request.data.pop('users')
            for i in range(len(users_list)):
                request.data.appendlist('users', users_list[i])
            request.data['count_votes'] = len(users_list)
            request.data._mutable = False

            return self.update(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"error": "Введен неверный индификатор поля для голосования"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


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

        queryset = self.model.objects.filter(tags__in=list_tags_user, seats_bool=True, timetable__in=timetable_list)
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
