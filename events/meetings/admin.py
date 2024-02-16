from django.contrib import admin
from .models import Profile, Meeting, Tags, Place, Timetable


#admin.site.register(Profile)
#admin.site.register(Meeting)
admin.site.register(Tags)
#admin.site.register(Place)
#admin.site.register(Timetable)


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
    list_display = ('place', 'event_date', 'start_time', 'end_time')
    list_filter = ('place', 'event_date')
    fields = ['place', 'event_date', ('start_time', 'end_time')]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('office', 'max_participant')
    fields = ['office', 'max_participant']
