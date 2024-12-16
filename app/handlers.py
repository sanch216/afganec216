#------------------------------------------------------------------
# Базовые импорты
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, ContentType , Voice
from commands import COMMANDS
# import app.keyboards as kb

from dotenv import load_dotenv

router_voice = Router()

#------------------------------------------------------------------
# Импорты для распознавания и обработки голосового сообщения
from pydub import AudioSegment
import torch
import whisper
from speaks import speak

#------------------------------------------------------------------
# Импорты для выполнения команд
import os
import datetime
import webbrowser
import wikipedia
import requests
import json
from pathlib import Path
#------------------------------------------------



#------------------------------------------------
# Классы ожидания
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State

# storage = MemoryStorage()
#------------------------------------------------------------------
#Waiting Class shits
#
# class DialogStates(StatesGroup):
#     waiting_for_city= State()

#Commands КОМАНДЫ
#------------------------------------------------------------------
# Start
# @router.message(CommandStart())
# async def cmdStart(message: Message) -> None:
#     await message.reply('Бот запущен',reply_markup = kb.main)
#     speak("Бот запущен",language ='ru')
# # Help
# @router.message(Command('help'))
# async def cmdHelp(message: Message) -> None:
#     await message.answer('Вот список команд, которые вы можете использовать:\n/start - запуск бота\n/help - получить помощь\n/work - запуск программы')
#
# # Work
# @router.message(Command('work'))
# async def cmdWork(message: Message) -> None:
#     await message.reply('Отправьте голосове сообщение: ')
#     # await state.set_state(DialogStates.waiting_for_voice_msg)
#
# # Settings
# @router.message(Command('settings'))
# async def settingsWork(message: Message) -> None:
#     await message.reply('Выберите пункт: ',reply_markup=kb.settings)
#
#
# # Хендлер для команды /mycity
# @router.message(Command("setcity"))
# async def cmd_mycity(message: Message, state: FSMContext):
#     await message.reply("Напишите ваш город:")
#     await state.set_state(DialogStates.waiting_for_city)
#
# # Хендлер для обработки ввода города
# @router.message(DialogStates.waiting_for_city)
# async def save_city(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     city = message.text
#     save_user_city(user_id, city)  # Сохраняем данные в JSON
#     await message.reply(f"Ваш город, {city}, успешно сохранён!")
#     await state.clear()  # Сбрасываем состояние
#
# # Хендлер для команды /info
# @router.message(Command("info"))
# async def cmd_info(message: Message):
#     user_id = message.from_user.id
#     city = get_user_city(user_id)
#     if city:
#         await message.reply(f"Ваш город: {city}")
#     else:
#         await message.reply("Город не указан. Установите его командой /mycity.")
#
#
# #------------------------------------------------------------------
# # СОХРАНЕНИЕ/ОБНОВЛЕНИЕ/ХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ В JSON
# DATA_FILE = Path("notes.json")
#
#
# # Функция для загрузки данных из файла
# def load_data():
#     if DATA_FILE.exists():
#         with open(DATA_FILE, "r", encoding="utf-8") as file:
#             return json.load(file)
#     return {}  # Если файл не существует, возвращаем пустой словарь
#
#
# # Функция для сохранения данных в файл
# def save_data(data):
#     with open(DATA_FILE, "w", encoding="utf-8") as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)
#
#
# # Сохранение города пользователя
# def save_user_city(user_id, city):
#     data = load_data()
#     data[str(user_id)+'city'] = {"city": city}
#     save_data(data)
#
#
# # Получение города пользователя
# def get_user_city(user_id):
#     data = load_data()
#     return data.get(str(user_id)+'city', {}).get('city')
#
#
# # Проверка удаления данных
# def delete_user_data(user_id):
#     data = load_data()
#     if str(user_id) in data:
#         del data[str(user_id)]
#         save_data(data)
#
# #------------------------------------------------------------------
# # СОЗДАТЬ ЗАМЕТКУ
# NOTES_FILE = Path("notes.json")
#
# def save_note_to_file(user_id, note_content):
#     notes = load_notes()
#     if str(user_id) not in notes:
#         notes[str(user_id)] = []
#     notes[str(user_id)].append({
#         "content": note_content,
#         "timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
#     })
#     save_notes(notes)
#
# def load_notes():
#     if NOTES_FILE.exists():
#         with open(NOTES_FILE, "r", encoding="utf-8") as file:
#             return json.load(file)
#     return {}
#
# def save_notes(notes):
#     with open(NOTES_FILE, "w", encoding="utf-8") as file:
#         json.dump(notes, file, indent=4, ensure_ascii=False)
#
#
# def show_notes(user_id):
#     notes = load_notes()
#     user_notes = notes.get(str(user_id), [])
#
#     if not user_notes:
#         return "У вас нет заметок."
#
#     notes_output = "\n".join(
#         [f"{index + 1}. {note['content']} \n(Создано: {note['timestamp']})"
#          for index, note in enumerate(user_notes)]
#     )
#
#     return notes_output
#
# def delete_note(user_id, note_index):
#     notes = load_notes()
#     user_notes = notes.get(user_id, [])
#
#     if 0 <= note_index < len(user_notes):  # Проверяем, существует ли заметка с таким индексом
#         del user_notes[note_index]  # Удаляем заметку
#         notes[user_id] = user_notes  # Обновляем список заметок пользователя
#         save_notes(notes)  # Сохраняем изменения в файл
#         return True
#     return False
#
#

# Voice to text

#------------------------------------------------------------------

device = "cpu"
# УКАЗЫВАЕМ МОДЕЛЬ WHISPER'а КОТОРЫЙ БУДЕТ РАСПОЗНАВАТЬ ГОЛОС. СООБЩ.

model = torch.hub.load("openai/whisper", "small", device=device,trust_repo=True)

#------------------------------------------------------------------
# ФУНКЦИЯ ДЛЯ ПРЕОБРАЗОВАНИЯ ИЗ .OGG -> .WAV ФОРМАТ
def ogg_to_wav(ogg_file_path):
    # Конвертируем OGG в WAV
    sound = AudioSegment.from_ogg(ogg_file_path)
    wav_file_path = ogg_file_path.replace(".ogg", ".wav")
    sound.export(wav_file_path, format="wav")
    return wav_file_path
#------------------------------------------------------------------
# ФУНКЦИЯ ДЛЯ "ОЧИСТКИ" ТЕКСТА ОТ ЛИШНИХ СИМВОЛОВ

import re
def clr_text(text):
    pattern = r'[А-Яа-яA-Za-z0-9\s]'
    clean_text = ''.join(re.findall(pattern, text))
    return clean_text
#------------------------------------------------------------------

#------------------------------------------------------------------
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ О ПОГОДЕ
# def get_weather(city):
#     try:
#         load_dotenv()
#         api_key = os.getenv("weather_api")
#         url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
#         response = requests.get(url).json()
#
#         # Проверяем, удалось ли получить данные
#         if response.get('cod') != 200:
#             return f"Ошибка: {response.get('message', 'Неизвестная ошибка')}"
#
#         weather = response['weather'][0]['description']
#         temp = response['main']['temp']
#         return f'Погода в {city}: {weather}, температура {temp}°C'
#     except Exception as e:
#         return f"Не удалось получить данные о погоде. Ошибка: {e}"

#------------------------------------------------------------------
# ОБРАБОТЧИК ГОЛОСОВОГО СООБЩЕНИЯ

@router_voice.message(F.voice)
async def handle_voice(message: Message):
    from main import bot # ДЛЯ СКАЧИВАНИЯ ГС
    voice: Voice = message.voice

    # Получаем информацию о голосовом сообщении
    file_id = voice.file_id

    # Скачиваем файл
    file = await bot.get_file(file_id)

    # Создаем директорию для сохранения, если ее нет
    if not os.path.exists('voices'):
        os.makedirs('voices')

    # Скачиваем файл
    file_path = f"voices/user.ogg"
    await bot.download_file(file.file_path, file_path)
    await message.answer("Голосовое сообщение сохранено!")

    # Конвертация OGG в WAV
    wav_file_path = ogg_to_wav(file_path)
    print(f"Конвертированный файл WAV: {wav_file_path}")
#-----------------------------------------------------------------

    try:
        # Распознавание речи с помощью Whisper

        result = model.transcribe(wav_file_path)
        text = result['text']
        await message.reply(f"Распознанный текст: {text}")

#------------------------------------------------
        #ЗДЕСЬ ИДЕТ ЛОГИРОВАНИЕ

        print(f"TEXT: {text}")
        txt = clr_text(text)
        print(f"CLEAR TEXT: {txt}")
        print(f"CLEAR TEXT LOWER: {txt.lower()}")

# ------------------------------------------------

#-----------------------------------------------------------------
# ПРОВЕРКА КОМАНД
        cmd_text = txt.lower().strip()
        print(f'CMD_TEXT: {cmd_text}')
        command_found = False

        for command, variants in COMMANDS.items():
            triggered_variant = next((variant for variant in variants if cmd_text.startswith(variant)), None)
            if triggered_variant:
                command_found = True
                #----------------------
                # КАКАЯ ПОГОДА
                if command == 'погода':
                    user_id = message.from_user.id
                    city = get_user_city(user_id)
                    if city:
                        weather =   get_weather(city)
                        await message.reply(weather)
                        speak(weather,language='ru')
                    else:
                        await message.reply("Город не указан. Напишите ваш город командой /setcity.")
                #----------------------
                # ЗАПИШИ ЗАМЕТКУ
                elif command == 'запиши заметку':

                    note_content = cmd_text.replace(triggered_variant, "").strip()  # Убираем текст команды

                    if note_content:

                        save_note_to_file(message.from_user.id, note_content)

                        await message.reply(f'Заметка сохранена: "{note_content}"')

                    else:

                        await message.reply("Текст заметки пуст. Попробуйте снова.")
                #----------------------
                # ОТКРОЙ ЗАМЕТКУ
                elif command == "открой заметки":

                    user_id = message.from_user.id

                    list_notes = show_notes(user_id)

                    await message.reply(f'Ваши заметки:\n{list_notes}')
                #----------------------
                # УДАЛИ ЗАМЕТКУ
                elif command == "удали заметку":
                    note_index_str = cmd_text.replace(triggered_variant, "").strip()  # Извлекаем индекс заметки
                    print(f'TEST – {note_index_str}')
                    if note_index_str.isdigit():  # Проверяем, что введён номер
                        note_index = int(note_index_str) - 1  # Индекс заметки (счёт от 1 для пользователя)
                        user_id = str(message.from_user.id)
                        result = delete_note(user_id, note_index)

                        if result:
                            await message.reply(f"Заметка номер {note_index + 1} удалена.")
                        else:
                            await message.reply(
                                f"Заметка номер {note_index + 1} не найдена. Проверьте правильность номера.")
                    else:
                        await message.reply(
                            "Введите номер заметки, которую нужно удалить, например: 'удали заметку 2'.")
                #----------------------
                # СКОЛЬКО ВРЕМЯ
                elif command == 'время':
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    await message.reply(f'Текущее время: {current_time}')

                #----------------------


                #----------------------
                # ЧТО ТАКОЕ ...

                elif command == 'что такое':
                    q = txt
                    webbrowser.open('http://www.google.com/search?q=' + q)

                #----------------------


                #----------------------
                # ОТКРОЙ САЙТ
                elif command == 'открой сайт':

                    url = cmd_text.replace(triggered_variant, "").strip()
                    if not url.startswith('http'):
                        url = f"http://{url}.com"
                    webbrowser.open(url)
                    await message.reply(f'Открываю сайт: {url}')
                #----------------------

                #----------------------
                # ОТКРОЙ ТГ

                elif command == 'открой телеграмм':
                    try:
                        await asyncio.to_thread(os.system, r'"C:\Users\sanch\AppData\Roaming\Telegram Desktop\Telegram.exe"')
                        await message.reply('Открываю Telegram.')
                    except Exception as e:
                        await message.reply(f"Ошибка: {str(e)}")
                #----------------------


                break

        if not command_found:
            await message.reply("Команда не распознана. Попробуйте снова.")

    except Exception as e:
        await message.reply(f"Ошибка распознавания: {str(e)}")

        
