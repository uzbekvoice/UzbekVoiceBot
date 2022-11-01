import json
import uuid
import random
import string
import base64
import aiohttp
import librosa
import re
from speechbrain.pretrained import VAD

from . import db
from main import BASE_DIR

GET_TEXT_URL = 'https://common.uzbekvoice.ai/api/v1/uz/sentences'
SEND_VOICE_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips'
VOICE_VOTE_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips/{}/votes'
SKIP_VOICE_URL = 'https://common.uzbekvoice.ai/api/v1/skipped_clips/{}'
SKIP_SENTENCE_URL = 'https://common.uzbekvoice.ai/api/v1/skipped_sentences/{}'
GET_VOICES_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips'
REPORT_URL = 'https://common.uzbekvoice.ai/api/v1/reports'
CLIPS_LEADERBOARD_URL = 'https://common.uzbekvoice.ai/api/v1/clips/leaderboard'
VOTES_LEADERBOARD_URL = 'https://common.uzbekvoice.ai/api/v1/clips/votes/leaderboard'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/95.0.4638.69 Safari/537.36',
}


async def authorization_base64(tg_id, additional_headers):
    user = db.get_user(tg_id)
    uuid = user.uuid
    access_token = user.access_token
    auth = f"{uuid}:{access_token}".encode('ascii')
    base64_bytes = base64.b64encode(auth)
    base64_string = base64_bytes.decode('ascii')
    authorization = f'Basic {base64_string}'
    return {
        'Authorization': authorization,
        **HEADERS,
        **additional_headers
    }


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
    characters_per_second = 36 / 2.35
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


async def get_text_to_read(tg_id):
    headers = await authorization_base64(tg_id, {})
    data = {'count': '1'}

    async with aiohttp.ClientSession() as session:
        async with session.get(GET_TEXT_URL, headers=headers, params=data) as get_request:
            response_json = await get_request.json()

            return response_json


async def get_voices_to_check(tg_id):
    headers = await authorization_base64(tg_id, {'Referer': 'https://common.uzbekvoice.ai/uz/listen'})
    data = {'count': '1'}

    async with aiohttp.ClientSession() as session:
        async with session.get(GET_VOICES_URL, headers=headers, params=data) as get_request:
            response_json = await get_request.json()

            return response_json


async def send_text_voice(file_directory, text_id, tg_id):
    headers = await authorization_base64(tg_id, {'sentence_id': text_id, 'Content-Type': 'audio/ogg'})
    data = open(file_directory, 'rb')

    async with aiohttp.ClientSession() as session:
        async with session.post(SEND_VOICE_URL, headers=headers, data=data) as sent_voice:
            await sent_voice.json()


async def send_voice_vote(voice_id, is_valid, tg_id):
    headers = await authorization_base64(tg_id, {'Content-Type': 'application/json'})

    data = {'challenge': 'null', "isValid": is_valid}
    request_url = VOICE_VOTE_URL.format(voice_id)
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, data=json.dumps(data), headers=headers) as posted_vote:
            posted_vote_response = await posted_vote.json()


async def skip_voice(voice_id, tg_id):
    headers = await authorization_base64(tg_id, {})

    request_url = SKIP_VOICE_URL.format(int(voice_id))
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, headers=headers) as skipped_voice:
            skipped_voice_response = await skipped_voice.json()


async def skip_sentence(sentence_id, tg_id):
    headers = await authorization_base64(tg_id, {})

    request_url = SKIP_SENTENCE_URL.format(sentence_id)
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, headers=headers) as skipped_sentence:
            skipped_sentence_response = await skipped_sentence.json()


async def report_function(kind, id_to_report, report_type, tg_id):
    headers = await authorization_base64(tg_id, {'Content-Type': 'application/json'})

    if report_type == 'report_1':
        reason = 'offensive-language'
    elif report_type == 'report_2':
        reason = 'grammar-or-spelling'
    elif report_type == 'report_3':
        reason = 'different-language'
    else:
        reason = 'difficult-pronounce'

    data = {"kind": kind, "id": id_to_report, "reasons": [reason]}
    print(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(REPORT_URL, data=json.dumps(data), headers=headers) as post_report:
            posted_report_response = await post_report.json()


async def download_file(download_url, voice_id):
    file_directory = str(BASE_DIR / 'downloads' / f"{voice_id}.ogg")
    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as get_voice:
            with open(file_directory, "wb") as file_stream:
                video_url_content = await get_voice.content.read()
                file_stream.write(video_url_content)

            return file_directory
