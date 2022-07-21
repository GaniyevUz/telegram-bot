from pprint import pprint

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters, FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup
import requests
import re

bot = Bot('5563981423:AAEdn3J0BnGxZyU0ZtzL_-Z5U6NZAvPWq8E', parse_mode="html")
storage = MemoryStorage()
BOT_NAME = '@Bot'
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    await bot.send_message(chat_id,
                           f'Hello {user_name}, this bot helps you to download media files from social medias such as *tiktok, instagram, youtube, pinterest*',
                           'markdownv2')


@dp.message_handler(filters.Text(contains=['instagram.com']))
async def download_tt(message: Message):
    a = await bot.send_message(message.chat.id, '<i>Downloading from instagram.com...</i>')
    await bot.send_chat_action(message.chat.id, 'upload_document')
    url = message.text
    r = requests.get("https://api.sssgram.com/st-tik/ins/dl", params={"url": "{}".format(url)})
    if r.status_code == 200:
        json = r.json()
        results = json['result']['insBos']
        description = results[0].get('desc', '')
        if json['result']['count'] > 1:
            media = []
            for result in results:
                url = result['url']
                type = 'video' if result['type'] == 'mp4' else 'photo'
                media.append({'type': type, 'media': url})
            else:
                media[-1]['caption'] = description
            await bot.delete_message(message.chat.id, a.message_id)
            await bot.send_media_group(message.chat.id, media=media)
        else:
            await bot.delete_message(message.chat.id, a.message_id)
            if results[0]['type'] == 'mp4':
                await bot.send_video(message.chat.id, results[0]['url'], caption=description)
            else:
                await bot.send_photo(message.chat.id, results[0]['url'], caption=description)


@dp.message_handler(filters.Text(contains=['tiktok.com']))
async def download_tt(message: Message):
    a = await bot.send_message(message.chat.id, '<i>Downloading from tiktok.com...</i>')
    await bot.send_chat_action(message.chat.id, 'upload_video')
    url = "https://tikdown.org/getAjax"
    payload = {'url': message.text, '_token': "t4JdZ9etWtvCbI68c77THtVyYJEtEp4DrGg2Af8W"}
    r = requests.get(url, params=payload).json()['html']
    soup = BeautifulSoup(r, 'html.parser')
    regex = re.compile(r'href="(.*)" name="download"')
    matches = regex.finditer(soup.prettify())
    d = []
    for match in matches:
        d.append(requests.get(match.groups()[0]).content)
    print(d[0])    # https://td-cdn.pw/api.php?download=tikdown.org-34700941555.mp4
    await bot.delete_message(message.chat.id, a.message_id)
    await bot.send_video(message.chat.id, d[0], caption='📥 downloaded by {}'.format(BOT_NAME))
    await bot.send_audio(message.chat.id, d[1], performer="Music", title=BOT_NAME,
                         caption='📥 downloaded by {}'.format(BOT_NAME))


@dp.message_handler(filters.Text(contains=['youtube.com']))
async def download_tt(message: Message):
    a = await bot.send_message(message.chat.id, '<i>Downloading from youtube.com...</i>') # sending proccess message
    await bot.send_chat_action(message.chat.id, 'upload_video')
    url = "https://onlinevideoconverter.pro/api/convert?url={}".format(message.text)
    payload = {"url": message.text, "extension": "mp3"}
    r = requests.post(url, data=payload).json()
    video_url = r['url'][1]['url']
    try:
        await bot.send_video(message.chat.id, requests.get(video_url).content,
                             caption=r['meta']['title'],
                             thumb=requests.get(r['thumb']).content)
    except Exception as e:
        await bot.send_message(message.chat.id, e) # error message
    await bot.delete_message(message.chat.id, a.message_id) # deleting proccess message


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
