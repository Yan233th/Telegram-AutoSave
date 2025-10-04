# saver.py
from telethon import events
from telethon.tl.types import Message, User, DocumentAttributeSticker, MessageMediaDocument


# 沿用我們之前修正過的 emoji 提取函數
def get_sticker_emoji(msg):
    if hasattr(msg.sticker, "emoji") and msg.sticker.emoji:
        return msg.sticker.emoji
    doc = None
    if isinstance(msg.media, MessageMediaDocument):
        doc = msg.media.document
    if not doc and hasattr(msg, "sticker"):
        doc = msg.sticker
    if doc and hasattr(doc, "attributes"):
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                return attr.alt or "[sticker]"
    return "[sticker]"


# 公共處理邏輯，提取並儲存訊息和使用者
async def process_message(msg, conn, save_message, save_or_update_user):
    # 獲取傳送者實體
    sender = await msg.get_sender()

    # 只有當傳送者是使用者時才儲存其資訊
    if sender and isinstance(sender, User):
        save_or_update_user(conn, sender.id, sender.first_name, sender.last_name, sender.username)

    # 儲存訊息內容
    if msg.text:
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
    elif msg.sticker or (msg.document and any(isinstance(attr, DocumentAttributeSticker) for attr in msg.document.attributes)):
        emoji = get_sticker_emoji(msg)
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, emoji, "sticker")


def register_handlers(client, conn, target_chat, save_message, save_or_update_user):
    """
    註冊實時消息處理器
    """

    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        msg = event.message
        if not isinstance(msg, Message):
            return  # 跳過系統消息
        await process_message(msg, conn, save_message, save_or_update_user)


async def fetch_history(client, conn, target_chat, save_message, save_or_update_user):
    """
    拉取歷史消息
    """
    async for msg in client.iter_messages(target_chat, reverse=True):
        if not isinstance(msg, Message):
            continue  # 跳過系統消息
        await process_message(msg, conn, save_message, save_or_update_user)
