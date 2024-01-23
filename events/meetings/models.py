from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Meeting(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    info = models.TextField(max_length=500, null=True, blank=True)
    #profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
    telegram = models.CharField(max_length=50, null=True, blank=True)
    meetings = models.ManyToManyField(Meeting, related_name='profile_list', null=True, blank=True)
    def __str__(self):
        return str(self.user)