from rest_framework import permissions
from .models import Meeting


class IsAuthorOrReadonlyAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthorOrReadonlyUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAuthorMeetingOrUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.query_params.get("meeting_id"):
            meeting_id = request.query_params.get("meeting_id")
            meeting = Meeting.objects.get(id=meeting_id)
            if request.user in meeting.author:
                return True
        return obj.user == request.user
