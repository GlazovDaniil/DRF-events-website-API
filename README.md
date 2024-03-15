# DRF-events-website-API
## *📊Диаграмма URLs📊*:

![URLs 0-2-0](https://github.com/GlazovDaniil/DRF-events-website-API/assets/78955311/0f266538-8740-4ac7-818c-a26ec1211232)



## *📜Задачи📜*:
 - ✅/⛔ Создать группы пользователей: администратор, пользователь (организатор/участник) 
 - ✅"Умный календарь" записи в аудитории для проведения мероприятий 
 - ✅ Теги как у мероприятий, так и у пользователей 
 - ⛔ Предпологаемый возраст для участников мероприятий 
 - ✅ Голосования в мероприятиях 
 - ✅/⛔ Чат мероприятия и в принципе чаты 

#
## **v0.2.5**

*Для применения изменений:*
- pip install -r requirements.txt
- python manage.py makemigrations (в терминале)

*Начата работа с веб-сокетом*

#
## **v0.2.4**

*Добавлено:*
- 'user/recommended_meetings/' рекомендуемые мероприятия для зарегистрированного пользователя

#
## **v0.2.3**

*Добавлено:*
- маркер наличия свободных мест на мероприятии
- счетчик свободных мест на мероприятии

#
## **v0.2.2.1**

*Добавлено:*
- метод для отмены поставленного голоса

#
## **v0.2.2**

*Для применения изменений:*
- python manage.py makemigrations (в терминале)

*Добавлено:*
- вывод информации о поле
- произведена оптимизация ряда методов
- проверка на автора мероприятия при создании в нем голосования (может создавать только автор)
  
#
## **v0.2.1**
*Для применения изменений:*
- python manage.py migrate (в терминале)

*Добавлено:*
- новые модели в админ панель (Chats, Messages, Votings, Fields)
- поле автора записи в модель расписания (Timetable)

#
## **v0.2.0**
*Для применения изменений:*
- python manage.py migrate (в терминале)

*Добавлено:*
- голосования для мероприятий (для одного мероприятия может быть создано несколько голосований)

#
## **v0.1.8**

*Добавлено:*
- теперь при создании чата или мероприятия они добавляются в профиль автора (он автоматически становится их участником)
- добавление чата для мероприятия (сначала создается без чата), он так же добавляется в профиль к автору

#
## **v0.1.7**

*Для применения изменений:*
- удалить файл db.sqlite3
- python manage.py makemigrations (в терминале)
- python manage.py migrate (в терминале)

*Добавлено:*
- Чат как для мероприятий, так и для пользователей (возможность добавлять чаты и выходить из них)

#
## **v0.1.6.2**

*Добавлено:*
- получение списка тегов (http://127.0.0.1:8000/meeting-api/v1/places_list/)
- получение списка мест проведения (http://127.0.0.1:8000/meeting-api/v1/tags_list/)

#
## **v0.1.6**

*Добавлено:*
- функции добавления в профиль (http://127.0.0.1:8000/meeting-api/v1/user_add_meeting/{id}/) и удаления из профиля (http://127.0.0.1:8000/meeting-api/v1/user_remove_meeting/{id}/) мероприятий пользователем

**Info:** Можно передавать как ключи по отдельности, так и их список list[str]


#
## **v0.1.5.2**

*Добавлено:*
- Получение информации о пользователе по токену (http://127.0.0.1:8000/meeting-api/v1/uset_by_token/)

#
## **v0.1.5.1**

*Исправлено:*
- работа swagger
- мелкие исправления

#
## **v0.1.5**

*Добавлено:*
- регистрация пользователей:
	1) регистрация нового пользователя и создание его аккаунта (http://127.0.0.1:8000/meeting-api/v1/user_register/)
	2) заполнение доп информации профиля (http://127.0.0.1:8000/meeting-api/v1/user_create/)
- возможность обновления (перезаписи мероприятия на друугое время и дату) зписи в Timetable

#
## **v0.1.4.1**

*Добавлено:*
- новый вид админ панели, переопределена регистрация моделей данных
- фильтры для почти всех моделей

#
## **v0.1.4**

*Для применения изменений:*
- удалить файл db.sqlite3
- python manage.py migrate (в терминале)

*Добавлено:*
- частично изменена структура базы данных
- проверка свободен ли кабинет при записи в него
- автоматическое заполнение поля "автор" по информации о пользователе, отправившем запрос
- возможность вписывать как в ручную, количество свободных мест на мероприятии, так и автоматическое заполнение этого поля исходя из информации о месте проведения из базы данных

#
## **v0.1.3**

*Добавлено:*
- отдельные классы пагинации для списка мероприятий и их участников
- мелкие исправления

#
## **v0.1.2.1**

*Добавлено:*
- requirements.txt со списком всех необходимых библеотек для запуска проекта
- представление для прсмотра списка пользователей, зарегестрированных на мероприятии, по id мероприятия

#
## **v0.1.2**

*Добавлено:*
- изменение прав доступа для meeting-api/v1/meeting

#
## **v0.1.1**

*Добавлено:*
- изменения настроек конфигурации сервера

#
## **v0.1.0**, **v0.0.10**

*Для применения изменений:*
- python manage.py migrate (в терминале)

*Добавлено:*
- теперь при создании мероприятия проверяется, свободен ли кабинет на это время, если нет, то выдается ошибка, иначе запись добавляется
- при удалении мероприятия и удаляется запись из расписания

#
## **v0.0.9**

*Добавлено:*
- пагинация вывода записей

#
## **v0.0.8**

*Добавлено:*
- начата работа по "умному календарю"
- переработаны и обновлены ряд представлений и сериализаторов
- разделен вывод информации о мероприятиях и их создание на отдельные URL адреса

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
- документация для API:
(http://127.0.0.1:8000/swagger/)
(http://127.0.0.1:8000/redoc/)

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
