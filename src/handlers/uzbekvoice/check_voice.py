import asyncio
import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from data.messages import CHECK_VOICE, CANCEL_MESSAGE
from keyboards.buttons import start_markup, reject_markup
from keyboards.inline import yes_no_markup, report_voice_markup
from main import dp, AskUserAction
from utils.helpers import send_message, send_voice, edit_reply_markup
from utils.uzbekvoice.helpers import get_voices_to_check, download_file, send_voice_vote, report_function


# Handler that answers to Check Voice message
@dp.message_handler(text=CHECK_VOICE)
async def check_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id

    await send_message(chat_id, 'ask-check-voice', markup=reject_markup)

    voices_info = await get_voices_to_check()
    await state.update_data(list_number=0, voices_info=voices_info)

    await ask_to_check_voice(chat_id, state)


# Handler that receives all messages
@dp.message_handler(state=AskUserAction.ask_action, content_types=['text'])
async def message_receiver_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_message = message.text

    if user_message == CANCEL_MESSAGE:
        await send_message(message.chat.id, 'action-rejected', markup=start_markup)
        await state.finish()
    else:
        data = await state.get_data()
        reply_message_id = data['reply_message_id']
        await send_message(chat_id, 'ask-check-voice-again', markup=reject_markup, reply=reply_message_id)


# Handler that receives action on pressed accept and reject inline button
@dp.callback_query_handler(state=AskUserAction.ask_action)
async def ask_user_action(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    await call.answer()

    data = await state.get_data()
    list_number = data['list_number']
    voices_info = data['voices_info']
    voice_id = voices_info[list_number]['id']

    if call_data == 'report':
        await edit_reply_markup(chat_id, message_id, report_voice_markup)
        await AskUserAction.report_type.set()
        return
    elif call_data == 'skip':
        await call.message.delete()
    else:
        await call.message.delete_reply_markup()
        await send_voice_vote(voice_id, call_data)

    # If there are no more voice to check, get new list of text
    if list_number == 4:
        voices_info = await get_voices_to_check()
        await state.update_data(list_number=0, voices_info=voices_info)
    else:
        await state.update_data(list_number=list_number + 1)

    await ask_to_check_voice(chat_id, state)


# Handler that receives action on pressed report inline button
@dp.callback_query_handler(state=AskUserAction.report_type)
async def ask_user_report(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call_data == 'back':
        await edit_reply_markup(chat_id, message_id, yes_no_markup)
        await AskUserAction.ask_action.set()
        return
    else:
        data = await state.get_data()
        list_number = data['list_number']
        voices_info = data['voices_info']
        voice_id = voices_info[list_number]['id']

        await report_function('clip', voice_id, call_data)
        await call.message.delete()

    # If there are no more voice to check, get new list of text
    if list_number == 4:
        voices_info = await get_voices_to_check()
        await state.update_data(list_number=0, voices_info=voices_info)
    else:
        await state.update_data(list_number=list_number + 1)

    await ask_to_check_voice(chat_id, state)


# Function to send voice message with text to user to
# check if the audio was recorded correctly
async def ask_to_check_voice(chat_id, state):
    data = await state.get_data()
    voices_info = data['voices_info']
    list_number = data['list_number']

    text_to_check = voices_info[list_number]['sentence']['text']
    voice_id = voices_info[list_number]['id']
    voice_url = voices_info[list_number]['audioSrc']

    file_directory = await download_file(voice_url, voice_id)

    message_id = await send_voice(chat_id, open(file_directory, 'rb'), 'caption', args=text_to_check)
    await asyncio.sleep(4)
    await edit_reply_markup(chat_id, message_id, yes_no_markup)
    await state.update_data(reply_message_id=message_id)

    os.remove(file_directory)
    await AskUserAction.ask_action.set()
