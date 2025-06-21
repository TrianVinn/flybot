import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from datetime import datetime

from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from aiohttp import web

# Проверяем, что все секреты переданы
required = ['API_ID','API_HASH','STRING_SESSION','TARGET','DEST_CHAT']
for name in required:
    if name not in os.environ:
        raise RuntimeError(f"❌ Не задана переменная окружения {name}")

api_id      = int(os.environ['API_ID'])
api_hash    = os.environ['API_HASH']
session_str = os.environ['STRING_SESSION']
target      = os.environ['TARGET']
dest_chat   = os.environ['DEST_CHAT']

client = TelegramClient(StringSession(session_str), api_id, api_hash)
last_online = None
user_entity = None  # сюда сохраним get_entity(target)

@client.on(events.Raw)
async def on_raw(upd):
    from telethon.tl.types import UpdateUserStatus
    if not isinstance(upd, UpdateUserStatus):
        return
    global last_online

    # Сразу отфильтровываем по user_id
    if upd.user_id != user_entity.id:
        return

    status = upd.status
    if isinstance(status, types.UserStatusOnline):
        last_online = datetime.now()
        await client.send_message(dest_chat, '✅ Цель сейчас ONLINE')
    elif isinstance(status, types.UserStatusOffline):
        offline_time = datetime.now()
        if last_online:
            delta = offline_time - last_online
            hrs, rem = divmod(delta.seconds, 3600)
            mins, secs = divmod(rem, 60)
            text = f'❌ Цель вышел OFFLINE — был в сети {hrs}ч {mins}м {secs}с'
        else:
            when = status.was_online.astimezone().strftime('%Y-%m-%d %H:%M:%S')
            text = f'❌ Цель вышел OFFLINE (время оффлайна {when})'
        last_online = None
        await client.send_message(dest_chat, text)

async def bot_main():
    global user_entity
    print("=== BOT: стартую… ===", flush=True)
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("StringSession недействителен или просрочен")
    user_entity = await client.get_entity(target)

    try:
        if dest_chat.startswith("https://t.me/+") :
            invite_hash = dest_chat.split("+")[-1]
            await client(ImportChatInviteRequest(invite_hash))
        else:
            await client(JoinChannelRequest(dest_chat))
    except Exception as e:
        print(f"⚠️ Не удалось присоединиться к {dest_chat}: {e}", flush=True)

    await client.send_message(dest_chat, "🤖 Бот запущен, отслеживаю статус…")
    print("=== BOT: готов ===", flush=True)
    await client.run_until_disconnected()

from flask import Flask
from threading import Thread

def run_http():
    app = Flask('')

    @app.route('/')
    def home():
        return 'OK'

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def start_http():
    thread = Thread(target=run_http)
    thread.start()

async def main():
    start_http()  # запускаем Flask-сервер в потоке
    await bot_main()

if __name__ == '__main__':
    asyncio.run(main())
