import aiohttp

from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from keyboards.buttons import go_back_markup, start_markup
from keyboards.inline import edit_accent_markup, edit_lang_markup, edit_profile_markup, edit_age_markup
from utils.helpers import IsRegistered, IsSubscribedChannel, delete_message_markup, send_message
from utils.uzbekvoice import db
from main import dp, bot, EditProfile
from aiogram.types import Message

from data.messages import GO_HOME_TEXT, MY_PROFILE, MY_RATING
from utils.uzbekvoice.common_voice import CLIPS_LEADERBOARD_URL, VOTES_LEADERBOARD_URL
from utils.uzbekvoice.helpers import authorization_token, send_my_profile


# Handler that answers to cancel callbacks
@dp.callback_query_handler(state=EditProfile.all_states, text=GO_HOME_TEXT)
async def cancel_message_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'reply_message_id' in data:
        reply_message_id = data['reply_message_id']
        await delete_message_markup(call.from_user.id, reply_message_id)
    await send_message(call.from_user.id, 'action-rejected', markup=start_markup)
    await state.finish()


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=MY_PROFILE)
async def my_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'reply_message_id' in data:
        reply_message_id = data['reply_message_id']
        await delete_message_markup(message.from_user.id, reply_message_id)
    await send_my_profile(message.from_user.id)


@dp.callback_query_handler(text="⚙️ Sozlamalar")
async def edit_profile(call: CallbackQuery):
    if db.user_exists(call.from_user.id):
        await EditProfile.choose_field_to_edit.set()
        await call.message.delete()
        await send_message(call.from_user.id, 'choose-field-to-edit', markup=edit_profile_markup())


@dp.callback_query_handler(text="⚙️ Sozlamalar", state='*')
async def edit_profile(call: CallbackQuery):
    if db.user_exists(call.from_user.id):
        await EditProfile.choose_field_to_edit.set()
        await call.message.delete()
        await send_message(call.from_user.id, 'choose-field-to-edit', markup=edit_profile_markup())


@dp.callback_query_handler(state=EditProfile.choose_field_to_edit, text=['edit-age', 'edit-lang', 'edit-accent'])
async def choose_field_handler(call: CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    await call.message.delete()
    if call_data == 'edit-age':
        state.update_data(message_to_delete=call.message)
        await EditProfile.edit_age.set()
        await send_message(call.from_user.id, 'ask-birth-year', markup=edit_age_markup())
    elif call_data == 'edit-lang':
        await EditProfile.edit_language.set()
        await send_message(call.from_user.id, 'ask-native-language', markup=edit_lang_markup())
    elif call_data == 'edit-accent':
        await EditProfile.edit_accent.set()
        await send_message(call.from_user.id, 'ask-accent', markup=edit_accent_markup())


@dp.callback_query_handler(state=EditProfile.edit_age, text=["< 19", "19-29", "30-39", "40-49", "50-59",
                            "60-69", "70-79", "80-89", "> 89"])
async def edit_age(call: CallbackQuery):
    await db.edit_profile(call.from_user.id, age=call.data)
    await call.message.delete()
    await send_my_profile(call.from_user.id)


@dp.callback_query_handler(state=EditProfile.edit_language, text=["O'zbek tili", "Qoraqalpoq tili", "Rus tili",
                                                                  "Tojik tili", "Qozoq tili"])
async def edit_lang(call: CallbackQuery):
    await db.edit_profile(call.from_user.id, lang=call.data)
    await call.message.delete()
    await send_my_profile(call.from_user.id)


@dp.callback_query_handler(state=EditProfile.edit_accent, text=["Andijon", "Buxoro", "Farg'ona", "Jizzax", "Sirdaryo", "Xorazm",
                                                                "Namangan", "Navoiy", "Qashqadaryo", "Qoraqalpog'iston", "Samarqand",
                                                                "Surxondaryo", "Toshkent viloyati", "Toshkent shahri"])
async def edit_accent(call: CallbackQuery):
    await db.edit_profile(call.from_user.id, accent=call.data)
    await call.message.delete()
    await send_my_profile(call.from_user.id)


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=MY_RATING)
async def vote_leaderboard(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(VOTES_LEADERBOARD_URL, headers=headers) as get_request:
            votes_leaderboard = await get_request.json()
            given_votes = 0
            votes_position = 0
            for i in votes_leaderboard:
                if i['you'] == True:
                    given_votes = i['total']
                    votes_position = i['position'] + 1

    async with aiohttp.ClientSession() as session:
        async with session.get(CLIPS_LEADERBOARD_URL, headers=headers) as get_request:
            clips_leaderboard = await get_request.json()
            recorded_clips = 0
            clips_position = 0
            for i in clips_leaderboard:
                if i['you'] == True:
                    recorded_clips = i['total']
                    clips_position = i['position'] + 1

    my_stats = [
        f"<b>🏆 Sizning yutuqlaringiz:</b>\n",
        f"🗣 Yozilgan ovozlar: {recorded_clips}",
        f"📊 Ovoz yozishdagi o'rningiz: {clips_position}\n",
        f"🎧 Tekshirilgan ovozlar: {given_votes}",
        f"📊 Ovoz tekshirishdagi o'rningiz: {votes_position}"
    ]

    await bot.send_message(message.chat.id, "\n".join(my_stats), parse_mode="HTML", reply_markup=go_back_markup)