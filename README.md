# PMoRS Monorepo

Учебный monorepo с проектами Django REST Framework, Kittygram, React frontend, Telegram-ботом и вспомогательным Telegram API-клиентом.

## Состав

- `DRF/` — Yatube API, документация и проверки.
- `kittygram/` — Kittygram backend, frontend, gateway и Docker Compose.
- `kittybot/` — Telegram-бот с резервным Dog API.
- `client_api/` — минимальный Pyrogram-клиент для отправки сообщения в Saved Messages.
- `postman/` — коллекции API-запросов.

## Kittygram в Docker

1. Скопируйте `kittygram/.env.example` в `kittygram/.env`.
2. Заполните production-секреты и `DJANGO_ALLOWED_HOSTS` (IP без `http://` и без порта, например `localhost,127.0.0.1,89.125.39.139`).
3. Запустите из `kittygram`:

```sh
docker compose up -d --build
```

Приложение будет доступно через Nginx на порту `80`. Подробности находятся в `kittygram/README.md`.

## Секреты

Секреты, Telegram credentials, MTProto session-файлы, базы данных, media и виртуальные окружения исключены из Git. Используйте только файлы `.env.example` как шаблоны.
