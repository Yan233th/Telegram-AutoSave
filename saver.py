from asyncio import sleep
from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.types import User, DocumentAttributeSticker, MessageMediaDocument


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
    # Check if sender_id exists, as system messages may not have one.
    if msg.sender_id:
        sender = await msg.get_sender()
        if sender and isinstance(sender, User):
            save_or_update_user(conn, sender.id, sender.first_name, sender.last_name, sender.username)

    if msg.text:
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
    elif msg.sticker or (msg.document and any(isinstance(attr, DocumentAttributeSticker) for attr in msg.document.attributes)):
        emoji = get_sticker_emoji(msg)
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, emoji, "sticker")
    else:
        # Handle other types, including system messages (MessageService).
        # Save the string representation of the message object for inspection.
        save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, str(msg), "other")


async def fetch_history(client, conn, target_chat, save_message, save_or_update_user):
    while True:
        try:
            async for msg in client.iter_messages(target_chat, reverse=True):
                await process_message(msg, conn, save_message, save_or_update_user)
            break

        except FloodWaitError as e:
            print(f"Server requests are too frequent. Please wait {e.seconds} seconds...")
            await sleep(e.seconds)

        except Exception as e:
            print(f"Unknown error occurred while fetching history: {e}, retrying in 10 seconds...")
            await sleep(10)


def register_handlers(client, conn, target_chat, save_message, save_or_update_user):
    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        msg = event.message
        await process_message(msg, conn, save_message, save_or_update_user)
