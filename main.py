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
        # <<< 1. 主要邏輯放入 try 區塊 >>>
        await client.start()

        # 歷史補全
        await fetch_history(client, conn, TARGET_CHAT, save_message, save_or_update_user)
        print("歷史消息同步完成")

        # 實時監聽
        register_handlers(client, conn, TARGET_CHAT, save_message, save_or_update_user)
        print("開始監聽新消息... (按 Ctrl+C 退出)")
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        # <<< 2. 捕捉到 Ctrl+C 時，打印提示訊息 >>>
        # 這個區塊可以為空，因為主要清理工作在 finally 中完成
        print("\n檢測到退出指令，正在關閉程式...")

    finally:
        # <<< 3. 無論如何都會執行的清理區塊 >>>
        # 確保客戶端和資料庫連線都被安全關閉
        print("正在清理資源...")
        if client.is_connected():
            await client.disconnect()
            print("Telegram 客戶端已斷開連接。")
        
        if conn:
            conn.close()
            print("資料庫連線已關閉。")
        
        print("程式已安全退出。")


if __name__ == "__main__":
    # 在 Python 3.11+ 中，可以使用 asyncio.run 的 shutdown_asyncgens=True 來幫助清理
    # 但這裡的 try/finally 結構更為通用和明確
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 為了處理在 asyncio.run 啟動前就按 Ctrl+C 的極端情況
        pass