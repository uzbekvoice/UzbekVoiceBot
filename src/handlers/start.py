import pandas
import aiohttp
from aiogram.types import Message, ParseMode
from aiogram.dispatcher import FSMContext
import re
from main import bot
from keyboards.buttons import (
    native_languages_markup,
    share_phone_markup,
    register_markup,
    accents_markup,
    genders_markup,
    leader_markup,
    start_markup,
    age_markup
)
from utils.uzbekvoice import db
from main import UserRegistration, dp
from utils.helpers import send_message
from data.messages import INSTRUCTIONS, LEADERBOARD, VOTE_LEADERBOARD, VOICE_LEADERBOARD
from utils.uzbekvoice.helpers import register_user, VOTES_LEADERBOARD_URL, CLIPS_LEADERBOARD_URL, \
    authorization_base64


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: Message, state: FSMContext):
    await state.finish()
    if db.user_exists(message.chat.id):
        await send_message(message.chat.id, 'welcome-text', markup=start_markup)
    else:
        await send_message(message.chat.id, 'start', markup=register_markup)


# Answer to all bot commands
@dp.message_handler(text="👤 Ro'yxatdan o'tish")
async def start_command(message: Message):
    if not db.user_exists(message.chat.id):
        await UserRegistration.full_name.set()
        await send_message(message.chat.id, 'ask-full-name')


@dp.message_handler(state=UserRegistration.full_name)
async def get_name(message: Message, state: FSMContext):
    if message.text == "👤 Ro'yxatdan o'tish":
        await UserRegistration.full_name.set()
        await send_message(message.chat.id, 'ask-full-name')
    else:
        async with state.proxy() as data:
            data["full_name"] = message.text
            await UserRegistration.next()
            await send_message(message.chat.id, 'ask-phone', markup=share_phone_markup)


@dp.message_handler(state=UserRegistration.phone_number, content_types=['contact', 'text'])
async def get_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        phone = str(message.contact.phone_number)
        if re.match(r'^\+998\d{9}$', phone) is None:
            await send_message(message.chat.id, 'wrong-phone')
        else:
            data["phone_number"] = str(message.contact.phone_number)
            await UserRegistration.next()
            await send_message(message.chat.id, 'ask-gender', markup=genders_markup)


@dp.inline_handler()
@dp.message_handler(state=UserRegistration.gender)
async def get_gender(message: Message, state: FSMContext):
    if message.text in ['Erkak', 'Ayol']:
        async with state.proxy() as data:
            data["gender"] = message.text
        await UserRegistration.next()
        await send_message(message.chat.id, 'ask-accent', markup=accents_markup)
    else:
        await send_message(message.chat.id, 'ask-gender', markup=genders_markup)


@dp.message_handler(state=UserRegistration.accent_region)
async def get_accent_region(message: Message, state: FSMContext):
    if (message.text in ["Andijon",
                         "Buxoro",
                         "Farg'ona",
                         "Jizzax",
                         "Sirdaryo",
                         "Xorazm",
                         "Namangan",
                         "Navoiy",
                         "Qashqadaryo",
                         "Qoraqalpog'iston",
                         "Samarqand",
                         "Surxondaryo",
                         "Toshkent viloyati",
                         "Toshkent shahri"]):
        async with state.proxy() as data:
            data["accent_region"] = message.text
        await send_message(message.chat.id, 'ask-birth-year', markup=age_markup)
        await UserRegistration.next()
    else:
        await send_message(message.chat.id, 'ask-accent', markup=accents_markup)


@dp.message_handler(state=UserRegistration.year_of_birth)
async def get_birth_year(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text in ["12-17", "18-24", "25-34", "35-..."]:
            data["year_of_birth"] = message.text
            await send_message(message.chat.id, 'ask-native-language', markup=native_languages_markup)
            await UserRegistration.next()
        else:
            await send_message(message.chat.id, 'ask-birth-year-again')
            return await UserRegistration.year_of_birth.set()
        await UserRegistration.next()


@dp.message_handler(state=UserRegistration.finish)
async def finish(message: Message, state: FSMContext):
    if message.text in [
        "O'zbek tili",
        "Qoraqalpoq tili",
        "Rus tili",
        "Tojik tili",
        "Qozoq tili"
    ]:
        async with state.proxy() as data:
            data["native_language"] = message.text

        await register_user(data, message.chat.id)
        await send_message(message.chat.id, 'register-success', markup=start_markup)
        await state.finish()
    else:
        await send_message(message.chat.id, 'ask-native-language', markup=native_languages_markup)
        return await UserRegistration.finish.set()


@dp.message_handler(text=LEADERBOARD)
@dp.message_handler(commands=['leaderboard'])
async def leaderboard(message: Message):
    await send_message(message.chat.id, 'leaderboard', markup=leader_markup)


@dp.message_handler(text=INSTRUCTIONS)
@dp.message_handler(commands=['instructions'])
async def instructions(message: Message):
    await send_message(message.chat.id, 'instructions')


@dp.message_handler(text=VOICE_LEADERBOARD)
@dp.message_handler(commands=['record_leaderboard'])
async def voice_leaderboard(message: Message):
    headers = await authorization_base64(message.chat.id, {})
    async with aiohttp.ClientSession() as session:
        async with session.get(CLIPS_LEADERBOARD_URL, headers=headers) as get_request:
            leaderboard_dict = await get_request.json()
            print(leaderboard_dict)
    data = {
        '№': [],
        '|FIO|': [],
        '|Yozilgan|': []
    }

    for leader in leaderboard_dict:
        data['№'].append(leader['position'] + 1)
        data['|FIO|'].append(f"{leader['username'][:10]}...")
        data['|Yozilgan|'].append(leader['total'])

    copy_data = data.copy()
    del data['№']
    leaderboard_text = pandas.DataFrame(data=data, index=copy_data['№'])
    leaderboard_text.index.name = '№'
    leaderboard_text = '```' + leaderboard_text.to_string() + '```'

    await bot.send_message(
        message.chat.id,
        leaderboard_text,
        reply_markup=start_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(text=VOTE_LEADERBOARD)
@dp.message_handler(commands=['check_leaderboard'])
async def vote_leaderboard(message: Message):
    headers = await authorization_base64(message.chat.id, {})

    async with aiohttp.ClientSession() as session:
        async with session.get(VOTES_LEADERBOARD_URL, headers=headers) as get_request:
            leaderboard_dict = await get_request.json()
    data = {
        '№': [],
        '|FIO|': [],
        '|Tekshirilgan|': []
    }

    for leader in leaderboard_dict:
        data['№'].append(leader['position'] + 1)
        data['|FIO|'].append(f"{leader['username'][:10]}...")
        data['|Tekshirilgan|'].append(leader['total'])

    copy_data = data.copy()
    del data['№']
    leaderboard_text = pandas.DataFrame(data=data, index=copy_data['№'])
    leaderboard_text.index.name = '№'
    leaderboard_text = '```' + leaderboard_text.to_string() + '```'

    await bot.send_message(
        message.chat.id,
        leaderboard_text,
        reply_markup=start_markup,
        parse_mode=ParseMode.MARKDOWN
    )
