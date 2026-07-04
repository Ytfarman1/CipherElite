"""
Auto Chat Flirting Plugin - GEMINI PRO EDITION
✅ Google Gemini (Free & Fast) Support
✅ Config.py Compatible
✅ Smart Context-Aware Fallback (No API needed)
"""

import asyncio
import logging
import random
from telethon import events

# Gemini Support
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config.config import Config
from utils.decorators import sudo_only

logger = logging.getLogger(__name__)

# ------------------------ SETTINGS ------------------------

FLIRT_SETTINGS = {
    "enabled": True,
    "style": "playful",  # playful, romantic, confident, sweet
    "auto_reply": True,
    "blacklist": [],
    "whitelist": {},
    "response_delay": 0,
    "all_users_enabled": True,
}

FLIRT_PROMPTS = {
    "playful": """You are a flirty, playful, and witty chat bot. 
    Respond to this message with a short, cheeky, and fun flirty reply in Hinglish (max 100 chars).
    Keep it light-hearted and teasing. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
    
    "romantic": """You are a romantic and charming chat bot.
    Respond to this message with a sweet, romantic flirty reply in Hinglish (max 100 chars).
    Be genuine and heartfelt. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
    
    "confident": """You are a confident and bold chat bot.
    Respond to this message with a confident and flirty reply in Hinglish (max 100 chars).
    Be bold but respectful. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
    
    "sweet": """You are a cute and sweet chat bot.
    Respond to this message with an adorable and flirty reply in Hinglish (max 100 chars).
    Be wholesome and kind. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
}

# ------------------------ MANAGER CLASS ------------------------

class AutoFlirtManager:
    def __init__(self, client):
        self.client = client
        self.settings = FLIRT_SETTINGS.copy()
        self.model = None
        
        # Pull key from Config file smoothly
        gemini_key = getattr(Config, "GEMINI_API_KEY", None)
        
        if genai and gemini_key:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("⚠️ GEMINI_API_KEY Config file ya Env Vars me nahi mili! Fallback mode active.")
        
    async def generate_flirty_reply(self, message_text: str) -> str:
        """Generate flirty reply using Gemini OR Smart Fallback"""
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
            logger.error(f"Error generating flirty reply with Gemini: {e}")
            return self.get_smart_fallback_reply(message_text)
    
    def get_smart_fallback_reply(self, message_text: str) -> str:
        text = message_text.lower()
        if any(word in text for word in ["nam", "name", "naam", "apna", "tumhara", "your name", "kya naam"]):
            return random.choice(["Mera naam hai 'Aapka Crush' 😉", "I'm your secret admirer, naam kya rakhu? 😏"])
        elif any(word in text for word in ["kaise", "how are", "kya hal", "kese", "kesi", "kya haal"]):
            return random.choice(["Aapko dekh ke toh bahut achha lag raha hai 😘", "Better now that you're here 😉"])
        elif any(word in text for word in ["hi", "hello", "hey", "hlo", "hola"]):
            return random.choice(["Ooh, hello there! 👋", "Hi cutie! 😉", "Hey there, I was waiting for you! ❤️"])
        else:
            return random.choice(["Smooth talker, huh? 😏", "I like where this is going 😏", "Ooh, interesting! 😂"])

    def is_user_enabled(self, user_id: int) -> bool:
        if not self.settings["all_users_enabled"]:
            return self.settings["whitelist"].get(user_id, False)
        return user_id not in self.settings["blacklist"]
    
    async def should_reply(self, user_id: int) -> bool:
        if not self.settings["auto_reply"] or not self.is_user_enabled(user_id):
            return False
        return True

# ------------------------ COMMAND FUNCTIONS ------------------------

@sudo_only
async def cmd_flirt_toggle(event):
    flirt_manager.settings["auto_reply"] = not flirt_manager.settings["auto_reply"]
    status = "✅ ON" if flirt_manager.settings["auto_reply"] else "❌ OFF"
    await event.edit(f"Auto Flirt: {status}")

@sudo_only
async def cmd_flirt_style(event, style: str):
    if style not in FLIRT_PROMPTS:
        await event.edit(f"❌ Invalid style! Use: {', '.join(FLIRT_PROMPTS.keys())}")
        return
    flirt_manager.settings["style"] = style
    await event.edit(f"✅ Flirt style changed to: **{style}**")

@sudo_only
async def cmd_flirt_status(event):
    all_status = "✅ ON" if flirt_manager.settings["all_users_enabled"] else "❌ OFF"
    auto_status = "✅ ON" if flirt_manager.settings["auto_reply"] else "❌ OFF"
    api_status = "✅ Active (Gemini)" if flirt_manager.model else "⚠️ Fallback Mode"
    
    status_text = f"""
🎭 **Auto Flirt Status**
━━━━━━━━━━━━━━━━━━━
✅ Auto Reply: {auto_status}
🌍 All Users: {all_status}
💕 Style: {flirt_manager.settings['style']}
🤖 Engine: {api_status}
"""
    await event.edit(status_text)

# ------------------------ GLOBAL MANAGER VARIABLE ------------------------
flirt_manager = None

def init(client_instance):
    global flirt_manager
    if not flirt_manager:
        flirt_manager = AutoFlirtManager(client_instance)
        logger.info("✅ Auto Flirt Manager Initialized via Config")

async def register_commands():
    global flirt_manager
    if not flirt_manager: return
    client = flirt_manager.client

    async def private_flirt_handler(event):
        if not flirt_manager or not flirt_manager.settings.get("auto_reply", False): return
        sender_id = event.sender_id
        message_text = event.text or ""
        if not message_text or sender_id == (await event.client.get_me()).id: return
        if not await flirt_manager.should_reply(sender_id): return
        try:
            reply = await flirt_manager.generate_flirty_reply(message_text)
            await event.respond(reply)
        except Exception as e: logger.error(f"Flirt Handler Error: {e}")

    client.remove_event_handler(private_flirt_handler)
    client.add_event_handler(private_flirt_handler, events.NewMessage(incoming=True, func=lambda e: e.is_private))

    async def cmd_toggle(event): await cmd_flirt_toggle(event)
    client.remove_event_handler(cmd_toggle)
    client.add_event_handler(cmd_toggle, events.NewMessage(pattern=r"\.flirttoggle$"))

    async def cmd_style(event):
        style = event.pattern_match.group(1)
        await cmd_flirt_style(event, style)
    client.remove_event_handler(cmd_style)
    client.add_event_handler(cmd_style, events.NewMessage(pattern=r"\.flirtstyle (.+)"))

    async def cmd_status(event): await cmd_flirt_status(event)
    client.remove_event_handler(cmd_status)
    client.add_event_handler(cmd_status, events.NewMessage(pattern=r"\.flirtstatus$"))

    logger.info("✅ Auto Flirt: Handlers registered!")
