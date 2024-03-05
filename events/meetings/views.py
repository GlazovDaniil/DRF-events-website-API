import datetime
from django.http import HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from .models import Profile, Meeting, Timetable, Place, Tags, Chat, Message, User, Voting, Field
from .serializers import (MeetingSerializer, ProfileSerializer, MeetingCreateSerializer, MeetingProfileListSerializer,
                          TimetableSerializer, UserSerializer, ProfileCreateSerializer, UserAddMeetingSerializer,
                          TagsSerializer, PlaceSerializer, ChatSerializer, MessageSerializer, ChatMessageSerializer,
                          ProfileChatSerializer, MeetingChatCreateSerializer, VotingSerializer, FieldSerializer,
                          FieldVotingSerializer)
from .permissions import IsAuthorOrReadonlyAuthor, IsAuthorOrReadonlyUser
from rest_framework import generics, views, response
from django.contrib.auth import logout
from .pagination import MeetingProfilesPagination, MeetingsPagination
from .castom_exeptions import MyCustomException
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.filters import OrderingFilter


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
            # user = User.objects.get(id=request.user.id)
            # profile_author = Profile.objects.get(user=user.id)

            request.data._mutable = True
            request.data['author'] = request.user.id
            request.data._mutable = False

            return self.create(request, *args, **kwargs)
        except:
            raise MyCustomException(detail={"Error": "Введены некорректные данные"},
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
        print(request.data)
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
                request.data._mutable = True
                request.data['author'] = request.user.id
                request.data._mutable = False
                return self.create(request, *args, **kwargs)
            else:
                raise MyCustomException(detail={"Error": "Невозможно записать на эту дату и время, так как они заняты"},
                                        status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise MyCustomException(detail={"Error": "Некорректно введены дата и время"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class TimetableUpdate(generics.UpdateAPIView):
    # изменение мероприятия в расписание
    permission_classes = (IsAuthorOrReadonlyAuthor,)
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
        profile = Profile.objects.get(user=request.user.id)
        print(profile.id)
        data = {
            "id": str(request.user.id),
            "username": str(request.user.username),
            "first_name": str(request.user.first_name),
            "last_name": str(request.user.last_name),
            "id_profile": str(profile.id),
        }
        return response.Response(data, status=status.HTTP_201_CREATED)


class UserAddMeetingAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # добавляет выбранные мероприятия из списка мероприятий пользователя
    model = Profile
    permission_classes = (IsAuthenticated,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            kwargs['pk'] = request.user.id
            # print(f'Получили {request.data}')
            profile = Profile.objects.get(user=request.user.id)

            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values()[i]["id"]))

            if type(request.data) is dict:
                meetings_list.append(str(request.data['meetings']))
                request.data['meetings'] = meetings_list

            else:
                add_id_meeting = request.data.getlist('meetings')

                for add_id in add_id_meeting:
                    meetings_list.append(add_id)
                # print(meetings_list)

                request.data._mutable = True
                request.data.pop("meetings")
                for meeting in meetings_list:
                    request.data.appendlist('meetings', meeting)
                request.data._mutable = False
            # print(f'Записали {add_id_meeting}')

            return self.update(request, *args, **kwargs)
        except Exception as e:
            raise MyCustomException(detail={"Error": e.__str__()},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class UserRemoveMeetingAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # убирает выбранные мероприятия из списка мероприятий пользователя
    model = Profile
    permission_classes = (IsAuthorOrReadonlyUser,)
    serializer_class = UserAddMeetingSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        try:
            # print(request.data["meetings"])
            profile = Profile.objects.get(user=request.user.id)
            meetings_list = []
            for i in range(profile.meetings.count()):
                meetings_list.append(str(profile.meetings.values('id')[i]["id"]))

            if type(request.data) is dict:
                new_meetings_list = list(set(meetings_list) - set(str(request.data['meetings'])))
                request.data['meetings'] = new_meetings_list
            else:
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

        request.data._mutable = True
        request.data['chat'] = str(kwargs['pk'])
        request.data['user'] = request.user.id
        request.data._mutable = False
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


class ProfileChatAddAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # добавление списка (или одного) мероприятий в профиль пользователя
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthenticated,)

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
            raise MyCustomException(detail={"Error": "Введены не корректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class ProfileChatRemoveAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # удаление списка (или одного) мероприятий из профиля пользователя
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthorOrReadonlyUser,)

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
            raise MyCustomException(detail={"Error": "Введены не корректные данные"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class MeetingChatAddAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    # добавление чата для мероприятия
    model = Meeting
    serializer_class = MeetingChatCreateSerializer
    pagination_class = MeetingsPagination
    queryset = Meeting.objects.all()

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
                MyCustomException(detail={"Error": "Возникла ошибка во время создания чата"},
                                  status_code=status.HTTP_400_BAD_REQUEST)
        else:
            raise MyCustomException(detail={"Error": "У этого мероприятия уже есть чат"},
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
        author = Meeting.objects.get(id=kwargs['pk']).author

        if request.user.id == author.id:
            request.data._mutable = True
            request.data['meeting'] = kwargs['pk']
            request.data['author'] = request.user.id
            request.data._mutable = False
            return self.create(request, *args, **kwargs)
        else:
            raise MyCustomException(detail={"Error": "Вы не являетесь создателем мероприятия"},
                                    status_code=status.HTTP_400_BAD_REQUEST)


class VotingDestroyAPIView(generics.DestroyAPIView):
    # удаление голосования
    model = Voting
    permission_classes = (IsAuthenticated,)  # изменить (может только автор)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()


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


class FieldDestroyAPIView(generics.DestroyAPIView):
    # удаление поля для голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class FieldAddVoteAPIView(generics.UpdateAPIView):
    # реализация голосования пользователем за данный вариант ответа
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
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


class FieldRemoveVoteAPIView(generics.UpdateAPIView):
    # реализация удаления голоса
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/api-authlogin/')


def accounts_profile_redirect(request):
    return HttpResponseRedirect('/meeting-api/v1/users/')
