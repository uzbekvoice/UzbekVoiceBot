import os

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from main import dp, AskUserVoice
from data.messages import RECORD_VOICE
from keyboards.buttons import start_markup, reject_markup
from utils.helpers import send_message
from utils.uzbekvoice.helpers import get_text_to_read, send_text_voice


# Handler that answers to Record Voice message
@dp.message_handler(text=RECORD_VOICE)
async def record_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id

    await send_message(chat_id, 'ask-record-voice', markup=reject_markup)

    text_info = await get_text_to_read()
    await state.update_data(list_number=0, text_info=text_info)

    await ask_to_send_voice(chat_id, state)


# Handler that receives all messages
@dp.message_handler(state=AskUserVoice.ask_voice, content_types=['text'])
async def message_receiver_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_message = message.text

    if user_message == 'Отменить':
        await send_message(message.chat.id, 'action-rejected', markup=start_markup)
        await state.finish()
    else:
        data = await state.get_data()
        reply_message_id = data['reply_message_id']
        await send_message(chat_id, 'ask-record-voice-again', markup=reject_markup, reply=reply_message_id)


# Handler that receives all voice messages
@dp.message_handler(state=AskUserVoice.ask_voice, content_types=['voice'])
async def voice_receiver_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id

    data = await state.get_data()
    list_number = data['list_number']
    text_info = data['text_info']
    text_id = text_info[list_number]['id']

    file_directory = 'downloads/{}.ogg'.format(text_id)
    await message.voice.download(file_directory)
    await send_text_voice(file_directory, text_id)
    os.remove(file_directory)

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
    message_id = await send_message(chat_id, 'caption', args=text_to_read, markup=reject_markup)
    await state.update_data(reply_message_id=message_id)

    await AskUserVoice.ask_voice.set()
