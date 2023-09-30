from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Regexp
from aiogram.utils import executor
from commands import set_bot_commands
import re
import openai
import json
import signal
import sys
import requests
from datetime import datetime
from pydantic_settings import BaseSettings
from prompt import Prompt


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ''
    OPENAI_API_TOKEN: str = ''
    PROXYCURL_API_TOKEN: str = ''

    class Config:
        env_file = '.env'


settings = Settings()
openai.api_key = settings.OPENAI_API_TOKEN
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
db = dict()

url_pattern = r'(https?://\S+)'


def link_parser(profile_url: str):
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    header_dic = {'Authorization': 'Bearer ' + settings.PROXYCURL_API_TOKEN}
    params = {
        'url': profile_url,
        'fallback_to_cache': 'on-error',
        'use_cache': 'if-present',
        'skills': 'include',
        'inferred_salary': 'include',
        'personal_email': 'include',
        'personal_contact_number': 'include',
        'twitter_profile_id': 'include',
        'facebook_profile_id': 'include',
        'github_profile_id': 'include',
        'extra': 'include',
    }
    try:
        response = requests.get(api_endpoint, params=params, headers=header_dic).json()
    except:
        return 'Something went wrong with this profile'
    res = dict()
    res['name'] = response['full_name']
    res['description'] = response['summary']
    res['country'] = response['country_full_name']
    res['work'] = []
    for i in range(min(2, len(response['experiences']))):
        q = response['experiences'][i]
        for el in q:
            if q[el] is None:
                q[el] = 'None'
        res['work'] += [
            f"Company: {q['company']}, Role: {q['title']}, Description: {q['description']}"
        ]
    res['years'] = 20 + (datetime.now().year - response['experiences'][-1]['starts_at']['year'])
    return res


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await bot.send_message(
        message.chat.id,
        """Hi! I can generate pesonilized letters for a job candidates based on the job description and LinkedIn profile of a candidate. 
Send me a job description.""",
    )


@dp.message_handler(commands=['change'])
async def update_job_description(message: types.Message):
    await bot.send_message(
        message.chat.id,
        'Send me a new job description.',
    )


@dp.message_handler(Regexp(url_pattern))
async def create_letter(message: types.Message):
    if str(message.chat.id) not in db['job_descriptions']:
        await message.reply(
            "I'm sorry, due to technical issues I lost the job description. Please send it again."
        )
        return
    msg = await message.reply('Started parsing profile and generating amazing letter...')
    url = re.search(url_pattern, message.text).group(0)
    job_description = db['job_descriptions'][str(message.chat.id)]
    user_info = link_parser(url)
    if isinstance(user_info, str):
        await bot.send_message(message.chat.id, user_info)
        return
    prompt = Prompt(
        job_description,
        user_info['name'],
        user_info['description'],
        user_info['work'],
        user_info['years'],
        user_info['country'],
    )
    db['last_prompts'][str(message.chat.id)] = prompt.prompt
    try:
        completion = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt.prompt}],
            max_tokens=1000,
            temperature=0.8,
        )
        db['requests_counter']['gpt-4'] += 1
    except:
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt.prompt}],
            max_tokens=1000,
            temperature=0.8,
        )
        db['requests_counter']['gpt-3.5-turbo'] += 1
    letter = completion.choices[0].message.content
    await bot.delete_message(msg.chat.id, msg['message_id'])
    await message.reply(letter)


@dp.message_handler()
async def get_job_description(message: types.Message):
    db['job_descriptions'][str(message.chat.id)] = message.text
    await bot.send_message(
        message.chat.id,
        'Alright, now send me a link to a LinkedIn profile.',
    )


async def on_startup(*args):
    await set_bot_commands(dp)
    global db
    with open('db.json', 'r') as f:
        db = json.load(f)
    print('Starting up...')


async def on_shutdown(*args):
    global db
    with open('db.json', 'w') as f:
        json.dump(db, f, indent=4)
    print('Shutting down...')


def save_and_exit(signalNumber, frame):
    print('Received signal, saving state...')
    global db
    with open('db.json', 'w') as f:
        json.dump(db, f, indent=4)
    sys.exit(0)


signal.signal(signal.SIGINT, save_and_exit)
signal.signal(signal.SIGTERM, save_and_exit)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)