import aiohttp
from utils.uzbekvoice.db import get_user
from main import dp, bot
from aiogram.types import Message

from data.messages import MY_PROFILE, MY_RATING
from utils.uzbekvoice.helpers import CLIPS_LEADERBOARD_URL, VOTES_LEADERBOARD_URL, authorization_base64


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


@dp.message_handler(text=MY_RATING)
@dp.message_handler(commands=['my_stats'])
async def vote_leaderboard(message: Message):
    headers = await authorization_base64(message.chat.id, {})

    async with aiohttp.ClientSession() as session:
        async with session.get(VOTES_LEADERBOARD_URL, headers=headers) as get_request:
            votes_leaderboard = await get_request.json()
            given_votes = 0
            votes_position = 0
            for i in votes_leaderboard:
                if i['you'] == True:
                    given_votes = i['total']
                    votes_position = i['position']

    async with aiohttp.ClientSession() as session:
        async with session.get(CLIPS_LEADERBOARD_URL, headers=headers) as get_request:
            clips_leaderboard = await get_request.json()
            recorded_clips = 0
            clips_position = 0
            for i in clips_leaderboard:
                if i['you'] == True:
                    recorded_clips = i['total']
                    clips_position = i['position']

    my_stats = [
        f"<b>🏆 Sizning yutuqlaringiz:</b>\n",
        f"🗣 Yozilgan ovozlar: {recorded_clips}",
        f"📊 Ovoz yozishdagi o'rningiz: {clips_position}\n",
        f"🎧 Tekshirilgan ovozlar: {given_votes}",
        f"📊 Ovoz tekshirishdagi o'rningiz: {votes_position}"
    ]

    await bot.send_message(message.chat.id, "\n".join(my_stats), parse_mode="HTML")