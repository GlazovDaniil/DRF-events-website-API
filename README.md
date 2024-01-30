# DRF-events-website-API

## *Задачи*:
 - Создать группы пользователей: администратор, пользователь (организатор/участник)
 - "Умный календарь" записи в аудитории для проведения мероприятий
 - Теги как у мероприятий, так и у пользователей
 - Предпологаемый возраст для участников мероприятий

#
## **v0.0.7**

*Добавлено:*
- новые условия для проверки в автотесте токена
- множественные проверки в автотесте по созданию мероприятия
- доклад о ходе тестирования
- черновая функция записи мероприятия в офис
  ![image](https://github.com/GlazovDaniil/DRF-events-website-API/assets/78955311/86e46eb8-1bba-45f5-8862-6d5808f30bcf)


#
## **v0.0.6**

*Добавлено:*
- подробный показ информации о тегах в профиле и мероприятии и отображение места проведения
- сериализаторы для просмотра тегов и мест проведения мероприятий
- дополнен автотест токена, всвязи с добавлением новых полей и моделей
- документация для API (http://127.0.0.1:8000/swagger/)

#
## **v0.0.5**

*Добавлено:*
- сообщения о этапах автотестирования во время его работы
- язык интерфейса админ-панели и API изменен на русский
- две таблицы в БД: для тегов и места проведения мероприятий, и зарегестрированы в админ панели
- описания полей для админ-панели
- новые поля для профиля пользователя и мероприятий
- новые сериализаторы с учетом новых таблиц и полей

#
## **v0.0.4**

*Добавлено:*
- Новый уровень вложенности для профиля пользователя (рис.1)
- В Meeting API список пользователей-участников (рис.2)
  
![image](https://github.com/GlazovDaniil/DRF-events-website-API/assets/78955311/a55e004a-1af1-4fb5-95d4-0ba0fe805897)
рис.1

![image](https://github.com/GlazovDaniil/DRF-events-website-API/assets/78955311/463fe999-4ae3-46a6-a805-b0edafd28e94)
рис.2

#
## **v0.0.3**

*Добавлено:*
- авторизация пользователей двумя вариантами: с помощью сессии и токена
- автотест проверки получения и корректности авторизации по токену
- права доступа для пользователей (проссматривать информацию могут все авторизованные пользователи, а изменять только владельцы аккаунта/мероприятия к которым информация относится)
- возможность проссматривать информацию об определенном мероприятии
- возможность изменять/удалять информацию об определенном мероприятии будучи его создателем
- возможность проссматривать информацию о определенном пользователе (имя, фамилия, никнейм, биографию и мероприятия)
- возможность изменять/удалять информацию о определенном пользователе будучи этим пользователем

## **v0.0.2**

*Добавлено:*
- новый вариант представления пользователя, представляющий собой дополнение к базовому набору полей в Django
- возможность добавлять мероприятия
- возможность проссматривать список всех мероприятий
- возможность проссматривать список всех пользователей
- админ панель
- автотест создания пользователя и создания им мероприятия

## **v0.0.1**

*Добавлено:*
- базовые настройки Django, DRF
- представления
- модели данных мероприятия и пользователя, а так же связь между ними
