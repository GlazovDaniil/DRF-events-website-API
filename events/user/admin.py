from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'info', 'birthday', 'telegram')
    list_filter = ('tags', 'birthday')
    fields = ['user', 'info', 'birthday', 'meetings', 'telegram', 'tags']
