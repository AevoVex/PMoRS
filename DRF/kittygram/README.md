# Kittygram API

Итоговая версия учебного приложения: пользователи, коты, достижения, регистрация через Djoser, JWT, проверка владельца и валидаторы из страниц 135–152.

## Запуск

Из корня `D:\Dev\PMoRS\DRF`:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 kittygram
```

При отдельной установке из папки `kittygram`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001
```

Демопользователи: `alice`, `bob`; пароль обоих — `Demo-Learning-42!`. В базе два кота с одним общим достижением. Демопользователи не staff; для админки и редактирования общего справочника создайте суперпользователя через `manage.py createsuperuser`.

## Вход

| Метод | Адрес | Данные |
|---|---|---|
| POST | `/auth/users/` | username, password; регистрация |
| POST | `/auth/jwt/create/` | username, password; получить access и refresh |
| POST | `/auth/jwt/refresh/` | refresh; получить новый access |
| POST | `/auth/jwt/verify/` | token; проверить подпись/срок токена |
| GET | `/auth/users/me/` | Текущий пользователь по Bearer access |

Для запросов к данным: `Authorization: Bearer <access>`. Refresh не используется в этом заголовке. Создание пары токенов не отзывает старые токены. Истёкший, повреждённый или отсутствующий access даёт 401.

## Данные

| Метод | Адрес | Результат |
|---|---|---|
| GET | `/` | Ссылки на ресурсы API |
| GET / POST | `/cats/` | Краткий список / создание кота |
| GET / PUT / PATCH / DELETE | `/cats/{id}/` | Деталь / изменение / удаление |
| GET | `/cats/recent-white-cats/` | Пять последних белых котов, полные данные |
| POST | `/mycats/` | Создать кота через вьюсет из миксинов |
| GET | `/mycats/{id}/` | Прочитать кота; других действий здесь нет |
| GET | `/users/`, `/users/{id}/` | Публичные поля пользователей и имена их котов |
| GET / POST | `/achievements/` | Список / добавление достижения |
| GET | `/achievements/{id}/` | Достижение |
| PUT / PATCH / DELETE | `/achievements/{id}/` | Изменение/удаление общего достижения, только staff |

Пример создания кота:

```json
{
  "name": "Мурзик",
  "color": "Gray",
  "birth_year": 2024,
  "achievements": [{"achievement_name": "Уронил ёлку"}]
}
```

Обязательны name, color и birth_year. Достижения необязательны. Owner берётся из access-токена и отображается числовым id; переданный в JSON owner игнорируется. Age вычисляется автоматически. Деталь содержит поля `id`, `name`, `color`, `birth_year`, `achievements`, `owner`, `age`. Список содержит только `id`, `name`, `color`.

Цвет: `Gray`, `Black`, `White`, `Ginger`, `Mixed`; регистр значим. Год рождения должен быть не в будущем, возраст — меньше 40 лет по разнице годов. Имя ограничено 16 символами и не должно совпадать с кодом цвета. У одного владельца не может быть двух котов с одинаковым именем.

При PATCH можно отправить одно поле. При PUT обязательны name/color/birth_year. Для обоих методов отсутствие achievements сохраняет связи, `[]` очищает, массив новых объектов заменяет. Повторное название достижения переиспользует существующую запись. Только владелец меняет и удаляет кота, остальные вошедшие пользователи могут читать.

## Ранние уроки Kittygram

Это отдельный режим с `lessons.sqlite3`, а не открытая часть итогового JWT API. Из корня `DRF`:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 lessons
```

Он доступен на порту 8002. Роуты:

| Адрес | Учебный механизм |
|---|---|
| `/functions/cats/`, `/functions/cats/{id}/` | View-функции, сериализатор без id, CRUD |
| `/bulk/cats/` | GET списка, POST массива котов, `many=True` |
| `/apiview/cats/` | APIView, GET и POST |
| `/generics/cats/`, `/generics/cats/{id}/` | Дженерики с полным CRUD |
| `/cats/`, `/cats/{id}/` | ModelViewSet, Owner и вычисляемый возраст |
| `/owners/`, `/owners/{id}/` | CRUD владельцев, обратный список имён котов |
| `/hex-cats/`, `/hex-cats/{id}/` | Эксперимент hex → имя CSS-цвета |
| `/readonly-cats/`, `/readonly-cats/{id}/` | Низкоуровневый ViewSet, только чтение |

Для привязки раннего кота сначала создайте Owner с `first_name`, `last_name`, затем передайте коту `owner_id`. В ответе owner будет строкой. В `hex-cats` пример `"color": "#228B22"` сохранится как `forestgreen`. Только именованные CSS-цвета поддерживаются. Финальное API hex не принимает.

Для этапа обычных токенов из папки `kittygram`:

```powershell
python manage.py migrate --settings=config.lesson_settings
python manage.py createsuperuser --settings=config.lesson_settings
$env:KITTYGRAM_LESSON_TOKEN = '1'
python manage.py runserver 127.0.0.1:8002 --settings=config.lesson_settings
```

Получите Token через POST `/api-token-auth/` с учётными данными созданного пользователя. Передавайте `Authorization: Token <token>`. Чтобы вновь разрешить анонимный учебный режим, остановите сервер, выполните `Remove-Item Env:KITTYGRAM_LESSON_TOKEN` и запустите его заново. Удаляется только переменная окружения текущего терминала, данные остаются.

## Проверки

```powershell
python manage.py test cats --verbosity 2
python manage.py test lessons --settings=config.lesson_settings --verbosity 2
python manage.py check
python manage.py makemigrations --check --dry-run
```

`python` здесь означает интерпретатор активированного окружения. [HTTP-запросы](../requests/kittygram.http), [отчёт](../docs/REPORT.md), [демонстрация](../docs/DEMO.md).

## Docker-деплой API

В каталоге `kittygram` скопируйте `.env.example` в `.env`, задайте уникальные длинные значения `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD`, а в `DJANGO_ALLOWED_HOSTS` перечислите IP/домены VPS без схемы и портов. Например: `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,89.125.39.139`. Compose собирает официальный frontend из `../frontend` вместе с Nginx. Затем выполните:

```sh
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

Контейнер backend при запуске применяет миграции и собирает статику, Nginx публикует React SPA, API, админку и загруженные медиа на порту 80. База, медиа и статика хранятся в именованных Docker volumes. Не используйте учебные учетные данные и не коммитьте рабочий `.env`. HTTPS нужно отдельно настроить для домена (например, через внешний reverse proxy или сертификаты Let's Encrypt).

Frontend-статика доступна по `/static/` из образа gateway (`/srv/frontend/static/`). Django admin-статика доступна по `/static_backend/` из volume backend (`/srv/static/`). Это разделение важно: если направить `/static/` в backend volume, React `main.*.js/css` будет отвечать 404. После исправления конфигурации пересоберите gateway и очистите старый HTML-кэш браузера:

```sh
docker compose build --no-cache backend nginx
docker compose up -d --force-recreate nginx backend
docker compose exec backend python manage.py collectstatic --no-input
```

Проверка должна показать совпадение хешей в HTML и файлов внутри gateway:

```sh
docker compose exec nginx sh -c 'grep -oE "/static/(js|css)/[^"]+" /srv/frontend/index.html; find /srv/frontend/static -maxdepth 2 -type f | sort | head'
curl -I http://89.125.39.139/
```

В DevTools после деплоя включите Disable cache и сделайте hard reload. Старый `index.html` может продолжать ссылаться на уже несуществующие хеши даже после исправления Nginx.
