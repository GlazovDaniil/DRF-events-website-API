from rest_framework import serializers
from .models import Meeting, Profile, Tags, Place, Timetable
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

UserModel = get_user_model()


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
        model = UserModel
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'last_name', 'email')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'tag_name')


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = ('office', 'max_participant')


class TimetableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Timetable
        fields = '__all__'


class TimetableForMeetingSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)

    class Meta:
        model = Timetable
        fields = ('place', 'event_date', 'start_time', 'end_time')


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'birthday', 'info', 'telegram', 'tags')


class ProfileStartSerializer(serializers.ModelSerializer):
    # используется для вывода списка участников мероприятий
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'info')


class MeetingStartSerializer(serializers.ModelSerializer):
    # используется для вывода списка мероприятий в профиле пользователя
    class Meta:
        model = Meeting
        fields = ('author', 'title', 'body', 'created_at', 'update_at')


# --------------------------!!!!!!!!!!--------------------------
class ProfileSerializer(serializers.ModelSerializer):
    # профили пользователей
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    tags = TagsSerializer(many=True, read_only=True)
    meetings = MeetingStartSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'birthday', 'info', 'telegram', 'tags', 'meetings')


class MeetingSerializer(serializers.ModelSerializer):
    """
    def validate(self, data):
        if data['event_date'] < data['created_at']:
            raise serializers.ValidationError(
                {"event_date": "Введена уже прошедшая дата, выберите другую дату проведения"})
        return data
    """

    # профили мероприятий
    timetable = TimetableForMeetingSerializer( read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    #profile_list = ProfileStartSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'seats', 'timetable', 'created_at',
                  'update_at', 'tags')


class MeetingCreateSerializer(serializers.ModelSerializer):
    profile_list = ProfileStartSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'seats', 'timetable', 'created_at',
                  'update_at', 'tags', 'profile_list')


class MeetingProfileListSerializer(serializers.ModelSerializer):
    profile_list = ProfileStartSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'profile_list')
