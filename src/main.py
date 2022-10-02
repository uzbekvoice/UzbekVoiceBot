import asyncio

import redis

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import BOT_TOKEN

loop = asyncio.get_event_loop()
storage = MemoryStorage()
bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage, loop=loop)

users_db = redis.StrictRedis(host='localhost', port=6379, db=1)


class AdminSendEveryOne(StatesGroup):
    ask_post = State()
    ask_send = State()


class AskUserVoice(StatesGroup):
    ask_voice = State()
    ask_confirm = State()
    report_type = State()


class AskUserAction(StatesGroup):
    ask_action = State()
    report_type = State()
