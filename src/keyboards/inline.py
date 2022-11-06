from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.messages import CANCEL_MESSAGE, VOICE_INCORRECT, VOICE_CORRECT, VOICE_REPORT, SKIP_STEP, REPORT_TEXT_1, \
    REPORT_TEXT_2, REPORT_TEXT_3, REPORT_TEXT_4, REPORT_TEXT_5, CONFIRM_VOICE_TEXT, REJECT_VOICE_TEXT, \
    SUBMIT_VOICE_TEXT, GO_HOME_TEXT


def yes_no_markup(voice_id, confirm_state=None):
    markup = InlineKeyboardMarkup(row_width=2)
    accept_button = InlineKeyboardButton(text='{} {}'.format('✅️' if confirm_state == 'accept' else '', VOICE_CORRECT),
                                         callback_data='accept/{}'.format(voice_id))
    reject_button = InlineKeyboardButton(text='{} {}'.format('✅️' if confirm_state == 'reject' else '', VOICE_INCORRECT),
                                         callback_data='reject/{}'.format(voice_id))
    skip_button = InlineKeyboardButton(text='{} {}'.format('✅️' if confirm_state == 'skip' else '', SKIP_STEP),
                                       callback_data='skip/{}'.format(voice_id))
    report_button = InlineKeyboardButton(text=VOICE_REPORT, callback_data='report/{}'.format(voice_id))
    markup.add(*[accept_button, reject_button])
    markup.add(skip_button)
    markup.add(report_button)
    if confirm_state is not None:
        next_button = InlineKeyboardButton(SUBMIT_VOICE_TEXT,
                                           callback_data='submit/{}'.format(voice_id))
        markup.add(next_button)
    else:
        markup.add(InlineKeyboardButton(GO_HOME_TEXT, callback_data='home'))
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


def edit_profile_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    edit_age_button = InlineKeyboardButton("Yosh", callback_data='edit-age')
    edit_lang_button = InlineKeyboardButton("Til", callback_data='edit-lang')
    edit_accent_button = InlineKeyboardButton("Sheva", callback_data='edit-accent')
    reject_button = InlineKeyboardButton(GO_HOME_TEXT, callback_data=GO_HOME_TEXT)
    markup.add(*[edit_age_button, edit_lang_button, edit_accent_button, reject_button])
    return markup


def edit_age_markup():
    age_markup = InlineKeyboardMarkup(row_width=1)
    age_button_1 = InlineKeyboardButton("< 19", callback_data="< 19")
    age_button_2 = InlineKeyboardButton("19-29", callback_data="19-29")
    age_button_3 = InlineKeyboardButton("30-39", callback_data="30-39")
    age_button_4 = InlineKeyboardButton("40-49", callback_data="40-49")
    age_button_5 = InlineKeyboardButton("50-59", callback_data="50-59")
    age_button_6 = InlineKeyboardButton("60-69", callback_data="60-69")
    age_button_7 = InlineKeyboardButton("70-79", callback_data="70-79")
    age_button_8 = InlineKeyboardButton("80-89", callback_data="80-89")
    age_button_9 = InlineKeyboardButton("> 89", callback_data="> 89")
    reject_button = InlineKeyboardButton(GO_HOME_TEXT, callback_data=GO_HOME_TEXT)
    age_markup.add(*[age_button_1, age_button_2, age_button_3, age_button_4, 
                    age_button_5, age_button_6, age_button_7, age_button_8, age_button_9, reject_button])

    return age_markup


def edit_lang_markup():
    native_languages_markup = InlineKeyboardMarkup(row_width=2)
    uzbek = InlineKeyboardButton("O'zbek tili", callback_data="O'zbek tili")
    qoraqalpoq = InlineKeyboardButton("Qoraqalpoq tili", callback_data="Qoraqalpoq tili")
    russian = InlineKeyboardButton("Rus tili", callback_data="Rus tili")
    tajik = InlineKeyboardButton("Tojik tili", callback_data="Tojik tili")
    kazakh = InlineKeyboardButton("Qozoq tili", callback_data="Qozoq tili")
    reject_button = InlineKeyboardButton(GO_HOME_TEXT, callback_data=GO_HOME_TEXT)
    native_languages_markup.add(*[uzbek, qoraqalpoq, russian, tajik, kazakh, reject_button])

    return native_languages_markup


def edit_accent_markup():
    accents_markup = InlineKeyboardMarkup(row_width=2)
    andijon = InlineKeyboardButton("Andijon", callback_data="Andijon")
    buxoro = InlineKeyboardButton("Buxoro", callback_data="Buxoro")
    fargona = InlineKeyboardButton("Farg'ona", callback_data="Farg'ona")
    jizzax = InlineKeyboardButton("Jizzax", callback_data="Jizzax")
    sirdaryo = InlineKeyboardButton("Sirdaryo", callback_data="Sirdaryo")
    xorazm = InlineKeyboardButton("Xorazm", callback_data="Xorazm")
    namangan = InlineKeyboardButton("Namangan", callback_data="Namangan")
    navoiy = InlineKeyboardButton("Navoiy", callback_data="Navoiy")
    qashqadaryo = InlineKeyboardButton("Qashqadaryo", callback_data="Qashqadaryo")
    qoraqalpogiston = InlineKeyboardButton("Qoraqalpog'iston", callback_data="Qoraqalpog'iston")
    samarqand = InlineKeyboardButton("Samarqand", callback_data="Samarqand")
    surxondaryo = InlineKeyboardButton("Surxondaryo", callback_data="Surxondaryo")
    toshkent = InlineKeyboardButton("Toshkent viloyati", callback_data="Toshkent viloyati")
    toshkent_shahri = InlineKeyboardButton("Toshkent shahri", callback_data="Toshkent shahri")
    reject_button = InlineKeyboardButton(GO_HOME_TEXT, callback_data=GO_HOME_TEXT)
    accents_markup.add(*[andijon, buxoro, fargona, jizzax, sirdaryo, xorazm, namangan, navoiy, qashqadaryo,
                        qoraqalpogiston, samarqand, surxondaryo, toshkent, toshkent_shahri, reject_button])

    return accents_markup


def my_profile_markup():
    my_profile_markup = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    settings_button = InlineKeyboardButton('⚙️ Sozlamalar', callback_data='⚙️ Sozlamalar')
    reject_button = InlineKeyboardButton(GO_HOME_TEXT, callback_data=GO_HOME_TEXT)
    my_profile_markup.add(*[settings_button, reject_button])

    return my_profile_markup
