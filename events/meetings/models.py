from django.db import models
from django.contrib.auth.models import User

class Meeting(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class AllUser(models.Model):
    id = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    info = models.CharField(max_length=500, null=True, blank=True)
    meetings = models.ManyToManyField(Meeting, null=True, blank=True)
    def __str__(self):
        return self.last_name + " " + self.first_name


