import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from main import dp, AskUserVoice
from data.messages import RECORD_VOICE, CANCEL_MESSAGE
from keyboards.buttons import start_markup, reject_markup
from keyboards.inline import skip_report_markup, report_text_markup, confirm_voice_markup
from utils.helpers import send_message, edit_reply_markup, send_voice
from utils.uzbekvoice.helpers import get_text_to_read, send_text_voice, report_function, check_if_audio_human_voice


# Handler that answers to Record Voice message
@dp.message_handler(text=RECORD_VOICE)
async def record_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id

    await send_message(chat_id, 'ask-record-voice', markup=reject_markup)

    text_info = await get_text_to_read()
    await state.update_data(list_number=0, text_info=text_info)

    await ask_to_send_voice(chat_id, state)


# Handler that answer to cancel message
@dp.message_handler(state=AskUserVoice.all_states, text=CANCEL_MESSAGE)
async def cancel_message_handler(message: Message, state: FSMContext):
    await send_message(message.chat.id, 'action-rejected', markup=start_markup)
    await state.finish()


# Handler that receives all unnecessary messages in ask voice state
@dp.message_handler(state=AskUserVoice.ask_voice, content_types=['text'])
async def ask_voice_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await send_message(message.chat.id, 'ask-record-voice-again', markup=reject_markup, reply=reply_message_id)


# Handler that receives user sent voices
@dp.message_handler(state=AskUserVoice.ask_voice, content_types=['voice'])
async def ask_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    audio_id = message.voice.file_id

    data = await state.get_data()
    list_number = data['list_number']
    text_info = data['text_info']
    text_id = text_info[list_number]['id']
    text_to_read = text_info[list_number]['text']
    # here goes checking audio
    file_directory = 'downloads/{}.ogg'.format(text_id)
    await message.voice.download(file_directory)
    print(check_if_audio_human_voice(file_directory))
    sent_audio_id = await send_voice(chat_id, audio_id, 'ask-recheck-voice', args=text_to_read,
                                     markup=confirm_voice_markup)

    await state.update_data(reply_message_id=sent_audio_id)
    await AskUserVoice.ask_confirm.set()


# Handler that receives all unnecessary messages in ask confirmation state
@dp.message_handler(state=AskUserVoice.ask_confirm, content_types=['text'])
async def ask_confirm_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await send_message(message.chat.id, 'ask-recheck-voice', args='', markup=reject_markup, reply=reply_message_id)


# Handler that receives pressed button, where the users confirm whether voice is correct or not
@dp.callback_query_handler(state=AskUserVoice.ask_confirm, text=['confirm-voice', 'reject-voice'])
async def ask_confirm_handler(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    call_data = call.data

    await call.answer()
    await call.message.delete()

    data = await state.get_data()
    list_number = data['list_number']
    text_info = data['text_info']
    text_id = text_info[list_number]['id']

    if call_data == 'confirm-voice':
        file_directory = 'downloads/{}.ogg'.format(text_id)
        await call.message.voice.download(file_directory)
        await send_text_voice(file_directory, text_id)
        os.remove(file_directory)

        # If there are no more text to read, get new list of text
        if list_number == 4:
            text_info = await get_text_to_read()
            await state.update_data(list_number=0, text_info=text_info)
        else:
            await state.update_data(list_number=list_number + 1)

    await ask_to_send_voice(chat_id, state)


# Handler that receives action on pressed report inline button
@dp.callback_query_handler(state=AskUserVoice.ask_voice, text=['report_1', 'report_2', 'report_3', 'report_4', 'back', 'report', 'skip'])
async def ask_report_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call_data == 'back':
        await edit_reply_markup(chat_id, message_id, skip_report_markup)
        await AskUserVoice.ask_voice.set()
        return
    elif call_data == 'report':
        await edit_reply_markup(chat_id, message_id, report_text_markup)
        return
    else:
        data = await state.get_data()
        list_number = data['list_number']
        text_info = data['text_info']
        text_id = text_info[list_number]['id']

        if 'report' in call_data:
            await report_function('sentence', text_id, call_data)
        await call.message.delete()

    # If there are no more text to read, get new list of text
    if list_number == 4:
        text_info = await get_text_to_read()
        await state.update_data(list_number=0, text_info=text_info)
    else:
        await state.update_data(list_number=list_number + 1)

    await ask_to_send_voice(chat_id, state)


# Function to send text to user in order to read
async def ask_to_send_voice(chat_id, state):
    data = await state.get_data()
    list_number = data['list_number']
    text_info = data['text_info']

    text_to_read = text_info[list_number]['text']
    message_id = await send_message(chat_id, 'caption', args=text_to_read, markup=skip_report_markup)
    await state.update_data(reply_message_id=message_id)

    await AskUserVoice.ask_voice.set()
