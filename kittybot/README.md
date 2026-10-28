# KittyBot

Telegram-бот на Python: приветствует пользователя, показывает кнопку `/newcat`
и присылает случайную фотографию котика. Если The Cat API временно недоступен,
бот запрашивает фотографию собаки в The Dog API.

## Подготовка

1. Создайте бота через `@BotFather` и сохраните полученный токен.
2. Скопируйте `.env.example` в `.env`.
3. В `.env` замените пример на настоящий токен:

   ```env
   TOKEN=123456789:your_bot_token
   ```

4. В PowerShell установите зависимости и запустите бота:

   ```powershell
   cd D:\Dev\PMoRS\kittybot
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe kittybot.py
   ```

Перед первым сообщением откройте созданного бота в Telegram и нажмите **Start**.

## Проверка

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

Файл `.env` исключён из Git. Не публикуйте токен и не добавляйте его прямо в код.
