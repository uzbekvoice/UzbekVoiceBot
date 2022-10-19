from time import sleep
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from keyboards.buttons import (
    accents_markup,
    genders_markup,
    native_languages_markup,
    start_markup,
    sweatshirt_size_markup
    )
from utils.helpers import send_message, check_user_info
from main import UserRegistration, dp
from utils.uzbekvoice.helpers import check_if_correct_year, native_language, register_user


# Answer to all bot commands
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    chat_id = message.chat.id

    # await check_user_info(chat_id)
    await UserRegistration.full_name.set()
    await send_message(chat_id, 'start')
    sleep(1)
    await send_message(chat_id, 'ask-full-name')


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: Message):
    chat_id = message.chat.id

    # await check_user_info(chat_id)
    await UserRegistration.full_name.set()
    await send_message(chat_id, 'start')
    sleep(1)
    await send_message(chat_id, 'ask-full-name')


@dp.message_handler(state=UserRegistration.full_name)
async def get_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        data["tg_id"] = chat_id
        data["full_name"] = message.text
        await send_message(chat_id, 'ask-phone', markup=ReplyKeyboardRemove())
        await UserRegistration.next()


@dp.message_handler(state=UserRegistration.full_name)
async def get_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        data["tg_id"] = chat_id
        data["full_name"] = message.text
        await send_message(chat_id, 'ask-phone', markup=ReplyKeyboardRemove())
        await UserRegistration.next()


@dp.message_handler(state=UserRegistration.phone_number)
async def get_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone"] = message.text
        await send_message(data['tg_id'], 'ask-sweatshirt', markup=sweatshirt_size_markup)
        await UserRegistration.next()


@dp.message_handler(state=UserRegistration.sweatshirt_size)
async def get_sweatshirt(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text in ('XS', 'S', 'M', 'L', 'XL', 'XXL'):
            data["sweatshirt"] = message.text
            await send_message(data['tg_id'], 'ask-gender', markup=genders_markup)
            await UserRegistration.next()
        else:
            await send_message(data["tg_id"], 'ask-sweatshirt-again', markup=sweatshirt_size_markup)
            return await UserRegistration.sweatshirt_size.set()


@dp.message_handler(state=UserRegistration.gender)
async def get_gender(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Erkak':
            data["gender"] = "M"
        elif message.text == 'Ayol':
            data["gender"] = "F"

    await send_message(data["tg_id"], 'ask-accent', markup=accents_markup)
    await UserRegistration.next()


@dp.message_handler(state=UserRegistration.accent_region)
async def get_accent_region(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["accent_region"] = message.text

    await send_message(data["tg_id"], 'ask-birth-year', markup=ReplyKeyboardRemove())
    await UserRegistration.next()


@dp.message_handler(state=UserRegistration.year_of_birth)
async def get_birth_year(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if check_if_correct_year(message.text):
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

    await register_user(state)
    await send_message(data["tg_id"], 'register-success', markup=start_markup)
    await state.finish()
