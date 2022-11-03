import os
import json
import aiohttp

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/95.0.4638.69 Safari/537.36',
}

GET_TEXT_URL = 'https://common.uzbekvoice.ai/api/v1/uz/sentences'
SEND_VOICE_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips'
VOICE_VOTE_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips/{}/votes'
SKIP_VOICE_URL = 'https://common.uzbekvoice.ai/api/v1/skipped_clips/{}'
SKIP_SENTENCE_URL = 'https://common.uzbekvoice.ai/api/v1/skipped_sentences/{}'
GET_VOICES_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips'
REPORT_URL = 'https://common.uzbekvoice.ai/api/v1/reports'
CLIPS_LEADERBOARD_URL = 'https://common.uzbekvoice.ai/api/v1/clips/leaderboard'
VOTES_LEADERBOARD_URL = 'https://common.uzbekvoice.ai/api/v1/clips/votes/leaderboard'


async def send_text_voice(token, file_directory, text_id):
    headers = {
        'sentence_id': text_id,
        'Content-Type': 'audio/ogg',
        'Authorization': token,
        **HEADERS,
    }
    data = open(file_directory, 'rb')

    async with aiohttp.ClientSession() as session:
        async with session.post(SEND_VOICE_URL, headers=headers, data=data) as sent_voice:
            await sent_voice.json()


async def send_voice_vote(token, voice_id, is_valid):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
        **HEADERS,
    }

    data = {'challenge': 'null', "isValid": is_valid}
    request_url = VOICE_VOTE_URL.format(voice_id)
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, data=json.dumps(data), headers=headers) as posted_vote:
            posted_vote_response = await posted_vote.json()


async def skip_voice(token, voice_id):
    headers = {
        'Authorization': token,
        **HEADERS,
    }

    request_url = SKIP_VOICE_URL.format(int(voice_id))
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, headers=headers) as skipped_voice:
            skipped_voice_response = await skipped_voice.json()


async def skip_sentence(token, sentence_id):
    headers = {
        'Authorization': token,
        **HEADERS,
    }

    request_url = SKIP_SENTENCE_URL.format(sentence_id)
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, headers=headers) as skipped_sentence:
            skipped_sentence_response = await skipped_sentence.json()


async def report_function(token, kind, id_to_report, report_type):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
        **HEADERS,
    }

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


async def handle_operation(token, operation):
    voice_id = operation['voice_id'] if 'voice_id' in operation else None
    sentence_id = operation['sentence_id'] if 'sentence_id' in operation else None
    if operation["type"] == "vote":
        return await send_voice_vote(token, voice_id, operation["command"] == 'accept')
    elif operation["type"] == "report_clip":
        return await report_function(token, 'clip', voice_id, operation["command"])
    elif operation["type"] == "skip_clip":
        return await skip_voice(token, voice_id)
    elif operation["type"] == "report_sentence":
        return await report_function(token, 'sentence', sentence_id, operation["command"])
    elif operation["type"] == "skip_sentence":
        return await skip_sentence(token, sentence_id)
    elif operation["type"] == "send_voice":
        await send_text_voice(token, operation["file_directory"], sentence_id)
        os.remove(operation["file_directory"])
        return

    # otherwise throw
    raise Exception("Unknown operation type")
