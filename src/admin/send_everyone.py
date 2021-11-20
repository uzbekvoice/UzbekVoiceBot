import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.utils.exceptions import UserDeactivated, BotBlocked

from main import users_db, dp, bot, AdminSendEveryOne
from keyboards.buttons import reject_markup, sure_markup, admin_markup


# Ask admin to send post
async def send_everyone_func(chat_id):
    await bot.send_message(chat_id, 'Перешлите пост для рассылки.', reply_markup=reject_markup)
    await AdminSendEveryOne.ask_post.set()


# Show post sample
@dp.message_handler(state=AdminSendEveryOne.ask_post, content_types=['photo', 'text', 'voice', 'animation', 'video'])
async def admin_post_type(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == 'Отменить':
        await reject_message(chat_id, state)
        return

    buttons = message.reply_markup

    await state.update_data(buttons=buttons)
    await state.update_data(message_id=message.forward_from_message_id)
    await state.update_data(copy_from=chat_id)

    await bot.copy_message(chat_id, chat_id, message.forward_from_message_id)
    await bot.send_message(chat_id, 'Ваш пост будет выглядеть так, начать рассылку?', reply_markup=sure_markup)

    await AdminSendEveryOne.ask_send.set()


# Ask, if the admin sure to start sending notifications
@dp.message_handler(state=AdminSendEveryOne.ask_send)
async def admin_ask_send(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == 'Отменить':
        await reject_message(chat_id, state)
        return

    if admin_message == 'Начать':
        await send_post(chat_id, state)
        return

    await bot.send_message(chat_id, 'Начать рассылку или отменить?', reply_markup=sure_markup)
    await AdminSendEveryOne.ask_send.set()


# Function for sending notifications to all users
async def send_post(chat_id, state):
    data = await state.get_data()
    message_id = data.get('message_id')
    buttons = data.get('buttons')

    await state.finish()

    await bot.send_message(chat_id, 'Рассылка началась!', reply_markup=admin_markup)
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

    admin_stat = "Рассылку получили: {0:,}\n" \
                 "Удалили бота: {1:,}\n" \
                 "Удалились с телеграм: {2:,}\n" \
                 "Прочие ошибки: {3:,}".format(success, blocked, deactivated, errors)

    await bot.send_message(chat_id, admin_stat, reply_markup=admin_markup)
    await sent_message.delete()


# Function to send notification to one user
async def send_copied_post_to_user(user_id, copy_from_chat_id, message_id, buttons):
    try:
        await bot.copy_message(user_id, copy_from_chat_id, message_id, disable_notification=True, reply_markup=buttons)
        return 'success'
    except BotBlocked:
        users_db.set(user_id, 'None')
        return 'blocked'
    except UserDeactivated:
        users_db.set(user_id, 'None')
        return 'deactivated'
    except Exception as err:
        print(err, 'send_copied_post_to_user')
        return False


async def send_progress_message(chat_id, count):
    sent_message = await bot.send_message(chat_id, '{0:,} пользователей получили рассылку'.format(count))
    return sent_message


async def reject_message(chat_id, state):
    await bot.send_message(chat_id, 'Вы отменили действия', reply_markup=admin_markup)
    await state.finish()
