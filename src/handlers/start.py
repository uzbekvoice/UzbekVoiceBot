import pandas
import aiohttp
from aiogram.types import Message, ParseMode
from aiogram.dispatcher import FSMContext

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
from utils.uzbekvoice.helpers import native_language
from data.messages import LEADERBOARD, VOTE_LEADERBOARD, VOICE_LEADERBOARD
from utils.uzbekvoice.helpers import register_user, HEADERS, VOTES_LEADERBOARD_URL, CLIPS_LEADERBOARD_URL, \
    authorization_base64


@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    chat_id = message.chat.id

    if db.user_exists(chat_id):
        await send_message(chat_id, 'welcome-text', markup=start_markup)
    else:
        await send_message(chat_id, 'start', markup=register_markup)


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: Message):
    chat_id = message.chat.id

    if db.user_exists(chat_id):
        await send_message(chat_id, 'welcome-text', markup=start_markup)
    else:
        await send_message(chat_id, 'start', markup=register_markup)


# Answer to all bot commands
@dp.message_handler(text="👤 Ro'yxatdan o'tish")
async def start_command(message: Message):
    chat_id = message.chat.id
    await UserRegistration.full_name.set()
    await send_message(chat_id, 'ask-full-name')


@dp.message_handler(state=UserRegistration.full_name)
async def get_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        data["tg_id"] = chat_id
        data["full_name"] = message.text
        await UserRegistration.next()
        await send_message(chat_id, 'ask-phone', markup=share_phone_markup)


@dp.message_handler(state=UserRegistration.full_name)
async def get_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        data["tg_id"] = chat_id
        data["full_name"] = message.text
        await UserRegistration.next()
        await send_message(chat_id, 'ask-phone', markup=share_phone_markup)


@dp.message_handler(state=UserRegistration.phone_number, content_types=['contact', 'text'])
async def get_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone_number"] = str(message.contact.phone_number)
        await UserRegistration.next()
        await send_message(data['tg_id'], 'ask-gender', markup=genders_markup)


@dp.inline_handler()
@dp.message_handler(state=UserRegistration.gender)
async def get_gender(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Erkak':
            data["gender"] = "M"
        elif message.text == 'Ayol':
            data["gender"] = "F"

    await UserRegistration.next()
    await send_message(data["tg_id"], 'ask-accent', markup=accents_markup)


@dp.message_handler(state=UserRegistration.accent_region)
async def get_accent_region(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["accent_region"] = message.text

    await send_message(data["tg_id"], 'ask-birth-year', markup=age_markup)
    await UserRegistration.next()


@dp.message_handler(state=UserRegistration.year_of_birth)
async def get_birth_year(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text in ["12-17", "18-24", "25-34", "35-..."]:
            data["year_of_birth"] = message.text
            await send_message(data["tg_id"], 'ask-native-language', markup=native_languages_markup)
            await UserRegistration.next()
        else:
            await send_message(data["tg_id"], 'ask-birth-year-again')
            return await UserRegistration.year_of_birth.set()
        await UserRegistration.next()


@dp.message_handler(state=UserRegistration.finish)
async def finish(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["native_language"] = native_language(message.text)

    await register_user(data)
    await send_message(data["tg_id"], 'register-success', markup=start_markup)
    await state.finish()


@dp.message_handler(lambda message: message.text == LEADERBOARD or message.text == '/leaderboard')
async def leaderboard(message: Message):
    await send_message(message.chat.id, 'leaderboard', markup=leader_markup)


@dp.message_handler(lambda message: message.text == '/record_leaderboard' or message.text == VOICE_LEADERBOARD)
async def voice_leaderboard(message: Message):
    await authorization_base64(message.chat.id)
    print(HEADERS)

    async with aiohttp.ClientSession() as session:
        async with session.get(CLIPS_LEADERBOARD_URL, headers=HEADERS) as get_request:
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


@dp.message_handler(lambda message: message.text == '/check_leaderboard' or message.text == VOTE_LEADERBOARD)
async def vote_leaderboard(message: Message):
    await authorization_base64(message.chat.id)

    async with aiohttp.ClientSession() as session:
        async with session.get(VOTES_LEADERBOARD_URL, headers=HEADERS) as get_request:
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
