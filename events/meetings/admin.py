from django.contrib import admin
from .models import Profile, Meeting, Tags, Place, Timetable, Voting, Field, Message, Chat


#admin.site.register(Profile)
#admin.site.register(Meeting)
admin.site.register(Tags)
#admin.site.register(Place)
#admin.site.register(Timetable)


class FieldInstanceInline(admin.TabularInline):
    model = Field
    fields = ['name']


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'meeting')
    list_filter = ('meeting',)
    fields = ['name', 'meeting']
    inlines = [FieldInstanceInline]


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'vote')
    list_filter = ('vote', 'users')
    fields = ['name', 'users', 'vote']


class MessageInstanceInline(admin.TabularInline):
    model = Message
    fields = ['user', 'message']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    fields = ['name', 'author']
    inlines = [MessageInstanceInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'user', 'message', 'created_at')
    list_filter = ('chat', 'user', 'created_at')
    fields = ['chat', 'user', 'message']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'info', 'birthday', 'telegram')
    list_filter = ('tags', 'birthday')
    fields = ['user', 'info', 'birthday', 'meetings', 'telegram', 'tags']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'body', 'seats', 'created_at', 'update_at')
    list_filter = ('tags', 'seats', 'created_at', 'update_at')
    fields = ['author', 'title', 'tags', 'body', 'seats', 'timetable']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('author', 'place', 'event_date', 'start_time', 'end_time')
    list_filter = ('place', 'event_date')
    fields = ['author', 'place', 'event_date', ('start_time', 'end_time')]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('office', 'max_participant')
    fields = ['office', 'max_participant']
