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
from .permissions import IsAuthorOrReadonlyMeeting, IsAuthorOrReadonlyProfile
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
            user = User.objects.get(id=request.user.id)
            profile_author = Profile.objects.get(user=user.id)

            request.data._mutable = True
            request.data['author'] = profile_author.id
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
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)
        meeting = Meeting.objects.get(title=serializer.data['title'],
                                      author=serializer.data['author'],
                                      created_at=serializer.data['created_at'])
        profile_author.meetings.add(meeting)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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


class ChatAPIView(generics.ListAPIView):
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
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)
        # profile_author.chats.add()

        request.data._mutable = True
        request.data['author'] = profile_author.id
        request.data._mutable = False
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # автодобавление автора в участники чата
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)
        chat = Chat.objects.get(name=serializer.data['name'],
                                author=serializer.data['author'],
                                created_at=serializer.data['created_at'])
        profile_author.chats.add(chat)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageCreateAPIView(generics.CreateAPIView):
    model = Message
    # permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)

        request.data._mutable = True
        request.data['chat'] = str(kwargs['pk'])
        request.data['user'] = profile_author.id
        request.data._mutable = False
        return self.create(request, *args, **kwargs)


class MessagesAPIView(generics.ListAPIView):
    model = Message
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    pagination_class = MeetingsPagination
    filter_backends = [OrderingFilter]
    ordering = ['-created_at']


class ChatMessageAPIView(generics.RetrieveAPIView):
    model = Chat
    pagination_class = MeetingsPagination
    # permission_classes = (IsAuthenticated,)
    serializer_class = ChatMessageSerializer
    queryset = Chat.objects.all()


class ProfileChatAddAPIView(generics.UpdateAPIView, generics.RetrieveAPIView):
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthorOrReadonlyProfile,)

    def put(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)
        profile = Profile.objects.get(id=request.user.id)
        kwargs['pk'] = profile_author
        # print(profile.chats.values())
        try:
            profile = Profile.objects.get(id=request.user.id)
            chats_list = []
            for i in range(profile.chats.count()):
                chats_list.append(str(profile.chats.values()[i]["id"]))
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
    model = Profile
    queryset = Profile.objects.all()
    serializer_class = ProfileChatSerializer
    permission_classes = (IsAuthorOrReadonlyProfile,)

    def put(self, request, *args, **kwargs):
        # на честность отправителя :)
        user = User.objects.get(id=request.user.id)
        profile_author = Profile.objects.get(user=user.id)
        kwargs['pk'] = profile_author

        try:
            profile = Profile.objects.get(id=request.user.id)
            chats_list = []
            for i in range(profile.chats.count()):
                chats_list.append(str(profile.chats.values()[i]["id"]))
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
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()


class VotingCreateAPIView(generics.CreateAPIView):
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['meeting'] = kwargs['pk']
        request.data._mutable = False
        return self.create(request, *args, **kwargs)


class VotingDestroyAPIView(generics.DestroyAPIView):
    model = Voting
    permission_classes = (IsAuthenticated,)  # изменить (может только автор)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()


class FieldCreateAPIView(generics.CreateAPIView):
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['vote'] = kwargs['pk']
        request.data._mutable = False
        return self.create(request, *args, **kwargs)


class FieldDestroyAPIView(generics.DestroyAPIView):
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class FieldAddVoteAPIView(generics.UpdateAPIView):
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        id_user = Profile.objects.get(user=request.user).id

        request.data._mutable = True
        request.data.appendlist('users', id_user)
        request.data._mutable = False
        return self.update(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/api-authlogin/')


def accounts_profile_redirect(request):
    return HttpResponseRedirect('/meeting-api/v1/users/')
