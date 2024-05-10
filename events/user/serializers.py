from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from .models import Profile, Meeting
from events.meetings.serializers import MeetingStartSerializer, TagsSerializer, MeetingForUserAddMeetingSerializer
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


class UserAddMeetingSerializer(serializers.ModelSerializer):
    meetings = MeetingForUserAddMeetingSerializer(many=True, queryset=Meeting.objects.all())

    class Meta:
        model = Profile
        fields = ('id', 'meetings')
