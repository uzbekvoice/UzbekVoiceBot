from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.messages import VOICE_INCORRECT, VOICE_CORRECT, VOICE_REPORT, SKIP_STEP, REPORT_TEXT_1, \
    REPORT_TEXT_2, REPORT_TEXT_3, REPORT_TEXT_4, REPORT_TEXT_5, CONFIRM_VOICE_TEXT, REJECT_VOICE_TEXT, \
    VOICE_LEADERBOARD, VOTE_LEADERBOARD


def yes_no_markup(voice_id):
    markup = InlineKeyboardMarkup(row_width=2)
    accept_button = InlineKeyboardButton(text=VOICE_CORRECT, callback_data='accept/{}'.format(voice_id))
    reject_button = InlineKeyboardButton(text=VOICE_INCORRECT, callback_data='reject/{}'.format(voice_id))
    skip_button = InlineKeyboardButton(text=SKIP_STEP, callback_data='skip/{}'.format(voice_id))
    report_button = InlineKeyboardButton(text=VOICE_REPORT, callback_data='report/{}'.format(voice_id))
    markup.add(*[accept_button, reject_button])
    markup.add(report_button)
    markup.add(skip_button)
    return markup


def report_voice_markup(voice_id):
    markup = InlineKeyboardMarkup(row_width=1)
    report_button_1 = InlineKeyboardButton(text=REPORT_TEXT_1,
                                           callback_data='report_1/{}'.format(voice_id))
    report_button_2 = InlineKeyboardButton(text=REPORT_TEXT_2,
                                           callback_data='report_2/{}'.format(voice_id))
    report_button_3 = InlineKeyboardButton(text=REPORT_TEXT_3,
                                           callback_data='report_3/{}'.format(voice_id))
    report_button_5 = InlineKeyboardButton(text=REPORT_TEXT_5, callback_data='back/{}'.format(voice_id))
    markup.add(*[report_button_1, report_button_2, report_button_3, report_button_5])
    return markup


def report_text_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    report_button_1 = InlineKeyboardButton(text=REPORT_TEXT_1,
                                           callback_data='report_1')
    report_button_2 = InlineKeyboardButton(text=REPORT_TEXT_2,
                                           callback_data='report_2')
    report_button_3 = InlineKeyboardButton(text=REPORT_TEXT_3,
                                           callback_data='report_3')
    report_button_4 = InlineKeyboardButton(text=REPORT_TEXT_4,
                                           callback_data='report_4')
    report_button_5 = InlineKeyboardButton(text=REPORT_TEXT_5, callback_data='back')
    markup.add(*[report_button_1, report_button_2, report_button_3, report_button_4, report_button_5])
    return markup


def text_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    skip_button = InlineKeyboardButton(text=SKIP_STEP, callback_data='skip')
    report_button = InlineKeyboardButton(text=VOICE_REPORT, callback_data='report')
    markup.add(*[skip_button, report_button])
    return markup


def confirm_voice_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    confirm_button = InlineKeyboardButton(CONFIRM_VOICE_TEXT,
                                          callback_data='confirm-voice')
    reject_button = InlineKeyboardButton(REJECT_VOICE_TEXT,
                                         callback_data='reject-voice')
    markup.add(*[confirm_button, reject_button])
    return markup
