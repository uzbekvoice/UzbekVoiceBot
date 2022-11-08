from aiogram.types import Message
from aiogram.dispatcher import FSMContext


from main import dp, bot, AdminBanCertain
from utils.uzbekvoice.db import User, session
from keyboards.buttons import admin_markup, yes_no_markup


async def block_certain_func(chat_id):
    message_txt = 'Send tg_id of users comma-separated. If it\'s only one user, just one id without comma after it.\n' \
                  'Example: 14878234, 4241231, 5545456 or 6594834'
    await bot.send_message(chat_id, message_txt)
    await AdminBanCertain.ask_correct.set()


# Ask to begin notification
@dp.message_handler(state=AdminBanCertain.ask_correct, content_types=['text'])
async def admin_ask_users(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text
    await state.update_data(users=admin_message)

    await bot.send_message(chat_id, 'Ban users or cancel the action?', reply_markup=yes_no_markup)
    await AdminBanCertain.ask_users.set()


# Sending function activator
@dp.message_handler(state=AdminBanCertain.ask_users)
async def admin_ask_send(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == '✅ Yes':
        await admin_block_users(message, state)
        return
    elif admin_message == '🚫 No':
        await state.finish()
        await bot.send_message(chat_id, 'Action canceled 🚫', reply_markup=admin_markup)
        return
    await bot.send_message(chat_id, 'Ban users or cancel the action?', reply_markup=yes_no_markup)
    await AdminBanCertain.ask_users.set()


async def admin_block_users(message: Message, state: FSMContext):
    chat_id = message.chat.id
    data = await state.get_data()
    users = data.get('users').split(', ')

    for user_id in users:
        session.query(User).filter(User.tg_id == user_id).update({'is_banned': True})
    session.commit()
    await state.finish()
    await bot.send_message(chat_id, 'Users have been baned ✅', reply_markup=admin_markup)









