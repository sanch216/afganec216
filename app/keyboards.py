from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup,KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = '/work'), KeyboardButton(text = '/help')],
], resize_keyboard = True, input_field_placeholder = 'Выберите пункт...')

