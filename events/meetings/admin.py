from django.contrib import admin
from .models import Profile, Meeting, Tags, Place, Timetable

admin.site.register(Profile)
admin.site.register(Meeting)
admin.site.register(Tags)
admin.site.register(Place)
admin.site.register(Timetable)
