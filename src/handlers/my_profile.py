from utils.uzbekvoice.db import get_user
from main import dp, bot
from aiogram.types import Message

from data.messages import MY_PROFILE


@dp.message_handler(text=MY_PROFILE)
@dp.message_handler(commands=['my_profile'])
async def instructions(message: Message):
    user = get_user(message.chat.id)
    my_profile = f"<b>👤 Mening profilim:</b>\n\nIsm: <code>{user[4]}</code>\nTelefon raqam: <code>{user[5]}</code>\nYosh oralig'i: <code>{user[9]}</code>\nJinsi: <code>{'Erkak' if user[7] == 'M' else 'Ayol'}</code>\nShevasi: <code>{user[8]}</code>\nOna-tili: <code>{user[10]}</code>"
    await bot.send_message(message.chat.id, my_profile, parse_mode="HTML")