from rest_framework import serializers
from .models import Meeting, Profile, Tags, Place
from django.contrib.auth.models import User


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'tag_name')


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('office', 'max_participant')


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
    place = PlaceSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    profile_list = ProfileStartSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'event_date', 'start_time', 'end_time', 'place', 'created_at',
                  'update_at', 'tags', 'profile_list')


class MeetingCreateSerializer(serializers.ModelSerializer):
    profile_list = ProfileStartSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'event_date', 'start_time', 'end_time', 'place', 'created_at',
                  'update_at', 'tags', 'profile_list')
