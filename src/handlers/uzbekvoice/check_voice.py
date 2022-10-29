import os
from time import sleep

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
import re
from main import dp, AskUserAction
from keyboards.buttons import start_markup, go_back_markup
from keyboards.inline import yes_no_markup, report_voice_markup
from utils.helpers import send_message, send_voice, edit_reply_markup, delete_message_markup
from utils.uzbekvoice.helpers import get_voices_to_check, download_file, send_voice_vote, report_function, skip_voice

from data.messages import VOICE_INCORRECT, VOICE_CORRECT, VOICE_REPORT, SKIP_STEP, REPORT_TEXT_1, \
    REPORT_TEXT_2, REPORT_TEXT_3, REPORT_TEXT_4, REPORT_TEXT_5, CONFIRM_VOICE_TEXT, REJECT_VOICE_TEXT, \
    VOICE_LEADERBOARD, VOTE_LEADERBOARD, CHECK_VOICE, CANCEL_MESSAGE


# Handler that answers to Check Voice message
@dp.message_handler(lambda message: message.text == CHECK_VOICE or message.text == '/check')
async def initial_check_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await send_message(chat_id, 'ask-check-voice', markup=go_back_markup)
    await ask_to_check_new_voice(chat_id, state)


# Handler that answers to cancel message
@dp.message_handler(state=AskUserAction.all_states, text=CANCEL_MESSAGE)
async def cancel_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await delete_message_markup(message.chat.id, reply_message_id)
    await send_message(message.chat.id, 'action-rejected', markup=start_markup)
    await state.finish()


# Handler that receives all unnecessary messages in ask action state
@dp.message_handler(state=AskUserAction.ask_action, content_types=['text'])
async def ask_action_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await send_message(message.chat.id, 'ask-check-voice-again', markup=go_back_markup, reply=reply_message_id)


# Handler that receives action on pressed accept, reject, skip and report inline button
@dp.callback_query_handler(lambda c: re.match(r'(accept|reject|skip|report).*', str(c.data)) is not None,
                           state=AskUserAction.ask_action)
async def ask_action_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    command, voice_id = call_data.split('/')

    await call.answer()

    if command == 'report':
        await edit_reply_markup(chat_id, message_id, report_voice_markup(voice_id))
        await AskUserAction.report_type.set()
        return

    elif command == 'skip':
        await skip_voice(voice_id, chat_id)
        await call.message.delete()
        await ask_to_check_new_voice(chat_id, state)
        return

    elif command in ['accept', 'reject']:
        await call.message.delete_reply_markup()
        await send_voice_vote(voice_id, command == 'accept', chat_id)
        await ask_to_check_new_voice(chat_id, state)
        return
    print("Error in ask_action_handler", command, voice_id, call_data)


# Handler that receives action on pressed report inline button
@dp.callback_query_handler(lambda c: re.match(r'(report|back).*', str(c.data)) is not None,
                           state=AskUserAction.report_type)
async def ask_report_type_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    command, voice_id = call_data.split('/')
    if command == 'back':
        await edit_reply_markup(chat_id, message_id, yes_no_markup(voice_id))
        await AskUserAction.ask_action.set()
        return
    else:
        await report_function('clip', voice_id, command, chat_id)
        await call.message.delete_reply_markup()
        await send_message(chat_id, 'reported', parse=ParseMode.MARKDOWN)
        await ask_to_check_new_voice(chat_id, state)


async def ask_to_check_new_voice(chat_id, state):
    voices = await get_voices_to_check(tg_id=chat_id)
    if len(voices) == 0:
        await send_message(chat_id, 'no-voices-to-check', markup=start_markup)
        await state.finish()
        return
    voice = voices[0]
    text_to_check = voice['sentence']['text']
    voice_id = voice['id']
    voice_url = voice['audioSrc']
    voice_file = await download_file(voice_url, '{}_{}'.format(chat_id, voice_id))

    message_id = await send_voice(chat_id, open(voice_file, 'rb'), 'caption', args=text_to_check)

    await edit_reply_markup(chat_id, message_id, yes_no_markup(voice_id))
    await state.update_data(reply_message_id=message_id)
    await AskUserAction.ask_action.set()
    os.remove(voice_file)
