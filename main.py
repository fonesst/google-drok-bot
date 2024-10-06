import telebot
import requests
from html2image import Html2Image
from io import BytesIO

# Инициализация бота
API_TOKEN = '7420597038:AAF-TC5qUHlwB7TMDtfHx7Ma5x1pPLgFDfo'
bot = telebot.TeleBot(API_TOKEN)

# Инициализация html2image для создания скриншотов
hti = Html2Image()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на сайт, и я сделаю скриншот.")

# Обработчик ссылок
@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_link(message):
    url = message.text
    try:
        # Получаем HTML сайта
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный запрос
        
        # Создаем скриншот HTML-кода
        html_content = response.text
        hti.screenshot(html_str=html_content, save_as='screenshot.png')

        # Открываем скриншот и отправляем пользователю
        with open('screenshot.png', 'rb') as screenshot:
            bot.send_photo(message.chat.id, screenshot)

    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка при открытии сайта: {e}")

# Запуск бота
bot.polling()
