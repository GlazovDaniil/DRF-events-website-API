# Generated by Django 5.0.1 on 2024-03-13 14:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0010_meeting_seats_bool'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='users_now_in_chat', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chat',
            name='author',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='author_chat', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='field',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='fields', to=settings.AUTH_USER_MODEL, verbose_name='Список выбравших это поле'),
        ),
    ]
