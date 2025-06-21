import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id   = 20863170
api_hash = 'e2bc54b0dc62fd727dc655a4107a5dcc'

async def main():
    # создаём пустую сессию
    session = StringSession()
    client  = TelegramClient(session, api_id, api_hash)
    # запустим, чтобы провести аутентификацию
    await client.start()  
    # теперь session содержит ваш логин-токен  
    print('YOUR_STRING_SESSION =', session.save())
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
