import datetime
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Tags(models.Model):
    tag_name = models.CharField(max_length=25,
                                help_text="Введите название тега",
                                verbose_name="Имя тега")

    def __str__(self):
        return self.tag_name


class Place(models.Model):
    office = models.CharField(max_length=50,
                              help_text="Введите место проведения мероприятия",
                              verbose_name="Место проведения мероприятия")
    max_participant = models.IntegerField(null=True, blank=True,
                                          help_text="Введите колличество мест",
                                          verbose_name="Колличество мест")

    def __str__(self):
        return self.office


class Meeting(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50,
                             help_text="Введите название мероприятия",
                             verbose_name="Название мероприятия")
    body = models.TextField(max_length=1000, null=True, blank=True,
                            help_text="Введите информацию о мероприятит",
                            verbose_name="Информация о мероприятии")
    place = models.ForeignKey(Place, on_delete=models.PROTECT,
                              help_text="Изменить место проведения мероприятия",
                              verbose_name="Место проведения мероприятия")
    event_date = models.DateField(help_text="Введите дату проведения мероприятия",
                                  verbose_name="Дата проведения мероприятия")
    start_time = models.TimeField(help_text="Введите время начала мероприятия",
                                  verbose_name="Время начала мероприятия")
    end_time = models.TimeField(help_text="Введите время окончания мероприятия",
                                verbose_name="Время окончания мероприятия")
    tags = models.ManyToManyField(Tags, related_name='meetings_list', blank=True,
                                  help_text="Выберите теги для мероприятия",
                                  verbose_name="Теги мероприятия")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания мероприятия")
    update_at = models.DateTimeField(auto_now=True,
                                     verbose_name="Дата последнего изменения мероприятия")

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    birthday = models.DateField(help_text="Укажите вашу дату рождения",
                                verbose_name="Дата рождения")
    info = models.TextField(max_length=500, null=True, blank=True,
                            help_text="Введите информацию о вас",
                            verbose_name="Информация о вас")
    # profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
    telegram = models.CharField(max_length=50, null=True, blank=True,
                                help_text="Напишите свой Telegtam",
                                verbose_name="Telegtam")
    meetings = models.ManyToManyField(Meeting, related_name='profile_list', blank=True,
                                      help_text="Выберете мероприятия, которые хотите поситить",
                                      verbose_name="Мероприятия")
    tags = models.ManyToManyField(Tags, blank=True,
                                  help_text="Выберите интересующие теги",
                                  verbose_name="Ваши теги")

    def __str__(self):
        return str(self.user)
