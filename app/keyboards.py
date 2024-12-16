from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = '/work'), KeyboardButton(text = '/help')], [KeyboardButton(text = '/settings'),KeyboardButton(text = '/commands')],
], resize_keyboard = True, input_field_placeholder = 'Выберите пункт...')

settings = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = '/setcity'), KeyboardButton(text = '/info')]
], resize_keyboard = True, input_field_placeholder = 'Выберите пункт...')

