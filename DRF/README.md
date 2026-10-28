# Yatube и Kittygram: DRF.pdf и продолжение DRF2.pdf

Здесь находятся два готовых локальных Django REST API и учебные варианты из методичек: [DRF.pdf](../DRF.pdf), 152 страницы, и [DRF2.pdf](../DRF2.pdf), 16 страниц. Основной Yatube обновлён по продолжению: приложение api, вьюсеты, группы по ID, авторы по username и комментарии. Решение первой части сохранено отдельно в lessons. Kittygram соответствует первой методичке.

## Что открыть сначала

- [Что сделано, как и почему](docs/REPORT.md) — основной отчёт для сдачи и объяснения работы.
- [Задания по страницам PDF](docs/REQUIREMENTS.md) — соответствие требований коду и проверкам.
- [Архитектура и модели данных](docs/ARCHITECTURE.md).
- [Демонстрация через PowerShell и Postman](docs/DEMO.md).
- [Результаты проверок](docs/VERIFICATION.md).
- [Оригинальные тесты и Postman-коллекция](yatube/UPSTREAM.md): 49 официальных тестов; Postman CLI — 60 запросов, 88 проверок.
- [Yatube: запуск и API](yatube/README.md), [Kittygram: запуск и API](kittygram/README.md).

## Быстрый запуск на этом компьютере

Окружение уже установлено в `D:\Dev\PMoRS\.venv-drf`. Миграции применены, демонстрационные данные созданы. Откройте два терминала PowerShell:

```powershell
cd D:\Dev\PMoRS\DRF
powershell -ExecutionPolicy Bypass -File .\run.ps1 yatube
```

```powershell
cd D:\Dev\PMoRS\DRF
powershell -ExecutionPolicy Bypass -File .\run.ps1 kittygram
```

Yatube работает на `http://127.0.0.1:8000/api/v1/posts/`, Kittygram — на `http://127.0.0.1:8001/cats/`. Ответ 401 без токена ожидаем: сначала выполните вход по [инструкции](docs/DEMO.md). Для остановки нажмите Ctrl+C в терминале сервера.

Учебные аккаунты в обоих проектах: `alice` и `bob`, пароль `Demo-Learning-42!`. Это обычные пользователи локальной демонстрации; для `/admin/` создайте суперпользователя командой `createsuperuser`.

## Установка с нуля

Нужен Python 3.12. Все команды ниже выполняются из папки `DRF`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe yatube\manage.py migrate
.\.venv\Scripts\python.exe yatube\manage.py seed_demo
.\.venv\Scripts\python.exe kittygram\manage.py migrate
.\.venv\Scripts\python.exe kittygram\manage.py seed_demo
```

`run.ps1` сначала ищет `DRF\.venv`, затем уже подготовленное `PMoRS\.venv-drf`. Активация окружения не обязательна. Скрипт применяет миграции перед запуском и слушает только `127.0.0.1`.

Для проверки в новом окружении:

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
.\.venv\Scripts\python.exe scripts\smoke_http.py
```

Перед `verify.py` установите тестовые зависимости: `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`. В подготовленном окружении замените `.\.venv\Scripts\python.exe` на `..\.venv-drf\Scripts\python.exe`.

Дополнительная проверка при установленном Postman CLI: `..\.venv-drf\Scripts\python.exe scripts\run_postman.py`. Она создаёт временную базу и не очищает рабочие данные.

## Состав

```text
DRF/
  yatube/           # Посты, группы, изображения, комментарии; Token
    api/           # Основной API по DRF2: вьюсеты, сериализаторы, права, роутер
    lessons/       # Сохранённые функции и другие этапы DRF1
    tests/         # Оригинальные тесты api_yatube
    postman_collection/  # Оригинальная коллекция
  kittygram/        # Коты, пользователи, достижения; Djoser + JWT
    lessons/       # Ранние этапы, отдельные настройки и база
  docs/             # Отчёт, требования, архитектура, демонстрация, проверки
  requests/         # Готовые HTTP-запросы для REST Client
  scripts/          # Автоматические проверки
  run.ps1
  requirements.txt
```

SQLite выбран для воспроизводимого учебного запуска без отдельного сервера БД. Пароли пользователей хешируются Django. Локальный ключ создаётся автоматически в `.local-secret`; базы, ключи и загруженные изображения исключены из Git. Переменные `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_DB_PATH` можно передать через окружение; соседний `.env` не читается.

Это локальная учебная поставка API: публикация в интернете, фронтенд, Telegram и оплата в заданиях этого PDF не требуются. Настройки с `DEBUG=True` предназначены для локального запуска.
