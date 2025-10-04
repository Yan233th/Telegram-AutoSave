import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from db import init_db, save_message
from saver import register_handlers, fetch_history

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")
TARGET_CHAT = os.getenv("TARGET_CHAT")

PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False").lower() in ("1", "true", "yes")
PROXY_TYPE = os.getenv("PROXY_TYPE", "socks5")
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", 1080))
PROXY_RDNS = os.getenv("PROXY_RDNS", "True").lower() in ("1", "true", "yes")

proxy = (PROXY_TYPE, PROXY_HOST, PROXY_PORT, PROXY_RDNS) if PROXY_ENABLED else None

async def main():
    conn = init_db()
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH, proxy=proxy)
    await client.start()

    # 历史补全
    await fetch_history(client, conn, TARGET_CHAT, save_message)
    print("历史消息同步完成")

    # 实时监听
    register_handlers(client, conn, TARGET_CHAT, save_message)
    print("开始监听新消息...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
