import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove


from main import dp, bot, AdminSendCertain
from keyboards.buttons import admin_markup, sure_markup, yes_no_markup
from .send_everyone import send_copied_post_to_user, send_progress_message


# Ask admin to send post
async def send_certain_func(chat_id):
    await bot.send_message(chat_id,
                           'Send the post content for notification of certain users 👇',
                           reply_markup=ReplyKeyboardRemove()
                           )
    await AdminSendCertain.ask_post.set()


# Canceled message
@dp.message_handler(state=AdminSendCertain.all_states, text='Cancel')
async def admin_reject_handler(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'You have canceled notification  ✅', reply_markup=admin_markup)
    await state.finish()


# Ask if the admin sure about the contents of the notification
@dp.message_handler(state=AdminSendCertain.ask_post, content_types=['photo', 'text', 'voice', 'animation', 'video'])
async def admin_ask_post(message: Message, state: FSMContext):
    chat_id = message.chat.id

    await state.update_data(message_id=message.message_id)

    await bot.copy_message(chat_id, chat_id, message.message_id)
    await bot.send_message(
        chat_id,
        'Your notification will look like this, do you confirm?',
        reply_markup=yes_no_markup
    )
    await AdminSendCertain.ask_correct.set()


# Ask users list
@dp.message_handler(state=AdminSendCertain.ask_correct)
async def admin_ask_correct(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == '✅ Yes':
        await bot.send_message(
            chat_id,
            "Write tg_id's of the users comma-separated.\nExample: 123123, 432432, 15645532",
            reply_markup=ReplyKeyboardRemove()
        )
        await AdminSendCertain.ask_users.set()
        return
    elif admin_message == '🚫 No':
        await state.finish()
        await bot.send_message(chat_id, 'Message canceled ✅', reply_markup=admin_markup)
        return

    await bot.send_message(
        chat_id,
        'Your notification will look like this, do you confirm?',
        reply_markup=yes_no_markup
    )
    await AdminSendCertain.ask_correct.set()


# Ask to begin notification
@dp.message_handler(state=AdminSendCertain.ask_users)
async def admin_ask_users(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    await state.update_data(users=admin_message)

    await bot.send_message(chat_id, 'Begin notification or cancel?', reply_markup=sure_markup)
    await AdminSendCertain.ask_send.set()


# Sending function activator
@dp.message_handler(state=AdminSendCertain.ask_send)
async def admin_ask_send(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == '✅ Start':
        await send_post(chat_id, state)
        return
    elif admin_message == '🚫 Cancel':
        await state.finish()
        await bot.send_message(chat_id, 'Notification canceled 🚫', reply_markup=admin_markup)
        return
    await bot.send_message(chat_id, 'Begin notification or cancel?', reply_markup=sure_markup)
    await AdminSendCertain.ask_send.set()


# Function for sending notifications to certain users
async def send_post(chat_id, state):
    data = await state.get_data()
    message_id = data.get('message_id')
    users = data.get('users').split(', ')

    await state.finish()

    await bot.send_message(chat_id, 'Notification to certain users begin!', reply_markup=admin_markup)

    tasks = []
    send_count = 0
    blocked = 0
    deactivated = 0
    errors = 0
    success = 0
    sent_message = await send_progress_message(chat_id, success)

    for user in users:
        tasks.append(asyncio.ensure_future(send_copied_post_to_user(user, chat_id, message_id, ReplyKeyboardRemove())))
        send_count += 1
        if send_count >= 30:
            send_count = 0
            await asyncio.sleep(1)

    gather_results = await asyncio.gather(*tasks)
    for result in gather_results:
        if result == 'success':
            success += 1
        elif result == 'deactivated':
            deactivated += 1
        elif result == 'blocked':
            blocked += 1
        else:
            errors += 1

    admin_stat = "Notification received: {0:,}\n" \
                 "Deleted the telegram: {2:,}\n" \
                 "Blocked the bot: {1:,}\n" \
                 "Other reasons: {3:,}".format(success, blocked, deactivated, errors)

    await bot.send_message(chat_id, admin_stat, reply_markup=admin_markup)
    await sent_message.delete()









