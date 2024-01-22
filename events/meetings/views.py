from .models import AllUser, Meeting
from .serializers import MeetingSerializer, AllUserSerialize
from rest_framework import generics


class MeetingAPIView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class AllUserAPIView(generics.ListAPIView):
    queryset = AllUser.objects.all()
    serializer_class = AllUserSerialize