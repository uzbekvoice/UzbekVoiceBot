import aiohttp
import pandas
from datetime import datetime
from aiogram.types import Message, ParseMode

from keyboards.buttons import start_markup
from main import bot, dp
from data.messages import VOICE_LEADERBOARD, VOTE_LEADERBOARD, OVERALL_STATS
from utils.helpers import IsRegistered, IsSubscribedChannel
from utils.uzbekvoice.common_voice import CLIPS_LEADERBOARD_URL, VOTES_LEADERBOARD_URL, RECORDS_STAT_URL, \
    ACTIVITY_STAT_URL
from utils.uzbekvoice.helpers import authorization_token


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=VOICE_LEADERBOARD)
async def voice_leaderboard(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id)
    }
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


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=VOTE_LEADERBOARD)
async def vote_leaderboard(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id)
    }

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


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=OVERALL_STATS)
async def stats(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id)
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(RECORDS_STAT_URL, headers=headers) as get_request:
            stats_dict = await get_request.json()
        async with session.get(ACTIVITY_STAT_URL, headers=headers) as get_request:
            activity_dict = await get_request.json()

    latest_records = stats_dict[-1]
    latest_activity = activity_dict[-1]

    overall_records = int(int(latest_records['total']) / 3600)  # 1 hour = 3600 seconds
    checked_records = int(int(latest_records['valid']) / 3600)
    stats_hour = latest_activity['date']
    stats_hour = datetime.strptime(stats_hour, '%Y-%m-%dT%H:%M:%S.%fZ').hour + 5
    users_count = latest_activity['value']

    stat_message = f"""
🗣️ Umumiy yozilgan: {overall_records} soat

✅ Tekshirilgan yozuvlar: {checked_records} soat

☑️ 2-bosqich maqsadi: 2000 soat tekshirilgan yozvular

⌛ Bugun {stats_hour}:00da aktivlar soni: {users_count}
    """

    await bot.send_message(
        message.chat.id,
        text=stat_message,
        reply_markup=start_markup,
        parse_mode=ParseMode.MARKDOWN
    )
