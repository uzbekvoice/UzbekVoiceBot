import os
from datetime import datetime, timedelta
import aiogram.types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import Message, CallbackQuery
from utils.uzbekvoice import db
from main import dp, AskUserVoice, BASE_DIR
from data.messages import RECORD_VOICE, CANCEL_MESSAGE
from keyboards.buttons import start_markup, go_back_markup
from keyboards.inline import text_markup, report_text_markup, confirm_voice_markup
from utils.helpers import send_message, edit_reply_markup, send_voice, delete_message_markup, delete_message, \
    IsRegistered, \
    IsBlockedUser
from utils.uzbekvoice.helpers import get_text_to_read, send_text_voice, report_function, check_if_audio_human_voice, \
    skip_sentence


# Handler that answers to Record Voice message
@dp.message_handler(IsRegistered(), IsBlockedUser(), text=RECORD_VOICE)
@dp.message_handler(IsRegistered(), IsBlockedUser(), commands=['record'])
async def record_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await send_message(chat_id, 'ask-record-voice', markup=go_back_markup)
    await ask_to_send_new_voice(chat_id, state)


# Handler that answer to cancel message
@dp.message_handler(state=AskUserVoice.all_states, text=CANCEL_MESSAGE)
async def cancel_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await delete_message_markup(message.chat.id, reply_message_id)
    await send_message(message.chat.id, 'action-rejected', markup=start_markup)
    await state.finish()


# Handler that receives all unnecessary messages in ask voice state
@dp.message_handler(state=AskUserVoice.ask_voice, content_types=['text'])
async def ask_voice_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await send_message(message.chat.id, 'ask-record-voice-again', markup=go_back_markup, reply=reply_message_id)


# Handler that receives user sent voices
@dp.message_handler(IsRegistered(), IsBlockedUser(), state=AskUserVoice.ask_voice, content_types=['voice'])
async def ask_voice_handler(message: Message, state: FSMContext):
    chat_id = message.chat.id
    audio_id = message.voice.file_id
    data = await state.get_data()
    text = data['text']
    text_id = text['id']
    text_to_read = text['text']
    audio_file = str(BASE_DIR / 'downloads' / '{}_{}.ogg'.format(chat_id, text_id))
    await message.voice.download(destination_file=audio_file)
    sent_audio_id = await send_voice(chat_id, audio_id, 'ask-recheck-voice',
                                     args=f'—————<br><b>{text_to_read}</b><br>—————',
                                     markup=confirm_voice_markup(),
                                     parse=aiogram.types.ParseMode.HTML)
    await state.update_data(reply_message_id=sent_audio_id)
    await AskUserVoice.ask_confirm.set()


# Handler that receives all unnecessary messages in ask confirmation state
@dp.message_handler(state=AskUserVoice.ask_confirm, content_types=['text'])
async def ask_confirm_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    await send_message(message.chat.id, 'ask-recheck-voice', args='', markup=go_back_markup, reply=reply_message_id)


# Handler that receives pressed button, where the users confirm whether voice is correct or not
@dp.callback_query_handler(state=AskUserVoice.ask_confirm, regexp=r'^(confirm-voice|reject-voice).*$')
async def ask_confirm_handler(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    call_data = str(call.data)
    command = call_data
    data = await state.get_data()
    reply_message_id = data['reply_message_id']
    message_id = call.message.message_id
    text = data['text']
    text_id = text['id']
    await call.answer()
    if str(reply_message_id) != str(message_id):
        return await call.answer('Xatolik yuz berdi, iltimos qaytadan yuboring!!!', show_alert=True)

    audio_file = str(BASE_DIR / 'downloads' / '{}_{}.ogg'.format(chat_id, text_id))

    if command == 'confirm-voice':
        voice_checking_message_id = await send_message(chat_id, 'voice-checking')
        user = db.get_user(chat_id)
        validation_required = user["last_validated_at"] is None or user["last_validated_at"] < (
                datetime.now() - timedelta(minutes=20))
        is_valid = len(check_if_audio_human_voice(audio_file)) != 0 if validation_required else True
        if not is_valid:
            await delete_message(chat_id, voice_checking_message_id)
            await delete_message_markup(chat_id, reply_message_id)
            await send_message(chat_id, 'wrong-audio-text', reply=reply_message_id, parse='html')
            await AskUserVoice.ask_voice.set()
            os.remove(audio_file)
            return
        # if user passed validation, save current time
        if validation_required:
            db.user_validated_now(chat_id)
        await call.message.delete_reply_markup()
        await send_text_voice(audio_file, text_id, chat_id)
        await ask_to_send_new_voice(chat_id, state)
        os.remove(audio_file)
    else:
        await call.message.delete()
        await ask_to_send_voice(chat_id, text, state)
        os.remove(audio_file)


# Handler that receives action on pressed report inline button
@dp.callback_query_handler(state=AskUserVoice.ask_voice, regexp=r'^(report_\d+|back|report|skip).*$')
async def ask_report_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = await state.get_data()
    text = data['text']
    reply_message_id = data['reply_message_id']
    command = call_data
    text_id = text["id"]
    if str(reply_message_id) != str(message_id):
        return await call.answer('Xatolik yuz berdi, iltimos qaytadan yuboring!!!', show_alert=True)
    if command == 'back':
        await edit_reply_markup(chat_id, message_id, text_markup())
        await AskUserVoice.ask_voice.set()
        return
    elif command == 'report':
        await edit_reply_markup(chat_id, message_id, report_text_markup())
        return
    elif command == 'skip':
        await call.message.delete()
        await skip_sentence(text_id, chat_id)
    else:
        await call.message.delete()
        if 'report' in command:
            await report_function('sentence', text_id, command, tg_id=chat_id)
            await skip_sentence(text_id, chat_id)

    await ask_to_send_new_voice(chat_id, state)


# Function to send text to user in order to read
async def ask_to_send_voice(chat_id, text, state):
    text_to_read = f'—————\n<b>{text["text"]}</b>\n—————'
    message_id = await send_message(
        chat_id,
        'caption',
        args=text_to_read,
        markup=text_markup(),
        parse=aiogram.types.ParseMode.HTML
    )
    await state.update_data(reply_message_id=message_id)
    await state.update_data(text=text)

    await AskUserVoice.ask_voice.set()


async def ask_to_send_new_voice(chat_id, state):
    texts = await get_text_to_read(chat_id)
    text = texts[0]
    await ask_to_send_voice(chat_id, text, state)
