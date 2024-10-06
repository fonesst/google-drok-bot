import telebot
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import zipfile
import time
import shutil

# Инициализация бота
TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'
bot = telebot.TeleBot(TOKEN)

# Глобальные переменные
user_query = {}
base_dir = 'search_results'

# Словарь категорий и расширений файлов
file_categories = {
    "Текстовые файлы": ['txt', 'md', 'log', 'csv', 'xml', 'json', 'yaml', 'yml', 'ini', 'rtf', 'doc', 'docx', 'pdf'],
    "Табличные файлы": ['xls', 'xlsx', 'ods', 'csv', 'tsv'],
    "Базы данных": ['db', 'sqlite', 'sqlite3', 'sql', 'mdb', 'accdb'],
    "Изображения": ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
    "Аудио файлы": ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
    "Видео файлы": ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv'],
    "Архивы и сжатие": ['zip', 'rar', '7z', 'tar', 'gz'],
    "Файлы кодирования и сценариев": ['py', 'js', 'html', 'css', 'php', 'cpp', 'java'],
    "Документы": ['pdf', 'doc', 'docx', 'odt', 'rtf'],
    "Системные файлы": ['exe', 'dll', 'sys', 'bat', 'ini'],
    "3D Моделирование и графика": ['obj', 'fbx', 'stl', 'blend'],
    "Виртуальные машины и контейнеры": ['vdi', 'vmdk', 'dockerfile'],
    "Другие специализированные файлы": ['torrent', 'ics', 'apk', 'ipa']
}

def perform_google_search(query, filetype, start=0, max_results=100):
    all_results = []
    while len(all_results) < max_results:
        search_query = f"{query} filetype:{filetype}"
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}&start={start}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = soup.find_all('div', class_='g')
        if not results:
            break

        for result in results:
            link = result.find('a', href=True)
            if link:
                url = link['href']
                domain = urllib.parse.urlparse(url).netloc
                all_results.append((domain, url))
                if len(all_results) >= max_results:
                    break

        start += 10
        time.sleep(1)

    return all_results

def save_results_to_file(results, category, filetype, base_dir):
    category_dir = os.path.join(base_dir, category, filetype.upper())
    os.makedirs(category_dir, exist_ok=True)
    
    for domain, url in results:
        file_path = os.path.join(category_dir, f'{domain}.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(url)

def create_zip_structure(base_dir, zip_name='all_results.zip'):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for folder, subfolders, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(folder, file)
                archive_path = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, archive_path)

def clear_data(chat_id):
    # Очистка глобальных переменных
    if chat_id in user_query:
        del user_query[chat_id]
    
    # Удаление директории с результатами поиска
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    # Удаление ZIP-файла, если он существует
    if os.path.exists('all_results.zip'):
        os.remove('all_results.zip')

@bot.message_handler(commands=['dorks'])
def handle_dorks_command(message):
    clear_data(message.chat.id)  # Очистка данных перед новым поиском
    bot.send_message(message.chat.id, "Введите текст для поиска:")
    bot.register_next_step_handler(message, get_user_query)

def get_user_query(message):
    user_query[message.chat.id] = message.text
    bot.send_message(message.chat.id, "Ищу файлы по вашему запросу. Это может занять некоторое время...")

    os.makedirs(base_dir, exist_ok=True)

    for category, extensions in file_categories.items():
        bot.send_message(message.chat.id, f"Поиск в категории '{category}'...")
        
        for filetype in extensions:
            search_results = perform_google_search(user_query[message.chat.id], filetype)
            if search_results:
                save_results_to_file(search_results, category, filetype, base_dir)
                bot.send_message(message.chat.id, f"Найдено {len(search_results)} результатов для типа {filetype}")

    zip_path = 'all_results.zip'
    create_zip_structure(base_dir, zip_path)

    with open(zip_path, 'rb') as zip_file:
        bot.send_document(message.chat.id, zip_file)

    bot.send_message(message.chat.id, "Поиск завершен. Результаты отправлены в виде ZIP-архива.")
    clear_data(message.chat.id)  # Очистка данных после завершения поиска

# Запуск бота
bot.polling()
