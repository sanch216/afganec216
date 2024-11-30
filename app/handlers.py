#------------------------------------------------------------------
# Базовые импорты
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, ContentType , Voice
from commands import COMMANDS
import app.keyboards as kb
# import types

router = Router()

#------------------------------------------------------------------
# Импорты для распознавания и обработки голосового сообщения
from pydub import AudioSegment
# import torchaudio
import torch
# import speech_recognition as sr
# import sounddevice as sd
import whisper
from speaks import speak

#------------------------------------------------------------------
# Импорты для выполнения команд
import os
import datetime
import webbrowser
import wikipedia
import requests
# import math

#------------------------------------------------

global user_city


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
    waiting_for_user_city= State()
    waiting_for_tg_path = State()

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

@router.message(Command('mycity'))
async def cmdCity(message: Message,state: FSMContext) -> None:
    await message.reply('Напишите ваш город: ')
    await state.set_state(DialogStates.waiting_for_user_city)

@router.message(DialogStates.waiting_for_user_city)
async def userCity(message: Message,state: FSMContext):
    user_city = message.text
    await state.clear()
    await message.reply(f'Ваш город, {user_city} , успешно сохранен!')

@router.message(Command('info'))
async def info(message: Message):
    await message.reply(f'ваш город: {user_city}')

# Voice to text

#------------------------------------------------------------------

device = "cpu"
# ispolzuem model ot openai (whisper)
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
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ О ПОГОДЕ
def get_weather():
    try:
        api_key = "b848c93f481c83de598e354f5f490f7d"
        city = "Бишкек"
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
# ОБРАБОТЧИК ГОЛОСОВОГО СООБЩЕНИЯ

@router.message(F.voice)
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

                if command == 'погода':
                    weather = get_weather()
                    await message.reply(weather if weather else "Не удалось получить данные о погоде.")

                elif command == 'время':
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    await message.reply(f'Текущее время: {current_time}')

                elif command == 'что такое':
                    search_query = cmd_text.replace(triggered_variant, "").strip()
                    if search_query:
                        try:
                            summary = wikipedia.summary(search_query, sentences=2, lang='ru')
                            await message.reply(summary)
                        except wikipedia.exceptions.DisambiguationError as e:
                            await message.reply(f"Слишком много вариантов: {e.options[:5]}")
                        except wikipedia.exceptions.PageError:
                            await message.reply("Страница не найдена.")
                        except Exception as e:
                            await message.reply(f"Ошибка: {str(e)}")
                    else:
                        await message.reply("Укажите, что искать.")

                elif command == 'открой сайт':

                    url = cmd_text.replace(triggered_variant, "").strip()
                    if not url.startswith('http'):
                        url = f"http://{url}.com"
                    webbrowser.open(url)
                    await message.reply(f'Открываю сайт: {url}')

                elif command == 'открой телеграмм':
                    try:
                        os.system(r'"C:\Users\sanch\AppData\Roaming\Telegram Desktop\Telegram.exe"')
                        await message.reply('Открываю Telegram.')
                    except Exception as e:
                        await message.reply(f"Ошибка: {str(e)}")

                break

        if not command_found:
            await message.reply("Команда не распознана. Попробуйте снова.")

    except Exception as e:
        await message.reply(f"Ошибка распознавания: {str(e)}")



































# if cmd_text.startswith("запиши заметку"):
        #     note_content = txt[15:].strip()  # Убираем "Запиши заметку"
        #     print(f"NOTE CONTENT: {note_content}")
        #     if note_content:
        #         with open("notes.txt", "a", encoding="utf-8") as file:
        #             file.write(f"{note_content}\n")
        #         await message.reply(f"Заметка сохранена: {note_content}")
        #         speak('заметка сохранена',language='ru')
        #     else:
        #         await message.reply("Текст заметки пуст. Попробуйте снова.")
        # else:
        #     await message.reply("Команда не распознана. Попробуйте снова.")
        
