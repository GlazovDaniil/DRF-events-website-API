# Generated by Django 5.0.1 on 2024-02-20 20:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0003_remove_meeting_voting_voting_voting'),
    ]

    operations = [
        migrations.RenameField(
            model_name='voting',
            old_name='voting',
            new_name='meeting',
        ),
    ]
