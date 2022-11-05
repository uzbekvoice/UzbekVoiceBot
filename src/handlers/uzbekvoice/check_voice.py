import time
import os
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove

from main import dp, AskUserAction, bot
from keyboards.buttons import start_markup, go_back_markup
from keyboards.inline import yes_no_markup, report_voice_markup
from utils.helpers import send_message, send_voice, edit_reply_markup, delete_message_markup, IsRegistered, \
    IsBlockedUser, IsSubscribedChannel
from utils.uzbekvoice.helpers import get_voice_to_check, download_file, get_audio_duration, enqueue_operation
import utils.uzbekvoice.db as db

from data.messages import VOICE_INCORRECT, VOICE_CORRECT, VOICE_REPORT, SKIP_STEP, REPORT_TEXT_1, \
    REPORT_TEXT_2, REPORT_TEXT_3, REPORT_TEXT_4, REPORT_TEXT_5, CONFIRM_VOICE_TEXT, REJECT_VOICE_TEXT, \
    VOICE_LEADERBOARD, VOTE_LEADERBOARD, CHECK_VOICE, CANCEL_MESSAGE, LISTEN_AUDIO_FIRST


# Handler that answers to Check Voice message
@dp.message_handler(IsRegistered(), IsBlockedUser(), IsSubscribedChannel(), text=CHECK_VOICE)
async def initial_check_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await send_message(chat_id, 'ask-check-voice', markup=go_back_markup)
    await ask_to_check_new_voice(chat_id, state)


# Handler that answers to cancel message
@dp.message_handler(state=AskUserAction.all_states, text=CANCEL_MESSAGE)
async def cancel_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'reply_message_id' in data:
        reply_message_id = data['reply_message_id']
        await delete_message_markup(message.chat.id, reply_message_id)
    await send_message(message.chat.id, 'action-rejected', markup=start_markup)
    await state.finish()


# Handler that receives all unnecessary messages in ask action state
@dp.message_handler(state=AskUserAction.ask_action, content_types=['text'])
async def ask_action_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'reply_message_id' in data:
        reply_message_id = data['reply_message_id']
        await send_message(message.chat.id, 'ask-check-voice-again', markup=go_back_markup, reply=reply_message_id)
    else:
        await cancel_message_handler(message, state)


# Handler that receives action on pressed accept, reject, skip and report inline button
@dp.callback_query_handler(state=AskUserAction.ask_action,
                           regexp=r'^(accept|reject|skip|report|submit|home).*$')
async def ask_action_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    if (call_data == 'home'):
        await cancel_message_handler(call.message, state)
        await state.finish()
        return

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    command, voice_id = call_data.split('/')
    data = await state.get_data()
    confirm_state = data['confirm_state'] if 'confirm_state' in data else None
    clip_duration = data['clip_duration'] if 'clip_duration' in data else 0
    if command == 'report':
        await call.answer()
        await edit_reply_markup(chat_id, message_id, report_voice_markup(voice_id))
        await AskUserAction.report_type.set()
        return

    if command != 'submit':
        await call.answer()
        await state.update_data(confirm_state=command)
        try:
            await edit_reply_markup(chat_id, message_id, yes_no_markup(voice_id, command))
        except:
            pass
        await AskUserAction.ask_action.set()
        return

    command = confirm_state
    last_sent_time = data['last_sent_time']
    if time.time() - last_sent_time < clip_duration + 0.3 and command in ['accept', 'reject']:
        try:
            db.add_user_violation(chat_id, 'vote_streak')
        except Exception as e:
            print(e)
        return await call.answer(LISTEN_AUDIO_FIRST, show_alert=True)
    else:
        await call.answer()

    if command == 'skip':
        await call.message.delete()
        await enqueue_operation({'type': 'skip_clip', 'voice_id': voice_id}, chat_id)
        await ask_to_check_new_voice(chat_id, state)
        return

    if command in ['accept', 'reject']:
        await call.message.delete_reply_markup()
        await enqueue_operation({'type': 'vote', 'voice_id': voice_id, 'command': command}, chat_id)
        await ask_to_check_new_voice(chat_id, state)
        return
    print("Error in ask_action_handler", command, voice_id, call_data)


# Handler that receives action on pressed report inline button
@dp.callback_query_handler(state=AskUserAction.report_type, regexp=r'^(report|back).*$')
async def ask_report_type_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    command, voice_id = call_data.split('/')
    data = await state.get_data()
    confirm_state = data['confirm_state'] if 'confirm_state' in data else None

    if command == 'back':
        await edit_reply_markup(chat_id, message_id, yes_no_markup(voice_id, confirm_state))
        await AskUserAction.ask_action.set()
        return
    else:
        await call.message.delete_reply_markup()
        await enqueue_operation({'type': 'report_clip', 'voice_id': voice_id, 'command': command}, chat_id)
        await send_message(chat_id, 'reported', parse=ParseMode.MARKDOWN)
        await ask_to_check_new_voice(chat_id, state)


async def ask_to_check_new_voice(chat_id, state):
    voice = await get_voice_to_check(chat_id, state)
    if voice is None:
        await send_message(chat_id, 'no-voices-to-check', markup=start_markup)
        await state.finish()
        return
    text_to_check = voice['sentence']['text']
    voice_id = voice['id']
    voice_url = voice['audioSrc']
    voice_file = await download_file(voice_url, '{}_{}'.format(chat_id, voice_id))
    message_id = await send_voice(chat_id, open(voice_file, 'rb'), 'caption', args=text_to_check)
    clip_duration = get_audio_duration(voice_file)
    await state.update_data(last_sent_time=time.time())
    await state.update_data(clip_duration=clip_duration)
    await state.update_data(confirm_state=None)
    await edit_reply_markup(chat_id, message_id, yes_no_markup(voice_id, None))
    await state.update_data(reply_message_id=message_id)
    await AskUserAction.ask_action.set()
    os.remove(voice_file)
