#------------------------------------------------------------------
# Базовые импорты
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message
import app.keyboards as kb

from dotenv import load_dotenv

router = Router()

#------------------------------------------------------------------
import os
import datetime
import requests
import json
from pathlib import Path
#------------------------------------------------
# Классы ожидания
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

storage = MemoryStorage()
#------------------------------------------------------------------
#Waiting Class shits
#
class DialogStates(StatesGroup):
    waiting_for_city = State()

#Commands КОМАНДЫ
#------------------------------------------------------------------
# Start
@router.message(CommandStart())
async def cmdStart(message: Message) -> None:
    await message.reply('Бот запущен',reply_markup = kb.main)
# Help
@router.message(Command('help'))
async def cmdHelp(message: Message) -> None:
    await message.answer('Вот список команд, которые вы можете использовать:\n/start - запуск бота\n/help - получить помощь\n/work - запуск программы')

# Work
@router.message(Command('work'))
async def cmdWork(message: Message) -> None:
    await message.reply('Отправьте голосове сообщение: ')
    # await state.set_state(DialogStates.waiting_for_voice_msg)

# Settings
@router.message(Command('settings'))
async def settingsWork(message: Message) -> None:
    await message.reply('Выберите пункт: ',reply_markup=kb.settings)


# Хендлер для команды /mycity
@router.message(Command("setcity"))
async def cmd_mycity(message: Message, state: FSMContext):
    await message.reply("Напишите ваш город:")
    await state.set_state(DialogStates.waiting_for_city)

# Хендлер для обработки ввода города
@router.message(DialogStates.waiting_for_city)
async def save_city(message: Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text
    save_user_city(user_id, city)  # Сохраняем данные в JSON
    await message.reply(f"Ваш город, {city}, успешно сохранён!")
    await state.clear()  # Сбрасываем состояние

# Хендлер для команды /info
@router.message(Command("info"))
async def cmd_info(message: Message):
    user_id = message.from_user.id
    city = get_user_city(user_id)
    if city:
        await message.reply(f"Ваш город: {city}")
    else:
        await message.reply("Город не указан. Установите его командой /mycity.")

#------------------------------------------------------------------
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ О ПОГОДЕ
def get_weather(city):
    try:
        load_dotenv()
        api_key = os.getenv("weather_api")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        response = requests.get(url).json()

        # Проверяем, удалось ли получить данные
        if response.get('cod') != 200:
            return f"Ошибка: {response.get('message', 'Неизвестная ошибка')}"

        weather = response['weather'][0]['description']
        temp = response['main']['temp']
        return f'Погода в {city}: {weather}, температура {temp}°C'
    except Exception as e:
        return f"Не удалось получить данные о погоде. Ошибка: {e}"

#------------------------------------------------------------------
# СОХРАНЕНИЕ/ОБНОВЛЕНИЕ/ХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ В JSON
DATA_FILE = Path("notes.json")


# Функция для загрузки данных из файла
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}  # Если файл не существует, возвращаем пустой словарь


# Функция для сохранения данных в файл
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Сохранение города пользователя
def save_user_city(user_id, city):
    data = load_data()
    data[str(user_id)+'city'] = {"city": city}
    save_data(data)


# Получение города пользователя
def get_user_city(user_id):
    data = load_data()
    return data.get(str(user_id)+'city', {}).get('city')


# Проверка удаления данных
def delete_user_data(user_id):
    data = load_data()
    if str(user_id) in data:
        del data[str(user_id)]
        save_data(data)

#------------------------------------------------------------------
# СОЗДАТЬ ЗАМЕТКУ
NOTES_FILE = Path("notes.json")

def save_note_to_file(user_id, note_content):
    notes = load_notes()
    if str(user_id) not in notes:
        notes[str(user_id)] = []
    notes[str(user_id)].append({
        "content": note_content,
        "timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    })
    save_notes(notes)

def load_notes():
    if NOTES_FILE.exists():
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4, ensure_ascii=False)


def show_notes(user_id):
    notes = load_notes()
    user_notes = notes.get(str(user_id), [])

    if not user_notes:
        return "У вас нет заметок."

    notes_output = "\n".join(
        [f"{index + 1}. {note['content']} \n(Создано: {note['timestamp']})"
         for index, note in enumerate(user_notes)]
    )

    return notes_output

def delete_note(user_id, note_index):
    notes = load_notes()
    user_notes = notes.get(user_id, [])

    if 0 <= note_index < len(user_notes):  # Проверяем, существует ли заметка с таким индексом
        del user_notes[note_index]  # Удаляем заметку
        notes[user_id] = user_notes  # Обновляем список заметок пользователя
        save_notes(notes)  # Сохраняем изменения в файл
        return True
    return False


