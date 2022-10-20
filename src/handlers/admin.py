from aiogram.types import Message

from data.messages import SEND_EVERYONE, BOT_STATISTICS

from admin.send_everyone import send_everyone_func
from admin.get_bot_stat import get_bot_stat_func

from keyboards.buttons import admin_markup
from main import bot, dp, ADMINS_ID


# Answer to /admin command to get list of admin commands
@dp.message_handler(chat_id=ADMINS_ID, commands=['admin'])
async def ask_admin_commands(message: Message):
    await bot.send_message(message.chat.id, 'Все команды админа', reply_markup=admin_markup)


# Answer to all admin commands
@dp.message_handler(chat_id=ADMINS_ID, text=[SEND_EVERYONE, BOT_STATISTICS])
async def admin_commands(message: Message):
    chat_id = message.chat.id
    admin_command = message.text

    # Function to send notification to all users
    if admin_command == SEND_EVERYONE:
        await send_everyone_func(chat_id)

    # Function to get bot statistics
    elif admin_command == BOT_STATISTICS:
        await get_bot_stat_func(chat_id)
