# Generated by Django 5.0.1 on 2024-03-09 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0009_alter_profile_birthday'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='seats_bool',
            field=models.BooleanField(default=True, null=True, verbose_name='Наличие свободных мест на мероприятии'),
        ),
    ]
