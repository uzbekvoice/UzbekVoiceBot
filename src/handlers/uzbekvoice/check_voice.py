import os
from time import sleep

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ParseMode

from main import dp, AskUserAction
from data.messages import CHECK_VOICE, CANCEL_MESSAGE
from keyboards.buttons import start_markup, reject_markup
from keyboards.inline import yes_no_markup, report_voice_markup, confirm_action_markup
from utils.helpers import send_message, send_voice, edit_reply_markup, delete_message_markup
from utils.uzbekvoice.helpers import get_voices_to_check, download_file, send_voice_vote, report_function, skip_voice


# Handler that answers to Check Voice message
@dp.message_handler(lambda message: message.text == CHECK_VOICE or message.text == '/check')
async def check_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id

    voices_info = await get_voices_to_check(tg_id=chat_id)

    if len(voices_info) == 0:
        await send_message(chat_id, 'no-voices-to-check', markup=start_markup)
        await state.finish()
        return
    await send_message(chat_id, 'ask-check-voice', markup=reject_markup)

    await state.update_data(list_number=0, voices_info=voices_info)

    await ask_to_check_voice(chat_id, state)


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
    await send_message(message.chat.id, 'ask-check-voice-again', markup=reject_markup, reply=reply_message_id)


# Handler that receives action on pressed accept, reject, skip and report inline button
@dp.callback_query_handler(state=AskUserAction.ask_action, text=['accept', 'reject', 'skip', 'report'])
async def ask_action_handler(call: CallbackQuery, state: FSMContext):
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

    elif call_data == 'skip':
        await skip_voice(voice_id, chat_id)
        await call.message.delete()
        await ask_to_check_voice(chat_id, state)

    elif call_data in ['accept', 'reject']:
        await state.update_data(call_data=call_data)
        await edit_reply_markup(chat_id, message_id, confirm_action_markup)
        await AskUserAction.confirm_action.set()

    # If there are no more voice to check, get new list of text
    if list_number == 4:
        voices_info = await get_voices_to_check(tg_id=chat_id)
        if len(voices_info) > 0:
            await state.update_data(list_number=0, voices_info=voices_info)
        else:
            await send_message(chat_id, 'no-voices-to-check', markup=start_markup)
            await state.finish()
            return
    else:
        await state.update_data(list_number=list_number + 1)


@dp.callback_query_handler(state=AskUserAction.confirm_action, text=['confirm', 'back'])
async def ask_action_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    await call.answer()

    data = await state.get_data()
    list_number = data['list_number']
    voices_info = data['voices_info']
    voice_id = voices_info[list_number]['id']
    if call_data == 'confirm':
        await call.message.delete_reply_markup()
        await send_voice_vote(voice_id, data['call_data'], chat_id)
        await ask_to_check_voice(chat_id, state)

    elif call_data == 'back':
        await edit_reply_markup(chat_id, message_id, yes_no_markup)
        await AskUserAction.ask_action.set()
        return


# Handler that receives action on pressed report inline button
@dp.callback_query_handler(state=AskUserAction.report_type, text=['report_1', 'report_2', 'report_3', 'back'])
async def ask_report_type_handler(call: CallbackQuery, state: FSMContext):
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
        await report_function('clip', voice_id, call_data, chat_id)
        await call.message.delete_reply_markup()
        await call.message.delete()
        await send_message(chat_id, 'reported', parse=ParseMode.MARKDOWN)

    # If there are no more voice to check, get new list of text
    if list_number == 4:
        voices_info = await get_voices_to_check(tg_id=chat_id)
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
    await edit_reply_markup(chat_id, message_id, yes_no_markup)
    await state.update_data(reply_message_id=message_id)

    os.remove(file_directory)
    await AskUserAction.ask_action.set()
