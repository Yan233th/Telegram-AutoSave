import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")

# 代理配置
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False").lower() == "true"
PROXY_TYPE = os.getenv("PROXY_TYPE", "socks5")  # socks5 / socks4 / http
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", 1080))
PROXY_RDNS = os.getenv("PROXY_RDNS", "False").lower() == "true"

proxy = None
if PROXY_ENABLED:
    proxy = (PROXY_TYPE, PROXY_HOST, PROXY_PORT, PROXY_RDNS)


async def list_chats():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH, proxy=proxy)
    await client.start()
    print("正在列出所有对话...")
    async for dialog in client.iter_dialogs():
        print(f"{dialog.name} → {dialog.id}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(list_chats())
