from telethon import events


def register_handlers(client, conn, target_chat, save_message):
    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        msg = event.message
        if msg.text:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
        elif msg.sticker:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.sticker.emoji or "", "sticker")
        elif msg.emoji:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.emoji, "emoji")


async def fetch_history(client, conn, target_chat, save_message):
    async for msg in client.iter_messages(target_chat, reverse=True):
        if msg.text:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.text, "text")
        elif msg.sticker:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.sticker.emoji or "", "sticker")
        elif msg.emoji:
            save_message(conn, msg.id, msg.chat_id, msg.sender_id, msg.date, msg.emoji, "emoji")
