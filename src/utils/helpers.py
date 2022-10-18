import json

from main import ADMINS_ID
from data.messages import msg_dict

from main import bot, users_db
from keyboards.buttons import start_markup


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


async def send_voice(chat_id, file_to_send, caption, args=None, markup=None):
    msg_to_send = await user_msg(caption, args)
    sent_voice = await bot.send_voice(chat_id, file_to_send, caption=msg_to_send, reply_markup=markup)
    return sent_voice.message_id


async def edit_reply_markup(chat_id, message_id, markup):
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)


# Get user message
async def user_msg(message_str, args):
    if args is None:
        user_message = msg_dict[message_str]
    else:
        if type(args) != tuple:
            user_message = msg_dict[message_str].format(args)
        else:
            user_message = msg_dict[message_str].format(*args)

    return user_message


# Save user id If it does not exist in DB
async def check_user_info(chat_id):
    user_info_db = users_db.get(chat_id)
    if user_info_db is None:
        user_info = {}
        users_db.set(chat_id, json.dumps(user_info))
    else:
        user_info = json.loads(user_info_db)

    return user_info


# Send notification to admin that bot started working
async def on_startup(args):
    for one_admin_id in ADMINS_ID:
        await send_message(one_admin_id, 'admin-bot-start', markup=start_markup)

