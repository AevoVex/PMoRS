# Yatube API

REST API учебного проекта Yatube для публикаций, групп, комментариев и подписок на авторов.

## Установка

Из корня `D:\Dev\PMoRS\DRF`:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 yatube
```

При отдельной установке из папки `yatube`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Команда `seed_demo` создаёт обычных пользователей `alice` и `bob` с паролем `Demo-Learning-42!`, группу `cats` и две публикации. Повторный вызов не сбрасывает пароли. Другой пароль для новых демопользователей: `manage.py seed_demo --password "Your-local-password"`.

## Примеры запросов к API

| Метод | Адрес | Что делает |
|---|---|---|
| POST | `/api/v1/api-token-auth/` | Получить Token по username/password |
| GET | `/api/v1/posts/` | Все публикации, сначала новые |
| POST | `/api/v1/posts/` | Создать публикацию текущего пользователя |
| GET | `/api/v1/posts/{id}/` | Получить одну публикацию |
| PUT | `/api/v1/posts/{id}/` | Обновить публикацию; text обязателен |
| PATCH | `/api/v1/posts/{id}/` | Изменить переданные поля |
| DELETE | `/api/v1/posts/{id}/` | Удалить свою публикацию |
| GET | `/api/v1/groups/` | Посмотреть группы и их slug |
| GET | `/api/v1/follow/` | Список подписок текущего пользователя |
| POST | `/api/v1/follow/` | Подписаться на автора по username |
| POST | `/api/v1/jwt/create/` | Получить JWT-токены |

Во всех запросах к данным нужен заголовок `Authorization: Token <token>`. Регистрация через API здесь не требуется заданием: пользователей создают через `seed_demo`, админку либо Django shell. Для админки выполните `manage.py createsuperuser`.

Получение токена:

```json
{"username": "alice", "password": "Demo-Learning-42!"}
```

Подписка на автора:

```json
{"following": "bob"}
```

Поиск среди своих подписок выполняется параметром `?search=bob`.

Создание публикации:

```json
{"text": "Мой кот любит спать", "group": "cats"}
```

Ответ включает `id`, `text`, `author` (id пользователя), `image` (URL либо null), `pub_date`, `group` (slug либо null), `character_quantity`. Клиент не задаёт автора, дату и число символов. Значение `group: null` убирает группу, отсутствие `group` в обновлении сохраняет прежнюю. Image отправляется файлом в `multipart/form-data`; обычный путь к файлу в JSON не является загрузкой.

Получение чужих публикаций разрешено после входа, изменение и удаление возвращают 403. Несуществующий id даёт 404, пустой текст/неизвестная группа — 400. Список возвращается массивом без пагинации, как в заданиях.

## Промежуточные решения

Из папки `yatube`, используя Python своего окружения:

```powershell
$env:YATUBE_STAGE = 'apiview'
python manage.py runserver 127.0.0.1:8003 --settings=config.lesson_settings
```

Для урока с роутером замените `apiview` на `viewset`. Оба режима используют `/api/v1/posts/`, обычный Token и ту же базу. В APIView доступны GET/POST списка, в ModelViewSet — весь CRUD. Чтобы вернуться к финальному API, запускайте без `--settings=config.lesson_settings`.

Первый сериализатор из страницы 29 находится в [lessons/serializers.py](lessons/serializers.py), класс `InitialPostSerializer`: имя отличается от финального, чтобы обе версии можно было импортировать и сравнивать. APIView/ModelViewSet используют уже финальные поля и защиту авторства; отключать авторизацию ради демонстрации не нужно.

## Проверка и навигация

```powershell
python manage.py test posts --verbosity 2
python manage.py check
python manage.py makemigrations --check --dry-run
```

Все команды `python` предполагают активированное окружение; вместо него можно указывать абсолютный путь к интерпретатору. [Готовые HTTP-запросы](../requests/yatube.http), [объяснение решений](../docs/REPORT.md), [сценарий защиты](../docs/DEMO.md).
