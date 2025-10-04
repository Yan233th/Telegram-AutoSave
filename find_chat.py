import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")


async def list_chats():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print("正在列出所有对话...")
    async for dialog in client.iter_dialogs():
        print(f"{dialog.name} → {dialog.id}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(list_chats())
