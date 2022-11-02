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
from redis import Redis
from rq import Queue

load_dotenv(find_dotenv())

loop = asyncio.get_event_loop()
storage = MemoryStorage()


WEBHOOK_HOST = getenv('WEBHOOK_HOST')
WEBHOOK_PATH = '/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 80

bot = Bot(getenv("BOT_TOKEN"), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage, loop=loop)

users_db = redis.StrictRedis(host='localhost', port=6379, db=1)

BASE_DIR: Path = Path(__file__).resolve().parent.parent
ADMINS_ID: list = list(map(int, getenv("ADMINS_ID").split()))

REDIS_URL = getenv("REDIS_URL")
queue = Queue(connection=Redis.from_url(REDIS_URL), name="high") if REDIS_URL else None


class UserRegistration(StatesGroup):
    full_name = State()
    phone_number = State()
    gender = State()
    native_language = State()
    accent_region = State()
    year_of_birth = State()
    finish = State()


class AdminSendEveryOne(StatesGroup):
    ask_post = State()
    ask_send = State()


class AdminSendCertain(StatesGroup):
    ask_post = State()
    ask_correct = State()
    ask_users = State()
    ask_send = State()


class AdminBanCertain(StatesGroup):
    ask_correct = State()
    ask_users = State()


class AdminUnbanCertain(StatesGroup):
    ask_correct = State()
    ask_users = State()


class AskUserVoice(StatesGroup):
    ask_voice = State()
    ask_confirm = State()
    confirm_action = State()
    report_type = State()


class AskUserAction(StatesGroup):
    ask_action = State()
    confirm_action = State()
    report_type = State()


class EditProfile(StatesGroup):
    choose_field_to_edit = State()
    edit_age = State()
    edit_language = State()
    edit_accent = State()
