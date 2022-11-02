from aiogram.dispatcher.filters import Filter
from aiogram.types import Message, ReplyKeyboardRemove
from utils.uzbekvoice import db
from data.messages import msg_dict
from main import bot, ADMINS_ID, dp
from keyboards.buttons import start_markup, register_markup
from .uzbekvoice import db


# Function to send waiting message
async def send_message(chat_id, msg, args=None, markup=None, parse=None, reply=None):
    try:
        msg_to_send = await user_msg(msg, args)
        sent_message = await bot.send_message(chat_id, msg_to_send, reply_markup=markup, parse_mode=parse,
                                              disable_web_page_preview=True, disable_notification=True,
                                              reply_to_message_id=reply)
        return sent_message.message_id
    except Exception as err:
        print('Error in send_message', err)


async def delete_message_markup(chat_id, message_id):
    try:
        await bot.edit_message_reply_markup(chat_id, message_id)

    except Exception as err:
        print('Error in delete_message_markup', err)


async def delete_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as err:
        print('Error in delete_message', err)


async def send_voice(chat_id, file_to_send, caption, args=None, markup=None, parse=None):
    msg_to_send = await user_msg(caption, args)
    sent_voice = await bot.send_voice(chat_id, file_to_send, caption=msg_to_send, reply_markup=markup, parse_mode=parse)
    return sent_voice.message_id


async def edit_reply_markup(chat_id, message_id, markup):
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)


# Get user message
async def user_msg(message_str, args):
    if args is None:
        if not (message_str in msg_dict):
            return message_str
        else:
            user_message = msg_dict[message_str]
    else:
        if type(args) != tuple:
            user_message = msg_dict[message_str].format(args)
        else:
            user_message = msg_dict[message_str].format(*args)

    return user_message


# Send notification to admin that bot started working
async def on_startup(args):
    for one_admin_id in ADMINS_ID:
        await send_message(one_admin_id, 'admin-bot-start', markup=start_markup)


# Filter for checking registration of user
class IsRegistered(Filter):
    key = "is_registered"

    async def check(self, message: Message):

        chat_id = message.chat.id
        if db.user_exists(chat_id):
            return True
        else:
            await send_message(chat_id, 'register', markup=register_markup)


# Filter for checking whether user is banned
class IsBlockedUser(Filter):
    key = "is_blocked_user"

    async def check(self, message: Message):
        chat_id = message.chat.id
        if db.user_banned(chat_id):
            await send_message(chat_id, 'banned', markup=ReplyKeyboardRemove())
            return False
        else:
            return True


# Filter for checking whether user is banned
class IsSubscribedChannel(Filter):
    key = "is_subscribed_channel"

    async def check(self, message: Message):
        chat_id = message.chat.id
        check_member = await bot.get_chat_member(-1001798621689, chat_id)
        if check_member.status not in ["member", "creator", "administrator"]:
            await send_message(chat_id, 'channel')
            return False
        else:
            return True


dp.filters_factory.bind(IsRegistered)
dp.filters_factory.bind(IsBlockedUser)
dp.filters_factory.bind(IsSubscribedChannel)




