from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.messages import VOICE_INCORRECT, VOICE_CORRECT

yes_no_markup = InlineKeyboardMarkup(row_width=2)
accept_button = InlineKeyboardButton(text=VOICE_CORRECT, callback_data='accept')
reject_button = InlineKeyboardButton(text=VOICE_INCORRECT, callback_data='reject')
yes_no_markup.add(*[accept_button, reject_button])
