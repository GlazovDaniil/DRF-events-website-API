from django.test import TestCase
from django.contrib.auth.models import User
from .models import Meeting, Place
import json

class MeetingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('==Тест создания мероприятия==')
    #Create a user
        testuser_1 = User.objects.create_user(
            username='testuser_1',
            password='abc123',)
        testuser_1.save()
        print('- Пользователь создан')
    #Create a meeting
        test_meeting = Meeting.objects.create(
            author=testuser_1,
            title='Meeting title',
            body='Body content...',)
        test_meeting.save()
        print('- Мероприятие создано')
    def test_meeting_content(self):
        meeting = Meeting.objects.get(id=1)
        author = f'{meeting.author}'
        title = f'{meeting.title}'
        body = f'{meeting.body}'
        self.assertEqual(author, 'testuser_1')
        self.assertEqual(title, 'Meeting title')
        self.assertEqual(body, 'Body content...')
        print('Конец теста\n')

class TokenTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('==Тест токена==')
        testuser_2 = User.objects.create_user(
            username='testuser_2',
            password='abc123',)
        testuser_2.save()
        print('- Пользователь создан')
        test_place = Place.objects.create(
            office='test_office'
        )
        print('- Место проведения создано')
        test_meeting = Meeting.objects.create(
            author= testuser_2,
            title='Meeting title',
            body='Body content...',
            place=test_place,)
        test_meeting.save()
        print('- Мероприятие создано')
    def test_get_token(self):
        response = self.client.post("/auth/token/login/", {"username": "testuser_2", "password": "abc123"})
        self.assertEqual(response.status_code, 200, "Токен должен быть успешно возвращен.")
        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["auth_token"]
        print('- Токен получен')

        # The following request fails
        response = self.client.get("/meeting-api/v1/meeting/", {},
                                    HTTP_AUTHORIZATION='Token {0}'.format(token))
        print('- Аунтефикация по токену успешна')
        response_content = json.loads(response.content.decode('utf-8'))
        print('- Декодирование JSON успешно')

        self.assertEqual(response_content[0]['title'], "Meeting title",
                         "Пользователь должен иметь возможность получить доступ к этой конечной точке.")
        print('Конец теста\n')