from utils.uzbekvoice.db import get_user
from main import dp, bot
from aiogram.types import Message

from data.messages import MY_PROFILE
from utils.helpers import send_message


@dp.message_handler(text=MY_PROFILE)
@dp.message_handler(commands=['my_profile'])
async def instructions(message: Message):
    user = get_user(message.chat.id)
    my_profile = f"👤 Mening profilim:\n\nIsm: {user[4]}"
    await bot.send_message(message.chat.id, my_profile)