import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from db import init_db, save_message, save_or_update_user
from saver import register_handlers, fetch_history

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")
TARGET_CHAT = int(os.getenv("TARGET_CHAT"))

PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False").lower() in ("1", "true", "yes")
PROXY_TYPE = os.getenv("PROXY_TYPE", "socks5")
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", 1080))
PROXY_RDNS = os.getenv("PROXY_RDNS", "True").lower() in ("1", "true", "yes")

proxy = (PROXY_TYPE, PROXY_HOST, PROXY_PORT, PROXY_RDNS) if PROXY_ENABLED else None


async def main():
    conn = init_db()
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH, proxy=proxy)

    try:
        await client.start()

        await fetch_history(client, conn, TARGET_CHAT, save_message, save_or_update_user)
        print("Historical messages synchronization complete.")

        register_handlers(client, conn, TARGET_CHAT, save_message, save_or_update_user)
        print("Listening for new messages... (Press Ctrl+C to exit)")
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        print("\nExit command detected, shutting down the application...")

    finally:
        print("Cleaning up resources...")
        if client.is_connected():
            await client.disconnect()
            print("Telegram client disconnected.")

        if conn:
            conn.close()
            print("Database connection closed.")

        print("Application has exited gracefully.")


if __name__ == "__main__":
    asyncio.run(main())
