from rest_framework import serializers
from .models import Meeting, AllUser
class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ('author', 'title', 'body', 'created_at', 'update_at')

class AllUserSerialize(serializers.ModelSerializer):
    class Meta:
        model = AllUser
        fields = ('id', 'first_name', 'last_name', 'info', 'meetings')