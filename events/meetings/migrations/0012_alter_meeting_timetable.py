# Generated by Django 5.0.1 on 2024-03-22 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0011_chat_users_alter_chat_author_alter_field_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='timetable',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='meetings.timetable', verbose_name='Запись мероприятия'),
        ),
    ]