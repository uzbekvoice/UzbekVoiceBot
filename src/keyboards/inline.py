from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.messages import VOICE_INCORRECT, VOICE_CORRECT, VOICE_REPORT, SKIP_STEP, REPORT_TEXT_1, \
    REPORT_TEXT_2, REPORT_TEXT_3, REPORT_TEXT_4, REPORT_TEXT_5

yes_no_markup = InlineKeyboardMarkup(row_width=2)
accept_button = InlineKeyboardButton(text=VOICE_CORRECT, callback_data='accept')
reject_button = InlineKeyboardButton(text=VOICE_INCORRECT, callback_data='reject')
skip_button = InlineKeyboardButton(text=SKIP_STEP, callback_data='skip')
report_button = InlineKeyboardButton(text=VOICE_REPORT, callback_data='report')
yes_no_markup.add(*[accept_button, reject_button, skip_button])
yes_no_markup.add(report_button)


report_voice_markup = InlineKeyboardMarkup(row_width=1)
report_text_markup = InlineKeyboardMarkup(row_width=1)

report_button_1 = InlineKeyboardButton(text=REPORT_TEXT_1, callback_data='report_1')
report_button_2 = InlineKeyboardButton(text=REPORT_TEXT_2, callback_data='report_2')
report_button_3 = InlineKeyboardButton(text=REPORT_TEXT_3, callback_data='report_3')
report_button_4 = InlineKeyboardButton(text=REPORT_TEXT_4, callback_data='report_4')
report_button_5 = InlineKeyboardButton(text=REPORT_TEXT_5, callback_data='back')

report_voice_markup.add(*[report_button_1, report_button_2, report_button_3, report_button_5])
report_text_markup.add(*[report_button_1, report_button_2, report_button_3, report_button_4, report_button_5])


skip_report_markup = InlineKeyboardMarkup(row_width=1)
skip_report_markup.add(*[skip_button, report_button])
