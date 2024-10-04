import requests
from bs4 import BeautifulSoup
import urllib.parse
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Укажите токен вашего бота
TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'

# Создаем объект бота
bot = telebot.TeleBot(TOKEN)

# Функция для выполнения поиска файлов в Google
def perform_file_search(user_query, file_type="xlsx", page=0):
    # Формирование запроса
    google_query = f'"{user_query}" filetype:{file_type}'
    url = f"https://www.google.com/search?q={urllib.parse.quote(google_query)}&start={page*10}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = soup.find_all('div', class_='g')
    
    if results:
        response_text = f"Бот ищет информацию в гугле:\n\"{user_query}\" filetype:{file_type}\n\n"
        response_text += f"Результаты поиска для запроса '{user_query}' (страница {page+1}):\n\n"
        for i, result in enumerate(results[:1], start=page*1+1):
            title_element = result.find('h3')
            title = title_element.text.strip() if title_element else "Заголовок не найден"
            link = result.find('a')['href'] if result.find('a') else "Ссылка не найдена"
            description = result.find('div', class_='VwiC3b').text.strip() if result.find('div', class_='VwiC3b') else "Описание недоступно"
            site_name = urllib.parse.urlparse(link).netloc
            response_text += f"{i}. 🏷 {site_name}\n🔗 {link}\n🏴‍☠️ {title}\n📋 {description}\n\n"
    else:
        response_text = "Результатов нет."

    # Создание клавиатуры для навигации
    keyboard = InlineKeyboardMarkup()
    next_button = InlineKeyboardButton("»", callback_data=f"google_search_page;{user_query};{file_type};{page+1}")
    prev_button = InlineKeyboardButton("«", callback_data=f"google_search_page;{user_query};{file_type};{page-1}") if page > 0 else None

    if prev_button:
        keyboard.add(prev_button)
    keyboard.add(next_button)

    return response_text, keyboard

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Введите запрос для поиска файлов в формате xlsx.")

# Обработка текстовых сообщений от пользователя
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_query = message.text.strip()
    response_text, keyboard = perform_file_search(user_query)
    bot.send_message(message.chat.id, response_text, reply_markup=keyboard)

# Обработка нажатия кнопок пагинации
@bot.callback_query_handler(func=lambda call: call.data.startswith('google_search_page'))
def handle_pagination(call):
    try:
        _, user_query, file_type, page = call.data.split(';')
        page = int(page)
        response_text, keyboard = perform_file_search(user_query, file_type, page)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка обработки пагинации: {str(e)}")
        bot.answer_callback_query(call.id, text="Произошла ошибка при обработке запроса.")

# Запуск бота
bot.polling(none_stop=True) 
