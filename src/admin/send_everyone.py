import asyncio

from sqlalchemy import select
from sqlalchemy.sql import exists
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import UserDeactivated, BotBlocked


from main import users_db, dp, bot, AdminSendEveryOne
from keyboards.buttons import reject_markup, sure_markup, admin_markup
from utils.uzbekvoice.db import engine, user_table, session, User


# Ask admin to send post
async def send_everyone_func(chat_id):
    await bot.send_message(chat_id, 'Send the post for push-notification.', reply_markup=reject_markup)
    await AdminSendEveryOne.ask_post.set()


# Show post sample
@dp.message_handler(state=AdminSendEveryOne.all_states, text='Cancel')
async def admin_reject_handler(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'You have canceled push-notification.', reply_markup=admin_markup)
    await state.finish()


# Show post sample
@dp.message_handler(state=AdminSendEveryOne.ask_post, content_types=['photo', 'text', 'voice', 'animation', 'video'])
async def admin_ask_post(message: Message, state: FSMContext):
    chat_id = message.chat.id
    buttons = message.reply_markup

    await state.update_data(buttons=buttons)
    await state.update_data(message_id=message.message_id)
    await state.update_data(copy_from=chat_id)

    await bot.copy_message(chat_id, chat_id, message.message_id)
    await bot.send_message(chat_id,
                           'Your push-notification will look like this, start sending it to users?',
                           reply_markup=sure_markup)

    await AdminSendEveryOne.ask_send.set()


# Ask if the admin sure to start sending notifications
@dp.message_handler(state=AdminSendEveryOne.ask_send)
async def admin_ask_send(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == 'Начать':
        await send_post(chat_id, state)
        return

    await bot.send_message(chat_id, 'Begin push-notification or cancel?', reply_markup=sure_markup)
    await AdminSendEveryOne.ask_send.set()


# Function for sending notifications to all users
async def send_post(chat_id, state):
    data = await state.get_data()
    message_id = data.get('message_id')
    buttons = data.get('buttons')

    await state.finish()

    await bot.send_message(chat_id, 'Push-notification begin!', reply_markup=admin_markup)
    users_id = users_db.keys()

    blocked = 0
    deactivated = 0
    errors = 0
    success = 0

    sent_message = await send_progress_message(chat_id, success)

    first_users_to_send = []
    for user_id in users_id:
        if len(first_users_to_send) < 20:
            first_users_to_send.append(int(user_id))
            continue

        tasks = []
        for user_to_send in first_users_to_send:
            tasks.append(asyncio.ensure_future(send_copied_post_to_user(user_to_send, chat_id, message_id, buttons)))

        gather_results = await asyncio.gather(*tasks)
        for result in gather_results:
            if result == 'success':
                success += 1
                if success % 500 == 0:
                    await sent_message.delete()
                    sent_message = await send_progress_message(chat_id, success)
            elif result == 'blocked':
                blocked += 1
            elif result == 'deactivated':
                deactivated += 1
            else:
                errors += 1

        await asyncio.sleep(1)
        first_users_to_send = []

    admin_stat = "Notification received: {0:,}\n" \
                 "Blocked the bot: {1:,}\n" \
                 "Deleted the telegram: {2:,}\n" \
                 "Other reasons: {3:,}".format(success, blocked, deactivated, errors)

    await bot.send_message(chat_id, admin_stat, reply_markup=admin_markup)
    await sent_message.delete()


# Function to send copy message-notification to one user
async def send_copied_post_to_user(user_id, copy_from_chat_id, message_id, buttons):
    try:
        await bot.copy_message(user_id, copy_from_chat_id, message_id, disable_notification=True, reply_markup=buttons)
        return 'success'
    except BotBlocked:
        return 'blocked'
    except UserDeactivated:
        return 'deactivated'
    except Exception as err:
        print(err, 'send_copied_post_to_user')
        return False


async def send_progress_message(chat_id, count):
    sent_message = await bot.send_message(chat_id, '{0:,} users received the push-notification.'.format(count))
    return sent_message


# Function to send message to the list of users
@dp.message_handler(commands=['admin_admin_send'])
async def send_post_to_user(message: Message):
    telephones = [
        '+998946526622',
    ]
    for telephone in telephones:
        with engine.connect() as conn:
            q = session.query(exists().where(user_table.c.phone_number == telephone)).scalar()
            if q:
                q = select(user_table).where(user_table.c.phone_number == telephone)
                user = conn.execute(q).first()
                text = """
                Assalomu alaykum, hurmatli foydalanuvchi! 
                
                Ba'zi texnik nosozliklar tufayli sizning ismi sharifingiz "Ro'yxatdan o'tish" deb saqlangan. 
                Iltimos @adamsaido ga to'liq ismi sharifingiz va telefon raqamangizni yozib qoldiring.
                
                Hurmat bilan UzbekVoice jamoasi
                """
                await bot.send_message(user.tg_id, text)
