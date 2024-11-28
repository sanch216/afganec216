import datetime
import types
import webbrowser
from aiogram.types import Message, ContentType , Voice
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
import app.keyboards as kb
from main import bot
from commands import COMMANDS
#------------------------------------------------
import wikipedia
import requests
import math
from pydub import AudioSegment
import os
import torchaudio
import torch
import speech_recognition as sr
import sounddevice as sd
import whisper
#------------------------------------------------
from speaks import speak
#------------------------------------------------
router = Router()
user_city = "Бишкек"
#Waiting Class shits
#
# class DialogStates(StatesGroup):
#     waiting_for_voice_msg = State()

#Commands
#------------------------------------------------------------------
#Start
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


#

# Voice to text

device = "cpu"

# ispolzuem model ot openai (whisper)

model = torch.hub.load("openai/whisper", "small", device=device,trust_repo=True)

# # Iz ogg formata v wav format
def ogg_to_wav(ogg_file_path):
    # Конвертируем OGG в WAV
    sound = AudioSegment.from_ogg(ogg_file_path)
    wav_file_path = ogg_file_path.replace(".ogg", ".wav")
    sound.export(wav_file_path, format="wav")
    return wav_file_path
#----------------------------------------------------------
import re

def clr_text(text):
    pattern = r'[А-Яа-яA-Za-z0-9\s\.]'
    clean_text = ''.join(re.findall(pattern, text))
    return clean_text

#----------------------------------------------------------

# Sam obrabotchik voice message

@router.message(F.voice)
async def handle_voice(message: Message):
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
        print(f"TEXT: {text}")
        txt = clr_text(text)
        print(f"CLEAR TEXT: {txt}")
        print(f"CLEAR TEXT LOWER: {txt.lower()}")

#-----------------------------------------------------------------
# Проверка на команду создания заметки
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
                        url = f"http://{url}"
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



def get_weather():
    try:
        api_key = "b848c93f481c83de598e354f5f490f7d"
        city = "Bishkek"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        response = requests.get(url).json()
        weather = response['weather'][0]['description']
        temp = response['main']['temp']
        weather_result = f'Погода в {city}: {weather}, температура {temp} '
    except Exception:
        return "Не удалось получить данные о погоде."
































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
        
