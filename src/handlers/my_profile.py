from utils.uzbekvoice.db import get_user
from main import dp, bot
from aiogram.types import Message

from data.messages import MY_PROFILE
from utils.helpers import send_message

# Telefon raqam: +998902646366
# Yosh oralig'i: 16-24
# Jinsi: Erkak
# Shevasi: Jizzax
# Ona-tili: O'zbek tili

languages = [
    "O'zbek tili",
    "Qoraqalpoq tili",
    "Rus tili",
    "Tojik tili",
    "Qozoq tili"
]

@dp.message_handler(text=MY_PROFILE)
@dp.message_handler(commands=['my_profile'])
async def my_profile(message: Message):
    user = get_user(message.chat.id)
    my_profile = [
        f"👤 Mening profilim:\n\n"
        f"Ism: <code>{user['full_name']}</code>",
        f"Telefon raqam: <code>{user['phone_number']}</code>",
        f"Yosh oralig'i: <code>{user['year_of_birth']}</code>",
        f"Jinsi: <code>{user['gender']}</code>",
        f"Ona-tili: <code>{user['native_language']}</code>",
        f"Shevasi: <code>{user['accent_region']}</code>",
    ]
    await bot.send_message(message.chat.id, '\n'.join(my_profile), parse_mode='HTML')
