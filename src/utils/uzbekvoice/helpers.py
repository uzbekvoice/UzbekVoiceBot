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
    "Va qahvaxona egasi jarimaga solindi.",
    "Bu yerda tushunmovchilik bo‘lgan.",
    "O‘zbekiston boks federatsiyasi aniqlik kiritdi.",
    "O‘qituvchilarni norozi qilmanglar.",
    "Federal xavfsizlik xizmatiga havolalar bo‘lgan.",
    "Tajovuzkor qo‘lga olingan.",
    "Hattoki sirtqida o‘qiydigan talabalarga ham.",
    "Shveysariyada jaziramadan so‘ng qor yog‘di.",
    "Qo‘l uchun antiseptik vosita ham defitsit.",
    "Biz O‘zbekistonga qaytdik.",
    "Yoshlikni saqlab qolishni xohlaysizmi?",
    "Yunusoboddagi uyning tomi yondi .",
    "Umumiy texnik talablar.",
    "Bu bizning asosiy maqsadimiz.",
    "Yaqin Sharqqa kelganimdan xursandman.",
    "Yo‘l bo‘lmasa, yo‘lsiz yashaydi.",
    "Samsung Yangi yil sovg‘alarini ulashmoqda!.",
    "Buni foydali deb o‘ylamayman.",
    "Shulardan biri o‘z nihoyasiga yetdi.",
    "Yoki pochtachi sumkasi.",
    "I darajali Davlat adliya maslahatchisi.",
    "Bu qoyilmaqom jang bo‘ldi.",
    "Hosilning bozori chaqqon.",
    "Boshqa boradigan joyim qolmadi.",
    "Shunchaki izohlashni istamayman”, dedi Tramp.",
    "Bu tatuirovka, nakleyka emas.",
    "Erkak yengil jarohat olgani aytilmoqda.",
    "Bu meni ilhomlantiradi deb o‘ylardim.",
    "Ammo kirish yo‘lagida isiriq tutatildi.",
    "Haydovchi qo‘lga olindi.",
    "Ularda mutlaqo boshqa tushunchalar hukmron.",
    "Britaniya hukumat aloqalari markazi.",
    "Ammo xavfsizlik haqida ham unutmang!",
    "Ko‘ramiz”, deydi Messi.",
    "Iroqda Isroil bayrog‘i taqiqlandi.",
    "Qolgan murojaatlar nazoratga olinib, ijroga qaratildi.",
    "Ayblanuvchilarning yaqinlari esa bundan norozi.",
    "Iste’molchilarga tanlov imkoniyati berilishi kerak.",
    "Nutqni rejissor so‘zladi.",
    "Essiz, yoshligim husnbuzarlar bilan o‘tmoqda.",
    "Foydasidan zarari ko‘p bo‘lgan sabzavotlar.",
    "Aftidan muddat qisqaradi shekilli.",
    "Bunga o‘zgartishlar kiritilishi kerak.",
    "Sababi, o‘qish sentabrdan boshlanardi.",
    "Avstraliyalik dayver akula qurboni bo‘ldi.",
    "Buyuk Britaniyada noma’lum dengiz mavjudoti aniqlandi.",
    "Tekshirish natijalari ma'lum qilinmagan.",
    "Asosiysi telefonni uyda unutib qoldirmang.",
    "Ishtirokchilar taklifni ma’qulladi.",
    "Go‘dak kuyib qolib, vafot etdi.",
    "Kanada bosh vaziri Jastin Tryudo.",
    "Aynan nima sizning harakatingizni sekinlashtiradi?",
    "Ba’zan tush surtsa ham, qayrilmaydi.",
    "Bunga nimaning hisobidan erishamiz?",
    "Bizni ulardan qayerimiz kam?",
    "Qanday hayot kechirish esa sizning tanlovingiz.",
    "Toshkentda yakkakurash bo‘yicha musobaqa o‘tkazildi.",
    "Atrofda yantoq juda ko‘p.",
    "Yarfo Muhammadni chaqirib keldi.",
    "Ansandagi xotira mehrobi.",
    "Gumonlanuvchi keyinroq qo‘lga olindi.",
    "Biz to‘xtamasligimiz lozim.",
    "Yigitlar vaziyatni tushunib turibdi.",
    "Hozircha chaqaloqning yaqinlari topilmadi.",
    "Bu bemorlarga tasalli beradi.",
    "Soxta mahsulotlardan ehtiyot bo‘ling !!!",
    "Keyingi yoz ular uchrashib, tanishmoqchi.",
    "Javob bo‘lmagach, xonaga kirdim.",
    "Mevali va manzarali daraxtlar ekildi.",
    "Ijtimoiy tarmoqlardagi trendlar.",
    "Reytingda yana Vladimir Putin yetakchilik qildi.",
    "Buxoruddin Yusuf Habibiy.",
    "Kassir uning talabini bajardi.",
    "Hamma tarmoqlar tahlil qilinmoqda.",
    "Ayol otasini baribir olib ketgan.",
    "Ammo qizig‘i keyin boshlandi.",
    "Investitsiya bo‘lmasa, iqtisodiyot rivojlanmaydi.",
    "Bolalar hayajondan yig‘lab yubordi.",
    "Ikki xalq mutlaqo o‘xshamaydi.",
    "Saytda qo‘shiqning audiosi e’lon qilingan.",
    "Afsuski, oliy ma’lumotim yo‘q.",
    "U yerda to‘rt kishi yaralandi.",
    "Leo qoyilmaqom o‘yin ko‘rsatmoqda.",
    "Chunki endi hujjatini yangilashi kerak.",
    "Quyida ushbu maqola to‘lig‘icha berildi.",
    "Holat yuzasidan jinoyat ishi qo‘zg‘atildi.",
    "Hammaning xayolida shu muammo.",
    "Abror Tursunpo‘latov, boks murabbiyi",
    "Kichkintoylar uchun o‘yin maydoni.",
    "Shahar juda o‘zgarib ketibdi.",
    "Oilasini boqishi kerak.",
    "Natijada samolyot Bayrutga qo‘ngan.",
    "Orada bir mizg‘ib oldim.",
    "O‘sha yili sen tug‘ilgan eding.",
    "Odamning vahmi keladi.",
    "Iqtisodiyot va moliya vazirlari o‘zgardi.",
    "Ayol yaralangan va kasalxonaga yotqizilgan.",
    "Uchrashuvda Oston to‘liq harakat qildi.",
    "Endigi navbatda Buxoro turgani aytilmoqda.",
    "Bir yildan so‘ng, balki qishgachadir.",
    "Odatda, unchalik ham xavfli emas.",
    "Ish haqingizdan ko‘nglingiz to‘lmayaptimi?",
    "UzReport Parijga e’tibor qaratadi.",
    "O‘zbekistonda esdalik tangalar narxi tushdi.",
    "Mahalliy aholi uylaridan ko‘chirilmoqda.",
    "Bu protseduralarning barchasi bajarilganmi?",
    "Hozirgi kunda sud tergovi ketayapti.",
    "ham qo‘lga olingan”, deyiladi xabarda.",
    "Bu poytaxt uchun antirekord hisoblanadi.",
    "O‘ylashga qo‘rqadi odam.",
    "Boshqa tafsilotlar hozircha keltirilmayapti.",
    "Tadbirkorlar bozor buzilishidan norozi .",
    "Ayrim o‘ziga xosliklar bilan.",
    "Ammo siz ham bizni eshiting.",
    "O‘zbekistonda urfga kirmagan moda trendlari.",
    "Lekin biz ishlashda davom etdik.",
    "Bunda qanday ish tutiladi?",
    "Sharoitlar shaharnikidan aslo qolishmaydi.",
    "Kitob tumanida yashagan.",
    "Shu bois muvaffaqiyatsizlik kuzatilgan.",
    "Uzr so‘rayman”, dedi futbolchi.",
    "Mamlakatda milliy motam e’lon qilindi .",
    "Ekspertlarning tadqiqotlari davom etmoqda.",
    "Uydagi o‘zaro tortishuv janjalga aylanadi.",
    "Bu xuddi mehmonxonada yashashga o‘xshadi”.",
    "Gap faqat mashg‘ulotlarda emas.",
    "Shunga qo‘rqib yuribman.",
    "O‘zbekistonning Ukrainadagi elchixonasi binosi.",
    "U tortning ko‘rinishini yanada boyitadi.",
    "Ta’lim dasturlari nochor va sayoz.",
    "Windows’da xavfli zaiflik aniqlandi.",
    "Avstraliya aborigenlari bayrog‘i.",
    "Faqat shundagina futbolni rivojlantirish mumkin.",
    "Ulardan birini keltirmoqdamiz.",
    "Saharlikka mazali sho‘rva retsepti.",
    "Hozirda hayvonot bog‘i yopilgan.",
    "O‘zbekistonda dollar kursi yana ko‘tarildi.",
    "Chempionlar Ligasi yakunlari haqida.",
    "Seni foydang zararing tegmagani, deydilar.",
    "Reytingda Germaniya termasi peshqadam.",
    "Ashbaxer bu ayblovlarni rad etgan.",
    "Instagram’dagi mashhur tuxum yorila boshladi.",
    "Kulishni ham, yig‘lashni ham bilmaysan.",
    "Hayronman, aytishga so‘z yo‘q.",
    "Xo‘sh, ular qanchalik haq edi?",
    "Sizning duogo‘ylaringiz ko‘p.",
    "Ularga esda qolarli hissiyotlar yetishmaydi!",
    "Bu revansh jangiga qattiq tayyorlandim.",
    "Yarim kechasi nima qilib yuribsiz?",
    "Tongda turiboq, mo‘ljallangan ishlarga kirishing.",

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
    "src/incorrect_clips/14.mp3",
    "src/incorrect_clips/15.mp3",
    "src/incorrect_clips/16.mp3",
    "src/incorrect_clips/17.mp3",
    "src/incorrect_clips/18.mp3"
]


def is_local_clip_id(clip_id):
    return int(clip_id) >= 9999999000


def is_local_clip(clip):
    return is_local_clip_id(clip["id"])


def get_local_clip(index):
    real_index = int(index) - 9999999000 if is_local_clip_id(index) else int(index)
    path = incorrect_clip_paths[real_index]
    sentence = random.choice(sample_sentences)
    return {
        "id": 9999999000 + real_index,
        "is_correct": False,
        "local_path": path,
        "sentence": {
            "text": sentence,
        },
    }


def get_random_incorrect_voice():
    return get_local_clip(random.randint(0, len(incorrect_clip_paths) - 1))


async def get_voice_to_check(tg_id, state, user):
    probability = user["verification_probability"]
    use_incorrect_clips = random.random() < probability
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
                return await get_voice_to_check(tg_id, state, user)
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
            voice = await get_voice_to_check(tg_id, state, user)
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
        print('Queue is not open')
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
