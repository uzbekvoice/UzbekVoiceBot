import uuid
import random
import string
import base64
import aiohttp
import librosa
import re
from speechbrain.pretrained import VAD
from rq import Retry
from . import db
from main import BASE_DIR, queue, bot
from keyboards.inline import my_profile_markup
from .common_voice import HEADERS, GET_TEXT_URL, GET_VOICES_URL, handle_operation


async def authorization_token(tg_id):
    user = db.get_user(tg_id)
    uuid = user.uuid
    access_token = user.access_token
    auth = f"{uuid}:{access_token}".encode('ascii')
    base64_bytes = base64.b64encode(auth)
    base64_string = base64_bytes.decode('ascii')
    return f'Basic {base64_string}'


def check_if_audio_human_voice(audio):
    savedir: str = str(BASE_DIR / "src" / "pretrained_models" / "vad-crdnn-libriparty")
    aaa = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir=savedir)
    boundaries = aaa.get_speech_segments(audio)

    return boundaries


def replace(text):
    return re.sub(
        r'(ch|sh)',
        'c',
        # replace spaces and punctuation
        re.sub(r'[^\w\s]', '',
               re.sub(r'([a-zA-Z])\1+', r'\1', text))
    )


def get_audio_duration(audio_path):
    return librosa.get_duration(filename=audio_path)


# gets audio duration in seconds
def check_if_audio_is_short(audio_path, text):
    characters_per_second = 18
    audio_duration = get_audio_duration(audio_path)
    text_duration = len(replace(text)) / characters_per_second
    return audio_duration < text_duration


async def register_user(state, tg_id):
    user_uid = uuid.uuid4()
    access_token = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(40)
    )

    await db.write_user(
        tg_id=tg_id,
        uuid=user_uid,
        access_token=access_token,
        full_name=state['full_name'],
        phone_number=state['phone_number'],
        gender=state['gender'],
        accent_region=state['accent_region'],
        year_of_birth=state['year_of_birth'],
        native_language=state['native_language']
    )


async def get_sentence_to_read(tg_id, state):
    data = await state.get_data()
    if "sentences" not in data or len(data["sentences"]) == 0:
        headers = {
            'Authorization': await authorization_token(tg_id),
            **HEADERS,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(GET_TEXT_URL, headers=headers, params={'count': '50'}) as get_request:
                response_json = await get_request.json()
                await state.update_data(sentences=response_json)
                return await get_sentence_to_read(tg_id, state)
    else:
        recorded_sentences = data["recorded_sentence_ids"] if "recorded_sentence_ids" in data else []
        sentences = data["sentences"]
        sentence = None
        for i in range(len(sentences)):
            sentence = sentences.pop()
            if sentence["id"] not in recorded_sentences:
                break
            else:
                sentence = None
        await state.update_data(sentences=sentences)
        if sentence is None:
            sentence = await get_sentence_to_read(tg_id, state)
        return sentence


sample_sentences = [
    "Bu voqea yuzaga chiqqaniga ishonolmasdim.",
    "Nilning Misr poytaxti Qohiradagi ko‘rinishi.",
    "Rekord yana yangilanishda davom etadi.",
    "Chunki aslida, fonogrammani jinim suymaydi.",
    "Shu mahallaning egasi-ku sizlar!",
    "Maqtashga arzigulik filmlar yo‘q deysizmi?",
    "Umrni uzaytirish xususiyatiga ega mahsulotlar.",
    "U yetarli darajada bo‘lishi kerak.",
    "Medal bilan nima bo‘lishi noaniq.",
    "O‘ylab ko‘rsam, undan ko‘nglim to‘lgan.",
    "San’atning bu yo‘nalishidagi ijrongizdan qoniqasizmi?",
    "Italiya sohilni qo‘riqlash xizmati kemasi.",
    "Ayting-chi, musobaqa qanday o‘tdi?",
    "Xitoydagi koronavirusga vaqtinchalik nom berildi.",
    "Ular ish bilan ta’minlanishi mumkin.",
    "Hozir biz Penrouz ishiga o‘tamiz.",
    "Biroq qonun talablariga rioya etildi”.",
    "U hozirda Iordaniyada bo‘lib turibdi.",
    "Lekin uni xonanda deb bilmayman.",
    "Umidaxondan eng sevimli taomlar shohsupasi.",
    "Ella Kennining turmush o‘rtog‘i Ukrainadan.",
    "Muddatimiz tugab, u yerdan kettik.",
    "Bu siyosat o‘zini to‘la oqladi.",
    "Uni ovqat yeyishga majbur qilmang.",
    "Bunaqasi tarixda birinchi marta bo‘lishi!",
    "Ichimlik tozalangan qahva kabi damlanadi.",
    "Aslida bu belgi yaxshi emas.",
    "Alessandra bilan ishlash maroqli kechmoqda.",
    "No frost texnologiyasi shunchalik zarurmi?",
    "Qurilma mart o‘rtalaridan sotuvga chiqadi.",
    "Bu borada muhokamalar olib borilgan.",
    "Jinoyatchilar yana uning gapiga kirgan.",
    "Bitkoinning kursiga nima ta’sir qiladi?",
    "Quyida ular bilan sizlarni tanishtiramiz.",
    "Shaharlar shiddat bilan o‘sib bormoqda.",
    "Bu gaplarni eshitib kulgingiz keladi.",
    "Lekin tajriba qilishdan qo‘rqmaslik lozim.",
    "Birinchisida qiz, ikkinchisida o‘g‘il degandi.",
    "Lumumba esa uy qamog‘ida qolaveradi.",
    "Ayb menda yoki Viktorda emas.",
    "Aksariyat onalar kasallikni yengil o‘tkazgan.",
    "Mahsulotlarga narxlar to‘la yozib qo‘yildi.",
    "U sanoqli kunlari qolayotganini tushunardi.",
    "O‘zbekiston delegatsiyasining tashrifi davom etmoqda.",
    "Allohning mo‘jizasi bilan shifo topdim.",
    "Qizaloq shifoxonada hayotdan ko‘z yumgan.",
    "Yangiliklar daryosidan chetda qolib ketmang!"
]


incorrect_clip_paths = [
    "src/incorrect_clips/1.mp3",
    "src/incorrect_clips/2.mp3",
    "src/incorrect_clips/3.mp3",
    "src/incorrect_clips/4.mp3",
    "src/incorrect_clips/5.mp3",
    "src/incorrect_clips/6.mp3",
    "src/incorrect_clips/7.mp3",
    "src/incorrect_clips/8.mp3",
    "src/incorrect_clips/9.mp3",
    "src/incorrect_clips/10.mp3",
    "src/incorrect_clips/11.mp3",
    "src/incorrect_clips/12.mp3",
    "src/incorrect_clips/13.mp3",
    "src/incorrect_clips/14.mp3"
]


def is_local_clip_id(clip_id):
    return int(clip_id) >= 9999999990


def is_local_clip(clip):
    return is_local_clip_id(clip["id"])


def get_local_clip(index):
    real_index = int(index) - 9999999990 if is_local_clip_id(index) else int(index)
    path = incorrect_clip_paths[real_index]
    sentence = random.choice(sample_sentences)
    return {
        "id": 9999999990 + real_index,
        "is_correct": False,
        "local_path": path,
        "sentence": {
            "text": sentence,
        },
    }


def get_random_incorrect_voice():
    return get_local_clip(random.randint(0, len(incorrect_clip_paths) - 1))


async def get_voice_to_check(tg_id, state):
    use_incorrect_clips = random.randint(1, 5) == 1
    if use_incorrect_clips:
        return get_random_incorrect_voice()

    data = await state.get_data()
    if "voices" not in data or len(data["voices"]) == 0:
        headers = {
            'Referer': 'https://common.uzbekvoice.ai/uz/listen',
            'Authorization': await authorization_token(tg_id),
            **HEADERS
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(GET_VOICES_URL, headers=headers, params={'count': '50'}) as get_request:
                response_json = await get_request.json()
                await state.update_data(voices=response_json)
                return await get_voice_to_check(tg_id, state)
    else:
        checked_voices = data["checked_voice_ids"] if "checked_voice_ids" in data else []
        voices = data["voices"]
        voice = None
        for i in range(len(voices)):
            voice = voices.pop()
            if voice["id"] not in checked_voices:
                break
            else:
                voice = None
        await state.update_data(voices=voices)
        if voice is None:
            voice = await get_voice_to_check(tg_id, state)
        return voice


async def download_file(download_url, voice_id):
    file_directory = str(BASE_DIR / 'downloads' / f"{voice_id}.ogg")
    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as get_voice:
            with open(file_directory, "wb") as file_stream:
                video_url_content = await get_voice.content.read()
                file_stream.write(video_url_content)

            return file_directory


async def enqueue_operation(operation, chat_id):
    # if queue is not open
    if queue is None:
        return handle_operation(operation, chat_id)
    else:
        queue.enqueue(
            'utils.uzbekvoice.common_voice.handle_operation',
            await authorization_token(chat_id),
            operation,
            retry=Retry(max=100, interval=30)
        )


async def send_my_profile(tg_id):
    user = db.get_user(tg_id)
    my_profile = [
        f"👤 Mening profilim:\n\n"
        f"ID: <code>{tg_id}</code>",
        f"Ism: <b>{user['full_name']}</b>",
        f"Telefon raqam: <b>{user['phone_number']}</b>",
        f"Yosh oralig'i: <b>{str(user['year_of_birth'])}</b>",
        f"Jinsi: <b>{user['gender']}</b>",
        f"Ona-tili: <b>{user['native_language']}</b>",
        f"Shevasi: <b>{user['accent_region']}</b>",
    ]
    await bot.send_message(tg_id, '\n'.join(my_profile), parse_mode="HTML", reply_markup=my_profile_markup())
