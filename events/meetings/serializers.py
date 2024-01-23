from rest_framework import serializers
from .models import Meeting, Profile
from django.contrib.auth.models import User

"""

class MeetingSerializer(serializers.ModelSerializer):
    profils = serializers.PrimaryKeyRelatedField(queryset='',many=True, read_only=True)
    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'created_at', 'update_at', 'profils')

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    meetings = MeetingSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'info', 'meetings')
"""

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

    meetings = MeetingStartSerializer(many=True, read_only=True)
    class Meta:
        model = Profile
        fields = ('id', 'username', 'first_name', 'last_name', 'info', 'meetings')

class MeetingSerializer(serializers.ModelSerializer):
    # профили мероприятий
    profile_list = ProfileStartSerializer(many=True, read_only=True)
    class Meta:
        model = Meeting
        fields = ('id', 'author', 'title', 'body', 'created_at', 'update_at', 'profile_list')
        

