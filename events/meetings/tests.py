from django.test import TestCase
from django.contrib.auth.models import User
from .models import Meeting
import json

class MeetingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
    #Create a user
        testuser_1 = User.objects.create_user(
            username='testuser_1',
            password='abc123',)
        testuser_1.save()
    #Create a meeting
        test_meeting = Meeting.objects.create(
            author=testuser_1,
            title='Meeting title',
            body='Body content...',)
        test_meeting.save()
    def test_meeting_content(self):
        meeting = Meeting.objects.get(id=1)
        author = f'{meeting.author}'
        title = f'{meeting.title}'
        body = f'{meeting.body}'
        self.assertEqual(author, 'testuser_1')
        self.assertEqual(title, 'Meeting title')
        self.assertEqual(body, 'Body content...')

class TokenTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        testuser_2 = User.objects.create_user(
            username='testuser_2',
            password='abc123',)
        testuser_2.save()

        test_meeting = Meeting.objects.create(
            author= testuser_2,
            title='Meeting title',
            body='Body content...', )
        test_meeting.save()

    def test_get_token(self):
        response = self.client.post("/auth/token/login/", {"username": "testuser_2", "password": "abc123"})
        self.assertEqual(response.status_code, 200, "Токен должен быть успешно возвращен.")

        response_content = json.loads(response.content.decode('utf-8'))
        print("1")
        token = response_content["auth_token"]
        print(token)


        # The following request fails
        response = self.client.get("/meeting-api/v1/meeting/", {},
                                    HTTP_AUTHORIZATION='Token {0}'.format(token))

        response_content = json.loads(response.content.decode('utf-8'))
        print(response_content)

        self.assertEqual(response_content[0]['title'], "Meeting title",
                         "Пользователь должен иметь возможность получить доступ к этой конечной точке.")