"""
Auto Chat Flirting Plugin - GROUP & PRIVATE ENABLED
✅ Works in Private
✅ Works in Groups ONLY when you are Tagged or Replied to
"""

import asyncio
import logging
from telethon import events

# ------------------------ SETTINGS ------------------------
GEMINI_API_KEY = "AIzaSyCh1WUqMcDE_u1_fp_FmVdR1ULkmDY7Qys"

# --- BAKI SETTINGS WAHI HAIN ---
FLIRT_SETTINGS = {"enabled": True, "style": "playful", "auto_reply": True}
FLIRT_PROMPTS = {
    "playful": "You are a flirty, playful, and witty chat bot. Reply to the user with a short, cheeky, and fun flirty reply in Hinglish (max 100 chars). Message: {msg}\nReply:"
}

# --- MANAGER CLASS ---
class AutoFlirtManager:
    def __init__(self, client):
        self.client = client
        self.me = None

    async def get_me(self):
        if not self.me:
            self.me = await self.client.get_me()
        return self.me

# ------------------------ HANDLER ------------------------
flirt_manager = None

def init(client_instance):
    global flirt_manager
    flirt_manager = AutoFlirtManager(client_instance)

async def register_commands():
    global flirt_manager
    if not flirt_manager: return
    client = flirt_manager.client
    me = await flirt_manager.get_me()

    async def flirt_handler(event):
        if not flirt_manager or not flirt_manager.settings.get("auto_reply", True): return
        
        # 1. Private Chat Logic
        if event.is_private:
            if event.sender_id == me.id: return
            reply = await flirt_manager.generate_flirty_reply(event.text or "")
            await event.respond(reply)

        # 2. Group Logic (Sirf Tabhi reply karega agar aapko Tag kiya ya aapke msg pe Reply kiya)
        elif event.is_group:
            # Check if bot is mentioned or replied to you
            is_reply_to_me = event.reply_to and (await event.get_reply_message()).sender_id == me.id
            is_mention = me.username and f"@{me.username}" in event.text
            
            if is_reply_to_me or is_mention:
                reply = await flirt_manager.generate_flirty_reply(event.text or "")
                await event.reply(reply)

    client.add_event_handler(flirt_handler, events.NewMessage(incoming=True))
