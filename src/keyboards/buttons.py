from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data.messages import INSTRUCTIONS, MY_PROFILE, MY_RATING, RECORD_VOICE, CHECK_VOICE, SEND_EVERYONE, BOT_STATISTICS, \
    CANCEL_MESSAGE, LEADERBOARD, \
    VOICE_LEADERBOARD, VOTE_LEADERBOARD, SEND_CERTAIN

admin_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
admin_button_1 = KeyboardButton(SEND_EVERYONE)
admin_button_2 = KeyboardButton(SEND_CERTAIN)
admin_button_3 = KeyboardButton(BOT_STATISTICS)
admin_markup.add(*[admin_button_1, admin_button_2, admin_button_3])


go_back_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
reject_button = KeyboardButton(CANCEL_MESSAGE)
go_back_markup.add(reject_button)


sure_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
send_button = KeyboardButton('✅ Start')
reject_button = KeyboardButton('🚫 Cancel')
sure_markup.add(*[send_button, reject_button])

yes_no_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
yes_button = KeyboardButton('✅ Yes')
no_button = KeyboardButton('🚫 No')
yes_no_markup.add(*[yes_button, no_button])

age_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
age_button_1 = KeyboardButton("< 19")
age_button_2 = KeyboardButton("19-29")
age_button_3 = KeyboardButton("30-39")
age_button_4 = KeyboardButton("40-49")
age_button_5 = KeyboardButton("50-59")
age_button_6 = KeyboardButton("60-69")
age_button_7 = KeyboardButton("70-79")
age_button_8 = KeyboardButton("80-89")
age_button_9 = KeyboardButton("> 89")
age_markup.add(*[age_button_1, age_button_2, age_button_3, age_button_4, 
                 age_button_5, age_button_6, age_button_7, age_button_8, age_button_9])

share_phone_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
share_phone_button = KeyboardButton("📱Raqamimni jo'natish", request_contact=True)
share_phone_markup.add(share_phone_button)


register_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
register_button = KeyboardButton("👤 Ro'yxatdan o'tish")
register_markup.add(*[register_button])


start_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
start_button_1 = KeyboardButton(RECORD_VOICE)
start_button_2 = KeyboardButton(CHECK_VOICE)
start_button_3 = KeyboardButton(LEADERBOARD)
start_button_4 = KeyboardButton(INSTRUCTIONS)
start_button_5 = KeyboardButton(MY_PROFILE)
start_button_6 = KeyboardButton(MY_RATING)
start_markup.add(*[start_button_1, start_button_2, start_button_3, start_button_4, start_button_5, start_button_6])


genders_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
female = KeyboardButton('👩 Ayol')
male = KeyboardButton('👨 Erkak')
genders_markup.add(*[female, male])


accents_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
andijon = KeyboardButton("Andijon")
buxoro = KeyboardButton("Buxoro")
fargona = KeyboardButton("Farg'ona")
jizzax = KeyboardButton("Jizzax")
sirdaryo = KeyboardButton("Sirdaryo")
xorazm = KeyboardButton("Xorazm")
namangan = KeyboardButton("Namangan")
navoiy = KeyboardButton("Navoiy")
qashqadaryo = KeyboardButton("Qashqadaryo")
qoraqalpogiston = KeyboardButton("Qoraqalpog'iston")
samarqand = KeyboardButton("Samarqand")
surxondaryo = KeyboardButton("Surxondaryo")
toshkent = KeyboardButton("Toshkent viloyati")
toshkent_shahri = KeyboardButton("Toshkent shahri")
accents_markup.add(*[andijon, buxoro, fargona, jizzax, sirdaryo, xorazm, namangan, navoiy, qashqadaryo,
                     qoraqalpogiston, samarqand, surxondaryo, toshkent, toshkent_shahri])


native_languages_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
uzbek = KeyboardButton("O'zbek tili")
qoraqalpoq = KeyboardButton("Qoraqalpoq tili")
russian = KeyboardButton("Rus tili")
tajik = KeyboardButton("Tojik tili")
kazakh = KeyboardButton("Qozoq tili")
native_languages_markup.add(*[uzbek, qoraqalpoq, russian], tajik, kazakh)

leader_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
leader_voice_button = KeyboardButton(VOICE_LEADERBOARD)
leader_vote_button = KeyboardButton(VOTE_LEADERBOARD)
leader_markup.add(*[leader_vote_button, leader_voice_button])
