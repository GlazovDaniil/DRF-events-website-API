from rest_framework import serializers
from .models import Meeting, Profile
from django.contrib.auth.models import User
class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('author', 'title', 'body', 'created_at', 'update_at')

class UserSerializer(serializers.ModelSerializer):
    #profiles = serializers.SerializerMethodField(ProfileSerializer)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    #def get_profiles(self, obj):
    #    return obj.profiles

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ('user', 'username', 'first_name', 'last_name', 'info', 'meetings')
