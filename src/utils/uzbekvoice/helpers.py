import asyncio

import aiohttp
from speechbrain.pretrained import VAD




GET_TEXT_URL = 'https://commonvoice.mozilla.org/api/v1/uz/sentences'
SEND_VOICE_URL = 'https://commonvoice.mozilla.org/api/v1/uz/clips'
VOICE_VOTE_URL = 'https://commonvoice.mozilla.org/api/v1/uz/clips/{}/votes'
GET_VOICES_URL = 'https://commonvoice.mozilla.org/api/v1/uz/clips'
REPORT_URL = 'https://commonvoice.mozilla.org/api/v1/reports'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/95.0.4638.69 Safari/537.36',
           'Authorization': 'Basic YzI2ZTZhOTAtMWMwOS00ZjFlLTk5ZmYtMTRmZWQ2'
                            'MGNlMTlhOmNhN2ViMjQ2NjQ0OWYxZWJmZjJmMjgzYjNhMTczOGMyOTJmYWQ0Mzg='}


def check_if_audio_human_voice(audio):
    
    AAA = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir="src/pretrained_models/vad-crdnn-libriparty")
    boundaries = AAA.get_speech_segments(audio)

    return boundaries


async def get_text_to_read():
    data = {'count': '5'}

    async with aiohttp.ClientSession() as session:
        async with session.get(GET_TEXT_URL, params=data) as get_request:
            response_json = await get_request.json()

            return response_json


async def get_voices_to_check():
    HEADERS['Referer'] = 'https://commonvoice.mozilla.org/uz/listen'
    data = {'count': '5'}

    async with aiohttp.ClientSession() as session:
        async with session.get(GET_VOICES_URL, headers=HEADERS, params=data) as get_request:
            response_json = await get_request.json()

            return response_json


async def send_text_voice(file_directory, text_id):
    HEADERS['sentence_id'] = text_id
    HEADERS['Content-Type'] = 'audio/ogg'
    data = open(file_directory, 'rb')

    async with aiohttp.ClientSession() as session:
        async with session.post(SEND_VOICE_URL, data=data, headers=HEADERS) as sent_voice:
            sent_voice_response = await sent_voice.json()


async def send_voice_vote(voice_id, vote):
    data = {'challenge': 'null'}
    if vote == 'accept':
        data['isValid'] = 'true'
    else:
        data['isValid'] = 'false'

    request_url = VOICE_VOTE_URL.format(voice_id)
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, params=data, headers=HEADERS) as posted_vote:
            posted_vote_response = await posted_vote.json()


async def report_function(kind, id_to_report, report_type):
    if report_type == 'report_1':
        reason = 'offensive-language'
    elif report_type == 'report_2':
        reason = 'grammar-or-spelling'
    elif report_type == 'report_3':
        reason = 'different-language'
    else:
        reason = 'difficult-pronounce'

    data = {"kind": kind, "id": id_to_report, "reasons": [reason]}
    async with aiohttp.ClientSession() as session:
        async with session.post(REPORT_URL, data=data) as post_report:
            posted_report_response = await post_report.json()
            # print(posted_report_response)


async def download_file(download_url, voice_id):
    file_directory = f'downloads/{voice_id}.ogg'
    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as get_voice:
            with open(file_directory, "wb") as file_stream:
                video_url_content = await get_voice.content.read()
                file_stream.write(video_url_content)

            return file_directory


if __name__ == '__main__':
    asyncio.run(get_voices_to_check())
