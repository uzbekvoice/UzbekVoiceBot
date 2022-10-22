from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data.messages import RECORD_VOICE, CHECK_VOICE, SEND_EVERYONE, BOT_STATISTICS, CANCEL_MESSAGE


admin_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
admin_button_1 = KeyboardButton(SEND_EVERYONE)
admin_button_2 = KeyboardButton(BOT_STATISTICS)
admin_markup.add(*[admin_button_1, admin_button_2])

reject_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
reject_button = KeyboardButton(CANCEL_MESSAGE)
reject_markup.add(reject_button)


sure_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
send_button = KeyboardButton('Начать')
reject_button = KeyboardButton('Отменить')
sure_markup.add(*[send_button, reject_button])

share_phone_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
share_phone_button = KeyboardButton("📱Raqamimni jo'natish", request_contact=True)
share_phone_markup.add(share_phone_button)


register_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
register_button = KeyboardButton("👤 Ro'yxatdan o'tish")
register_markup.add(*[register_button])


start_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
start_button_1 = KeyboardButton(RECORD_VOICE)
start_button_2 = KeyboardButton(CHECK_VOICE)
start_markup.add(*[start_button_1, start_button_2])


genders_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
female = KeyboardButton("Ayol")
male = KeyboardButton("Erkak")
genders_markup.add(*[female, male])


accents_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
andijon = KeyboardButton("Andijon")
buxoro = KeyboardButton("Buxoro")
fargona = KeyboardButton("Farg'ona")
jizzax = KeyboardButton("Jizzax")
xorazm = KeyboardButton("Xorazm")
namangan = KeyboardButton("Namangan")
navoiy = KeyboardButton("Navoiy")
qashqadaryo = KeyboardButton("Qashqadaryo")
qoraqalpogiston = KeyboardButton("Qoraqalpog'iston")
samarqand = KeyboardButton("Samarqand")
surxondaryo = KeyboardButton("Surxondaryo")
toshkent = KeyboardButton("Toshkent viloyati")
toshkent_shahri = KeyboardButton("Toshkent shahri")
accents_markup.add(*[andijon, buxoro, fargona, jizzax, xorazm, namangan, navoiy, qashqadaryo, 
                     qoraqalpogiston, samarqand, surxondaryo, toshkent, toshkent_shahri])


native_languages_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
uzbek = KeyboardButton("O'zbek tili")
qoraqalpoq = KeyboardButton("Qoraqalpoq tili")
russian = KeyboardButton("Rus tili")
native_languages_markup.add(*[uzbek, qoraqalpoq, russian])
