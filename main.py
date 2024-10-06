import telebot
import httpx
import random
import time
from html2image import Html2Image
from io import BytesIO

# Инициализация бота
API_TOKEN = '7420597038:AAF-TC5qUHlwB7TMDtfHx7Ma5x1pPLgFDfo'
bot = telebot.TeleBot(API_TOKEN)

# Инициализация html2image для создания скриншотов
hti = Html2Image()

# Функция для имитации человеческого поведения
def human_like_delay():
    delay = random.uniform(1.5, 3.5)  # случайная задержка между 1.5 и 3.5 секундами
    time.sleep(delay)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на сайт, и я сделаю скриншот, имитируя работу пользователя.")

# Обработчик ссылок
@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_link(message):
    url = message.text
    try:
        # Имитация человеческой задержки перед запросом
        human_like_delay()

        # Получаем HTML сайта
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()  # Проверка успешного запроса
            
            # Снова задержка, чтобы имитировать время "чтения" контента
            human_like_delay()

            # Получаем HTML-код страницы
            html_content = response.text

            # Создаем скриншот HTML-кода
            hti.screenshot(html_str=html_content, save_as='screenshot.png')

            # Задержка перед отправкой изображения
            human_like_delay()

            # Отправляем скриншот пользователю
            with open('screenshot.png', 'rb') as screenshot:
                bot.send_photo(message.chat.id, screenshot)

    except httpx.RequestError as e:
        bot.reply_to(message, f"Ошибка при открытии сайта: {e}")

# Запуск бота
bot.polling()
