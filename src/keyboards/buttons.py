from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data.messages import RECORD_VOICE, CHECK_VOICE, SEND_EVERYONE, BOT_STATISTICS

admin_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
admin_button_1 = KeyboardButton(SEND_EVERYONE)
admin_button_2 = KeyboardButton(BOT_STATISTICS)
admin_markup.add(*[admin_button_1, admin_button_2])

reject_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
reject_button = KeyboardButton('Отменить')
reject_markup.add(reject_button)


sure_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
send_button = KeyboardButton('Начать')
reject_button = KeyboardButton('Отменить')
sure_markup.add(*[send_button, reject_button])


start_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_button_1 = KeyboardButton(RECORD_VOICE)
start_button_2 = KeyboardButton(CHECK_VOICE)
start_markup.add(*[start_button_1, start_button_2])
