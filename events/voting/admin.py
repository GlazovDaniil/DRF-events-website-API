from django.contrib import admin
from .models import Field, Voting


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
    list_display = ('id', 'name', 'vote')
    list_filter = ('vote', 'users')
    fields = ['name', 'users', 'vote']
