from django.db import models
from events.meetings.models import Meeting, User


class Voting(models.Model):
    name = models.CharField(max_length=50, null=True,
                            help_text="Введите название голосования",
                            verbose_name="Название голосования")
    meeting = models.ForeignKey(Meeting, null=True, blank=True, related_name='voting', on_delete=models.CASCADE,
                                help_text="Выберите мероприятие",
                                verbose_name="Мероприятие")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    all_votes = models.IntegerField(default=0, verbose_name="Количество проголосовавших")

    def __str__(self):
        return self.name


class Field(models.Model):
    name = models.CharField(max_length=50,
                            help_text="Введите название поля",
                            verbose_name="Название поля")
    users = models.ManyToManyField(User, related_name='fields', blank=True,
                                   verbose_name="Список выбравших это поле")
    vote = models.ForeignKey(Voting, null=True, blank=True, related_name='fields', on_delete=models.CASCADE,
                             help_text="Выберите голосование",
                             verbose_name="Голосование")
    count_votes = models.IntegerField(default=0, help_text="Введите количество голосов",
                                      verbose_name="Количество голосов")

    def __str__(self):
        return self.name
