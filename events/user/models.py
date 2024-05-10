from django.db import models
from events.meetings.models import Meeting, User, Tags, Chat  # при реализации чата убрать его модель


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, help_text="Укажите вашу дату рождения",
                                verbose_name="Дата рождения")
    info = models.TextField(max_length=500, null=True, blank=True,
                            help_text="Введите информацию о вас",
                            verbose_name="Информация о вас")
    # profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
    telegram = models.CharField(max_length=50, null=True, blank=True,
                                help_text="Напишите свой Telegtam",
                                verbose_name="Telegtam")
    phone = models.CharField(max_length=11, null=True, help_text="Напишите свой номер телефона",
                                verbose_name="Ваш номер телефона")
    meetings = models.ManyToManyField(Meeting, related_name='meetings', blank=True,
                                      help_text="Выберете мероприятия, которые хотите поситить",
                                      verbose_name="Мероприятия")
    tags = models.ManyToManyField(Tags, blank=True,
                                  help_text="Выберите интересующие теги",
                                  verbose_name="Ваши теги", related_name='tags')
    chats = models.ManyToManyField(Chat, related_name='profile', blank=True,
                                   help_text="Выберете чаты",
                                   verbose_name="Ваши чаты")
