#------------------------------------------------------------------
# Базовые импорты
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.types import Message, ContentType , Voice
from commands import COMMANDS
from msg_handlers import get_weather, get_user_city, load_data, save_data,save_user_city,delete_user_data,save_note_to_file,load_notes,save_notes,show_notes,delete_note
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
import requests
import json
from pathlib import Path
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

                        weather = get_weather(city)

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

                        speak('Сохранила вашу заметку','ru')

                    else:

                        await message.reply("Текст заметки пуст. Попробуйте снова.")
                #----------------------
                # ОТКРОЙ ЗАМЕТКУ
                elif command == "открой заметки":

                    user_id = message.from_user.id

                    list_notes = show_notes(user_id)

                    await message.reply(f'Ваши заметки:\n{list_notes}')
                    speak('Открыла ваши заметки в телеграме','ru')
                #----------------------
                # УДАЛИ ЗАМЕТКУ
                elif command == "удали заметку":

                    note_index_str = cmd_text.replace(triggered_variant, "").strip()  # Извлекаем индекс заметки

                    if note_index_str.isdigit():  # Проверяем, что введён номер

                        note_index = int(note_index_str) - 1  # Индекс заметки (счёт от 1 для пользователя)

                        user_id = str(message.from_user.id)

                        result = delete_note(user_id, note_index)

                        if result:

                            await message.reply(f"Заметка номер {note_index + 1} удалена.")

                            speak(f'Ваша заметка {note_index + 1} удалена')
                        else:

                            await message.reply(f"Заметка номер {note_index + 1} не найдена. Проверьте правильность номера.")

                    else:

                        await message.reply("Введите номер заметки, которую нужно удалить, например: 'удали заметку 2'.")
                #----------------------
                # СКОЛЬКО ВРЕМЯ
                elif command == 'время':

                    current_time = datetime.datetime.now().strftime("%H:%M:%S")

                    await message.reply(f'Текущее время: {current_time}')

                    speak(f'Текущее время: {current_time}','ru')

                #----------------------
                # ЧТО ТАКОЕ ...

                elif command == 'что такое':
                    q = txt

                    webbrowser.open('http://www.google.com/search?q=' + q)

                    speak("Ищу в поиске", 'ru')

                #----------------------
                # ОТКРОЙ САЙТ
                elif command == 'открой сайт':

                    url = cmd_text.replace(triggered_variant, "").strip()

                    if not url.startswith('http'):

                        url = f"http://{url}.com"

                    webbrowser.open(url)

                    await message.reply(f'Открываю сайт: {url}')

                    speak('Открываю сайт')
                #----------------------

                elif command == 'открой браузер':

                    webbrowser.open('https://www.google.ru/')

                    speak('Открываю','ru')

                #----------------------
                # ОТКРОЙ ТГ

                elif command == 'открой телеграмм':
                    try:
                        webbrowser.open('https://web.telegram.org/a/')
                        await message.reply('Открываю Telegram.')
                        speak('Открываю','ru')
                    except Exception as e:
                        await message.reply(f"Ошибка: {str(e)}")

                elif command == 'открой проводник':
                    os.startfile(r"C:\\")
                    speak('Открыла','ru')

                elif command == 'выключи компьютер':
                    os.system('shutdown -s -t 10')
                    speak('Всего хорошего!','ru')

                break

        if not command_found:
            await message.reply("Команда не распознана. Попробуйте снова.")

    except Exception as e:
        await message.reply(f"Ошибка распознавания: {str(e)}")

        
