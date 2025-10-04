# saver.py
from telethon import events
from telethon.tl.types import Message, DocumentAttributeSticker, MessageMediaDocument

def get_sticker_emoji(msg):
    """
    安全地從消息中獲取貼圖的 emoji。
    Telethon 可能會將貼圖作為 Sticker 對象或附加了貼圖屬性的 Document 對象處理。
    此函數兼容這兩種情況。
    """
    # 情況一：處理普通貼圖或 Telethon 正確識別的 Sticker 對象
    # 注意：有時 msg.sticker 本身就是一個 Document，所以要先檢查類型
    if hasattr(msg.sticker, 'emoji') and msg.sticker.emoji:
        return msg.sticker.emoji

    # 情況二：處理被視為 Document 的貼圖（如 .webm, .tgs 動畫貼圖）
    # 這包括 msg.media 是 Document，或者 msg.sticker 本身就是 Document
    doc = None
    if isinstance(msg.media, MessageMediaDocument):
        doc = msg.media.document
    
    # 兜底檢查，有時 msg.sticker 就是 document
    if not doc and hasattr(msg, 'sticker'):
         doc = msg.sticker

    if doc and hasattr(doc, 'attributes'):
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                # attr.alt 儲存了貼圖關聯的 emoji
                return attr.alt or "[sticker]"
    
    return "[sticker]" # 如果都找不到，返回一個通用標籤

def register_handlers(client, conn, target_chat, save_message):
    """
    註冊實時消息處理器
    """
    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        msg = event.message
        if not isinstance(msg, Message):
            return  # 跳過系統消息
        
        if msg.text:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
        elif msg.sticker or msg.media and isinstance(msg.media, MessageMediaDocument):
            emoji = get_sticker_emoji(msg)
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, emoji, "sticker")


async def fetch_history(client, conn, target_chat, save_message):
    """
    拉取歷史消息
    """
    async for msg in client.iter_messages(target_chat, reverse=True):
        if not isinstance(msg, Message):
            continue  # 跳過系統消息
        
        if msg.text:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
        # 檢查是否為貼圖（包括普通貼圖和被視為文件的貼圖）
        elif msg.sticker or msg.media and isinstance(msg.media, MessageMediaDocument):
            emoji = get_sticker_emoji(msg)
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, emoji, "sticker")