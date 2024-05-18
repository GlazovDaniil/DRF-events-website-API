# from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from .models import Meeting, Profile, Tags, Place, Timetable, Chat, Message, Voting, Field
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


UserModel = get_user_model()


@swagger_auto_schema(
        tags=["YourModel tag"],
        operation_id="Write here smth",
        operation_description="GET request",
    )
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
        )
        return user

    class Meta:
        ref_name = 'UserSerializer'
        model = UserModel
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'tag_name')


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = ('id', 'office', 'max_participant')


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ('id', 'author', 'event_date', 'start_time', 'end_time', 'used', 'place')


class TimetableListSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()

    class Meta:
        model = Timetable
        fields = ('id', 'author', 'event_date', 'start_time', 'end_time', 'used', 'place')


class TimetableForMeetingSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)

    class Meta:
        model = Timetable
        fields = ('place', 'event_date', 'start_time', 'end_time')


class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ('id', 'users', 'name', 'vote', 'count_votes')


class FieldVotingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ('id', 'name', 'users', 'count_votes')


class VotingSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=True, read_only=True, source='fields')

    class Meta:
        model = Voting
        fields = ('id', 'name', 'meeting', 'all_votes', 'field')


class ProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'user', 'birthday', 'info', 'phone', 'telegram', 'tags')


class ProfileStartSerializer(serializers.ModelSerializer):
    # используется для вывода списка участников мероприятий
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'info', 'telegram', 'phone')


class MeetingStartSerializer(serializers.ModelSerializer):
    # используется для вывода списка мероприятий в профиле пользователя
    timetable = TimetableForMeetingSerializer(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'seats', 'seats_bool', 'timetable', 'created_at', 'update_at')


# --------------------------!!!!!!!!!!--------------------------
class ProfileSerializer(serializers.ModelSerializer):
    # профили пользователей
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    meetings = MeetingStartSerializer(many=True, read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    my_meeting = MeetingStartSerializer(many=True, read_only=True, source='my_meetings')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'birthday', 'info', 'phone', 'telegram', 'tags', 'my_meeting', 'meetings', 'chats')


class ProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'birthday', 'info', 'phone', 'telegram', 'tags', 'chats')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        user.username = user_data.get('username', user.username)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.save()

        instance.phone = validated_data.get('phone', instance.phone)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.info = validated_data.get('info', instance.info)
        instance.telegram = validated_data.get('telegram', instance.telegram)
        print(instance.tags.all())
        instance.tags.set(validated_data.get('tags', instance.tags.all()))
        print(instance.tags.all())
        instance.chats.set(instance.chats.all())
        instance.save()

        return instance


class ProfileChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'chats')


class MeetingSerializer(serializers.ModelSerializer):
    # профили мероприятий
    timetable = TimetableForMeetingSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    # profile_list = ProfileStartSerializer(many=True, read_only=True)
    voting = VotingSerializer(many=True, read_only=True)
    seats_bool = serializers.BooleanField(read_only=True)
    # user_registered = serializers.BooleanField(initial=get_alternate_name, read_only=True, default=get_alternate_name)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'seats', 'seats_bool', 'created_at', 'update_at',
                  'timetable', 'tags', 'chat', 'voting')


class MeetingCreateSerializer(serializers.ModelSerializer):
    profile_list = ProfileStartSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'seats', 'seats_bool', 'timetable', 'created_at',
                  'update_at', 'tags', 'chat', 'profile_list')


class MeetingProfileListSerializer(serializers.ModelSerializer):
    profile_list = ProfileStartSerializer(many=True, read_only=True, source='meetings')

    class Meta:
        model = Meeting
        fields = ('id', 'profile_list')


class MeetingForUserAddMeetingSerializer(PrimaryKeyRelatedField, serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'


class UserAddMeetingSerializer(serializers.ModelSerializer):
    meetings = MeetingForUserAddMeetingSerializer(many=True, queryset=Meeting.objects.all())

    class Meta:
        model = Profile
        fields = ('id', 'meetings')


class ChatSerializer(serializers.ModelSerializer):
    profile_list = ProfileStartSerializer(many=True, read_only=True, source='chats')

    class Meta:
        model = Chat
        fields = ('id', 'name', 'author', 'created_at', 'profile_list')


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'chat', 'user', 'created_at', 'message')


class ChatMessageSerializer(serializers.ModelSerializer):
    message_list = MessageSerializer(many=True, read_only=True, source='messages')
    profile_list = ProfileStartSerializer(many=True, read_only=True, source='profile')

    class Meta:
        model = Chat
        fields = ('id', 'name', 'author', 'profile_list', 'message_list')


class MeetingChatCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = ('id', 'chat')
