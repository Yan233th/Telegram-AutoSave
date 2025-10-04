from telethon import events
from telethon.tl.types import Message, User, DocumentAttributeSticker, MessageMediaDocument


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


async def process_message(msg, conn, save_message, save_or_update_user):
    sender = await msg.get_sender()

    if sender and isinstance(sender, User):
        save_or_update_user(conn, sender.id, sender.first_name, sender.last_name, sender.username)

    if msg.text:
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
    elif msg.sticker or (msg.document and any(isinstance(attr, DocumentAttributeSticker) for attr in msg.document.attributes)):
        emoji = get_sticker_emoji(msg)
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, emoji, "sticker")


async def fetch_history(client, conn, target_chat, save_message, save_or_update_user):
    async for msg in client.iter_messages(target_chat, reverse=True):
        if not isinstance(msg, Message):
            continue  # Skip system messages
        await process_message(msg, conn, save_message, save_or_update_user)


def register_handlers(client, conn, target_chat, save_message, save_or_update_user):
    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        msg = event.message
        if not isinstance(msg, Message):
            return  # Skip system messages
        await process_message(msg, conn, save_message, save_or_update_user)
