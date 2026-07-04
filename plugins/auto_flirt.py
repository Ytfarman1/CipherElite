"""
Auto Chat Flirting Plugin - ULTIMATE FIXED VERSION
✅ Direct API Key Support (No Config Errors)
✅ Smart Context-Aware Fallback
✅ 100% Working
"""

import asyncio
import logging
import random
import os
from telethon import events

# Library Import
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from utils.decorators import sudo_only

logger = logging.getLogger(__name__)

# ------------------------ SETTINGS ------------------------

# 💡 YAHAN APNI API KEY PASTE KARO (Double quotes ke andar)
# Example: gemini_key = "AIzaSy..."
GEMINI_API_KEY = "AIzaSyCh1WUqMcDE_u1_fp_FmVdR1ULkmDY7Qys"

FLIRT_SETTINGS = {
    "enabled": True,
    "style": "playful",
    "auto_reply": True,
    "blacklist": [],
    "whitelist": {},
    "response_delay": 0,
    "all_users_enabled": True,
}

FLIRT_PROMPTS = {
    "playful": "You are a flirty, playful, and witty chat bot. Respond to this message with a short, cheeky, and fun flirty reply in Hinglish (max 100 chars). Keep it light-hearted and teasing. Use emojis if appropriate. Message: {msg}\nReply:",
    "romantic": "You are a romantic and charming chat bot. Respond to this message with a sweet, romantic flirty reply in Hinglish (max 100 chars). Be genuine and heartfelt. Use emojis if appropriate. Message: {msg}\nReply:",
    "confident": "You are a confident and bold chat bot. Respond to this message with a confident and flirty reply in Hinglish (max 100 chars). Be bold but respectful. Use emojis if appropriate. Message: {msg}\nReply:",
    "sweet": "You are a cute and sweet chat bot. Respond to this message with an adorable and flirty reply in Hinglish (max 100 chars). Be wholesome and kind. Use emojis if appropriate. Message: {msg}\nReply:",
}

# ------------------------ MANAGER CLASS ------------------------

class AutoFlirtManager:
    def __init__(self, client):
        self.client = client
        self.settings = FLIRT_SETTINGS.copy()
        self.model = None
        
        # Initialize Gemini directly
        if genai and GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSyAapki"):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini AI Engine successfully loaded!")
            except Exception as e:
                logger.error(f"Gemini Init Error: {e}")
        
    async def generate_flirty_reply(self, message_text: str) -> str:
        try:
            if self.model:
                style = self.settings["style"]
                prompt = FLIRT_PROMPTS[style].format(msg=message_text)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self.model.generate_content, prompt)
                if response and response.text:
                    return response.text.strip()
            return self.get_smart_fallback_reply(message_text)
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.get_smart_fallback_reply(message_text)
    
    def get_smart_fallback_reply(self, message_text: str) -> str:
        text = message_text.lower()
        if any(word in text for word in ["nam", "name", "naam", "kya naam"]):
            return random.choice(["Mera naam hai 'Aapka Crush' 😉", "I'm your secret admirer 😏"])
        elif any(word in text for word in ["kaise", "how are", "kya hal"]):
            return random.choice(["Aapko dekh ke toh bahut achha lag raha hai 😘", "Better now that you're here 😉"])
        elif any(word in text for word in ["hi", "hello", "hey"]):
            return random.choice(["Ooh, hello there! 👋", "Hi cutie! 😉", "Hey there, I was waiting for you! ❤️"])
        else:
            return random.choice(["Smooth talker, huh? 😏", "I like where this is going 😏", "Ooh, interesting! 😂"])

    async def should_reply(self, user_id: int) -> bool:
        if not self.settings["auto_reply"] or user_id in self.settings["blacklist"]: return False
        return True

# ------------------------ COMMANDS ------------------------

flirt_manager = None

def init(client_instance):
    global flirt_manager
    flirt_manager = AutoFlirtManager(client_instance)

async def register_commands():
    global flirt_manager
    if not flirt_manager: return
    client = flirt_manager.client

    async def private_flirt_handler(event):
        if not flirt_manager or not flirt_manager.settings.get("auto_reply", False): return
        if event.sender_id == (await event.client.get_me()).id: return
        if await flirt_manager.should_reply(event.sender_id):
            reply = await flirt_manager.generate_flirty_reply(event.text or "")
            await event.respond(reply)

    client.add_event_handler(private_flirt_handler, events.NewMessage(incoming=True, func=lambda e: e.is_private))

    async def cmd_status(event):
        status = "✅ Active" if flirt_manager.model else "⚠️ Fallback Mode"
        await event.edit(f"🎭 **Auto Flirt**\n🤖 Engine: {status}")

    client.add_event_handler(cmd_status, events.NewMessage(pattern=r"\.flirtstatus$"))
