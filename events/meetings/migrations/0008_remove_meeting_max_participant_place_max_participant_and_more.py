# Generated by Django 5.0.1 on 2024-01-30 11:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0007_remove_meeting_profile_list_profile_meetings_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='max_participant',
        ),
        migrations.AddField(
            model_name='place',
            name='max_participant',
            field=models.IntegerField(blank=True, help_text='Введите колличество мест', null=True, verbose_name='Колличество мест'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birthday',
            field=models.DateField(default=datetime.date(2024, 1, 30), help_text='Укажите вашу дату рождения', verbose_name='Дата рождения'),
        ),
    ]
