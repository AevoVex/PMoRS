# PMoRS Monorepo

Учебный monorepo с проектами Django REST Framework, Kittygram, React frontend, Telegram-ботом и вспомогательным Telegram API-клиентом.

## Состав

- `DRF/` — Yatube и Kittygram API, документация и проверки.
- `DRF/frontend/` — официальный React frontend Kittygram.
- `DRF/kittygram/` — production Docker Compose для Kittygram, PostgreSQL и Nginx.
- `kittybot/` — Telegram-бот с резервным Dog API.
- `client_api/` — минимальный Pyrogram-клиент для отправки сообщения в Saved Messages.
- `postman/` — коллекции API-запросов.

## Kittygram в Docker

1. Скопируйте `DRF/kittygram/.env.example` в `DRF/kittygram/.env`.
2. Заполните production-секреты и `DJANGO_ALLOWED_HOSTS`.
3. Запустите из `DRF/kittygram`:

```sh
docker compose up -d --build
```

Приложение будет доступно через Nginx на порту `80`. Подробности находятся в `DRF/kittygram/README.md`.

## Секреты

Секреты, Telegram credentials, MTProto session-файлы, базы данных, media и виртуальные окружения исключены из Git. Используйте только файлы `.env.example` как шаблоны.
