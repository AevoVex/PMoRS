import logging
import os
import requests
from dotenv import load_dotenv
from telebot import TeleBot, types

# 1. Загрузка переменных окружения
load_dotenv()
secret_token = os.getenv('TOKEN')
bot = TeleBot(token=secret_token)

# 2. Настройка логирования
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
)

URL = 'https://api.thecatapi.com/v1/images/search'

# 3. Функция получения изображения с обработкой ошибок
def get_new_image():
    try:
        response = requests.get(URL).json()
        random_cat = response[0].get('url')
        return random_cat
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        # Запасной API с собаками
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url).json()
        return response[0].get('url')

# 4. Обработчик команды /newcat (должен быть выше общих обработчиков)
@bot.message_handler(commands=['newcat'])
def new_cat(message):
    chat_id = message.chat.id
    bot.send_photo(chat_id, get_new_image())

# 5. Обработчик команды /start
@bot.message_handler(commands=['start'])
def wake_up(message):
    chat_id = message.chat.id
    name = message.from_user.first_name

    # Создание клавиатуры с кнопкой
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('/newcat')
    keyboard.add(button)

    bot.send_message(
        chat_id=chat_id,
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашел',
        reply_markup=keyboard,
    )
    bot.send_photo(chat_id, get_new_image())

# 6. Обработчик обычных текстовых сообщений
@bot.message_handler(content_types=['text'])
def say_hi(message):
    bot.send_message(chat_id=message.chat.id, text='Привет, я KittyBot!')

# 7. Точка входа и запуск polling
def main():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()