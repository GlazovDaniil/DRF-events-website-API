from rest_framework import permissions
from .models import Meeting, Profile


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
            if request.user == meeting.author:
                return True
        return obj.user == request.user


class PermissionCreateObjects(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user_id = request.user.id or ''
        profile = Profile.objects.get(user=user_id)
        if profile and profile.teacher_permission:
            return True
        return False
