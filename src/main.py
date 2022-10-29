import asyncio

import redis

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from dotenv import load_dotenv
from os import getenv

load_dotenv()

from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

loop = asyncio.get_event_loop()
storage = MemoryStorage()
bot = Bot(getenv("BOT_TOKEN"), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage, loop=loop)

users_db = redis.StrictRedis(host='localhost', port=6379, db=1)

BASE_DIR: Path = Path(__file__).resolve().parent.parent
ADMINS_ID: list = list(map(int, getenv("ADMINS_ID").split()))


class UserRegistration(StatesGroup):
    full_name = State()
    phone_number = State()
    gender = State()
    accent_region = State()
    year_of_birth = State()
    native_language = State()
    finish = State()


class AdminSendEveryOne(StatesGroup):
    ask_post = State()
    ask_send = State()


class AskUserVoice(StatesGroup):
    ask_voice = State()
    ask_confirm = State()
    confirm_action = State()
    report_type = State()


class AskUserAction(StatesGroup):
    ask_action = State()
    confirm_action = State()
    report_type = State()
