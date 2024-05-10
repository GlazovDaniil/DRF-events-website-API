from rest_framework import generics, status, response
from rest_framework.permissions import IsAuthenticated
from events.meetings.castom_exeptions import MyCustomException, Http200Exception
from .models import Voting, Field
from events.meetings.models import Meeting
from .serializers import VotingSerializer, FieldVotingSerializer, FieldSerializer


class VotingAPIView(generics.ListAPIView):
    """Лист всех голосований"""
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()


class VotingRenameAPIView(generics.UpdateAPIView):
    """Переименование голосования"""
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class VotingCreateAPIView(generics.CreateAPIView):
    # создание голосования
    model = Voting
    permission_classes = (IsAuthenticated,)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def post(self, request, *args, **kwargs):
        """Создание голосования"""
        try:
            author = Meeting.objects.get(id=kwargs['pk']).author

            if request.user.id == author.id:
                if type(request.data) is dict:
                    request.data['meeting'] = kwargs['pk']
                    request.data['author'] = request.user.id
                else:
                    request.data._mutable = True
                    request.data['meeting'] = kwargs['pk']
                    request.data['author'] = request.user.id
                    request.data._mutable = False
            else:
                raise MyCustomException(detail="Вы не являетесь создателем мероприятия",
                                        status_code=status.HTTP_400_BAD_REQUEST)
        except:
            raise MyCustomException(detail="Введен неверный индификатор голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.create(request, *args, **kwargs)


class VotingDestroyAPIView(generics.DestroyAPIView):
    # удаление голосования
    model = Voting
    permission_classes = (IsAuthenticated,)  # изменить (может только автор)
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()

    def delete(self, request, *args, **kwargs):
        """Удаление голосования"""
        try:
            Voting.objects.get(pk=kwargs['pk'])
            return self.destroy(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldCreateAPIView(generics.CreateAPIView):
    # создание поля голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    @staticmethod
    def create_fields_from_list(vote, names):
        """Создание полей из списка"""
        for i in names:
            name = ' '.join(i.split('_'))
            field = Field.objects.create(
                name=name,
                vote=Voting.objects.get(id=vote),
                count_votes=0,
            )
            field.save()

    def post(self, request, *args, **kwargs):
        """Создание поля в голосовании"""
        try:
            if type(request.data) is dict:
                names = request.data['name'].split(' ')
                self.create_fields_from_list(kwargs['pk'], names)
                return response.Response(status=status.HTTP_200_OK)
            else:
                request.data._mutable = True
                request.data['vote'] = kwargs['pk']
                request.data['count_votes'] = 0
                request.data._mutable = False
                return self.create(request, *args, **kwargs)
        except Exception as excep:
            raise MyCustomException(detail=f"{excep}",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldRetrieveAPIView(generics.RetrieveAPIView):
    # просмотр информации поля голосования
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def get(self, request, *args, **kwargs):
        """Получение поля голосования"""
        try:
            Field.objects.get(pk=kwargs['pk'])
            return self.retrieve(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldDestroyAPIView(generics.DestroyAPIView):
    """Удаление поля для голосования"""
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldSerializer
    queryset = Field.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            field = Field.objects.get(pk=kwargs['pk'])
            vote = Voting.objects.get(id=field.vote)
            vote.all_votes -= field.count_votes
            vote.save()
            return self.destroy(request, *args, **kwargs)
        except:
            raise MyCustomException(detail="Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)


class FieldRenameAPIView(generics.UpdateAPIView):
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def patch(self, request, *args, **kwargs):
        """Для изменения имени"""
        return self.partial_update(request, *args, **kwargs)


class FieldAddVoteAPIView(generics.UpdateAPIView):
    # реализация голосования пользователем за данный вариант ответа
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            id_new_user = request.user.id
            field = Field.objects.get(id=kwargs['pk'])

            users_list = []
            count_users = field.users.count()
            for id_user in range(count_users):
                users_list.append(field.users.values('id')[id_user]['id'])

            if id_new_user not in users_list:
                users_list.append(id_new_user)
                count_users += 1
                vote = Voting.objects.get(id=field.vote.id)
                vote.all_votes += 1
                vote.save()

            if type(request.data) is dict:
                request.data['users'] = users_list
                request.data['count_votes'] = count_users
            else:
                request.data._mutable = True
                if request.data.getlist('users'):
                    request.data.pop('users')
                for i in range(count_users):
                    request.data.appendlist('users', users_list[i])
                request.data['count_votes'] = count_users
                request.data._mutable = False

        except Exception as e:
            raise MyCustomException(detail=f"Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


class FieldRemoveVoteAPIView(generics.UpdateAPIView):
    # реализация удаления голоса
    model = Field
    permission_classes = (IsAuthenticated,)
    serializer_class = FieldVotingSerializer
    queryset = Field.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            id_user = request.user.id
            field = Field.objects.get(id=kwargs['pk'])

            users_list = []
            count_users = field.users.count()
            for user in range(count_users):
                users_list.append(field.users.values('id')[user]['id'])

            if id_user in users_list:
                users_list.remove(id_user)
                count_users -= 1
                vote = Voting.objects.get(id=field.vote.id)
                vote.all_votes -= 1
                vote.save()
            else:
                raise MyCustomException(detail="Вы не голосовали в этом голосовании",
                                        status_code=status.HTTP_400_BAD_REQUEST)

            if type(request.data) is dict:
                request.data['users'] = users_list
                request.data['count_votes'] = count_users
            else:
                request.data._mutable = True
                if request.data.getlist('users'):
                    request.data.pop('users')
                for i in range(count_users):
                    request.data.appendlist('users', users_list[i])
                request.data['count_votes'] = count_users
                request.data._mutable = False
        except:
            raise MyCustomException(detail="Введен неверный индификатор поля для голосования",
                                    status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return self.update(request, *args, **kwargs)


