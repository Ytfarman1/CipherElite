"""
Auto Chat Flirting Plugin — Gemini API Edition
✅ Works in Private (replies to every incoming PM)
✅ Works in Groups ONLY when you are Tagged or Replied to (consent-based —
   never replies to random group messages nobody addressed to the bot)
✅ Google Gemini API (free tier) — falls back to built-in smart replies
   if no key is set or the API fails, so it never crashes.
"""

import asyncio
import logging
import random
from telethon import events

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config.config import Config
from utils.decorators import sudo_only

logger = logging.getLogger(__name__)

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
    "playful": """You are a flirty, playful, and witty chat bot.
    Respond to this message with a short, cheeky, and fun flirty reply (max 100 chars).
    Keep it light-hearted and teasing. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
    "romantic": """You are a romantic and charming chat bot.
    Respond to this message with a sweet, romantic flirty reply (max 100 chars).
    Be genuine and heartfelt. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
    "confident": """You are a confident and bold chat bot.
    Respond to this message with a confident and flirty reply (max 100 chars).
    Be bold but respectful. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
    "sweet": """You are a cute and sweet chat bot.
    Respond to this message with an adorable and flirty reply (max 100 chars).
    Be wholesome and kind. Use emojis if appropriate.
    Message: {msg}
    Reply:""",
}

class AutoFlirtManager:
    def __init__(self, client):
        self.client = client
        self.settings = FLIRT_SETTINGS.copy()
        self._gemini_model = None

        if genai and hasattr(Config, "GEMINI_API_KEY") and Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self._gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")

    async def generate_flirty_reply(self, message_text: str) -> str:
        try:
            if self._gemini_model:
                style = self.settings["style"]
                prompt = FLIRT_PROMPTS[style].format(msg=message_text)
                response = await asyncio.to_thread(self._gemini_model.generate_content, prompt)
                reply = (response.text or "").strip()
                if reply:
                    return reply[:150]
                return self.get_smart_fallback_reply(message_text)
            else:
                return self.get_smart_fallback_reply(message_text)
        except Exception as e:
            logger.error(f"Error generating flirty reply: {e}")
            return self.get_smart_fallback_reply(message_text)

    def get_smart_fallback_reply(self, message_text: str) -> str:
        text = message_text.lower()
        if any(word in text for word in ["nam", "name", "naam", "apna", "tumhara", "your name", "kya naam"]):
            return random.choice([
                "Mera naam hai 'Aapka Crush' 😉",
                "I'm your secret admirer, naam kya rakhu? 😏",
                "Naam toh batao pehle, phir main bataunga 😘",
                "Mera naam Flirty Bot, aapka? 💕"
            ])
        elif any(word in text for word in ["kaise", "how are", "kya hal", "kese", "kesi", "kya haal"]):
            return random.choice([
                "Aapko dekh ke toh bahut achha lag raha hai 😘",
                "Better now that you're here 😉",
                "Main toh theek hoon, aap sunao? 💕",
                "Abhi toh aapka message aaya, aur achha ho gaya 😏"
            ])
        elif any(word in text for word in ["kya", "what", "why", "kyu", "kaun", "who"]):
            return random.choice([
                "Kya kya soch rahe ho aap mere baare mein? 😏",
                "Aap jo chahein, main wahi hoon 😉",
                "Pata nahi, lekin aapka khayal achha lagta hai 💭",
                "Itna sawaal? Pehle date pe chalein? 😂"
            ])
        elif any(word in text for word in ["hi", "hello", "hey", "hlo", "hola"]):
            return random.choice([
                "Ooh, hello there! 👋",
                "Hi cutie! 😉",
                "Hey there, I was waiting for you! ❤️",
                "Namaste! Aap kaise ho? 😘"
            ])
        else:
            return random.choice([
                "Smooth talker, huh? 😏",
                "I like where this is going 😏",
                "Ooh, interesting! 😂",
                "Not bad, not bad 😏💕",
                "Mujhe tumse baat karke maza aa raha hai ✨"
            ])

    def is_user_enabled(self, user_id: int) -> bool:
        if not self.settings["all_users_enabled"]:
            return self.settings["whitelist"].get(user_id, False)
        else:
            return user_id not in self.settings["blacklist"]

    async def should_reply(self, user_id: int) -> bool:
        if not self.settings["auto_reply"]:
            return False
        if not self.is_user_enabled(user_id):
            return False
        return True

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
async def cmd_flirt_blacklist(event, action: str, user_id: int = None):
    if action == "add" and user_id:
        if user_id not in flirt_manager.settings["blacklist"]:
            flirt_manager.settings["blacklist"].append(user_id)
        await event.edit(f"✅ User {user_id} added to blacklist")
    elif action == "remove" and user_id:
        if user_id in flirt_manager.settings["blacklist"]:
            flirt_manager.settings["blacklist"].remove(user_id)
        await event.edit(f"✅ User {user_id} removed from blacklist")
    elif action == "list":
        blacklist = flirt_manager.settings["blacklist"]
        if blacklist:
            await event.edit(f"🚫 Blacklist: {', '.join(map(str, blacklist))}")
        else:
            await event.edit("✅ Blacklist is empty")

@sudo_only
async def cmd_flirt_set_user(event, user_id: int, status: str):
    is_enabled = status.lower() == "on"
    flirt_manager.settings["whitelist"][user_id] = is_enabled
    status_text = "✅ ON" if is_enabled else "❌ OFF"
    await event.edit(f"User {user_id}: Flirt {status_text}")

@sudo_only
async def cmd_flirt_set_all(event, status: str):
    flirt_manager.settings["all_users_enabled"] = status.lower() == "on"
    status_text = "✅ ON" if flirt_manager.settings["all_users_enabled"] else "❌ OFF"
    info = f"""
🌍 **All Users Flirt Status: {status_text}**
{'When ON: Bot replies to all users (except blacklist)' if flirt_manager.settings['all_users_enabled'] else 'When OFF: Bot only replies to whitelisted users'}
"""
    await event.edit(info)

@sudo_only
async def cmd_flirt_delay(event, seconds: int):
    flirt_manager.settings["response_delay"] = seconds
    await event.edit(f"✅ Response delay set to {seconds} seconds")

@sudo_only
async def cmd_flirt_status(event):
    all_status = "✅ ON" if flirt_manager.settings["all_users_enabled"] else "❌ OFF"
    auto_status = "✅ ON" if flirt_manager.settings["auto_reply"] else "❌ OFF"
    ai_status = "🟢 Gemini AI" if flirt_manager._gemini_model else "🟡 Smart Fallback (no API key set)"
    whitelist_count = len([u for u, v in flirt_manager.settings["whitelist"].items() if v])
    blacklist_count = len(flirt_manager.settings["blacklist"])
    status_text = f"""
🎭 **Auto Flirt Status**
━━━━━━━━━━━━━━━━━━━
🧠 Engine: {ai_status}
✅ Auto Reply: {auto_status}
🌍 All Users: {all_status}
💕 Style: {flirt_manager.settings['style']}
⏰ Delay: {flirt_manager.settings['response_delay']}s
✅ Whitelisted: {whitelist_count} users
🚫 Blacklisted: {blacklist_count} users
"""
    await event.edit(status_text)

flirt_manager = None

def init(client_instance):
    global flirt_manager
    if not flirt_manager:
        flirt_manager = AutoFlirtManager(client_instance)
        flirt_manager.client = client_instance
        logger.info("✅ Auto Flirt Manager Initialized")

async def register_commands():
    global flirt_manager
    if not flirt_manager:
        logger.error("Flirt Manager initialized नहीं है!")
        return

    client = flirt_manager.client

    async def private_flirt_handler(event):
        if not flirt_manager or not flirt_manager.settings.get("auto_reply", False):
            return
        sender_id = event.sender_id
        message_text = event.text or ""
        if not message_text or sender_id == (await event.client.get_me()).id:
            return
        if not await flirt_manager.should_reply(sender_id):
            return
        try:
            reply = await flirt_manager.generate_flirty_reply(message_text)
            if flirt_manager.settings.get("response_delay", 0) > 0:
                await asyncio.sleep(flirt_manager.settings["response_delay"])
            await event.respond(reply)
        except Exception as e:
            logger.error(f"Flirt Handler Error: {e}")

    client.remove_event_handler(private_flirt_handler)
    client.add_event_handler(private_flirt_handler, events.NewMessage(incoming=True, func=lambda e: e.is_private))

    async def group_flirt_handler(event):
        if not flirt_manager or not flirt_manager.settings.get("auto_reply", False):
            return
        sender_id = event.sender_id
        message_text = event.text or ""
        me_id = (await event.client.get_me()).id
        if not message_text or sender_id == me_id:
            return
        is_reply_to_bot = False
        if event.is_reply:
            replied = await event.get_reply_message()
            if replied and replied.sender_id == me_id:
                is_reply_to_bot = True
        is_mentioned = bool(getattr(event.message, "mentioned", False))
        if not (is_reply_to_bot or is_mentioned):
            return
        if not await flirt_manager.should_reply(sender_id):
            return
        try:
            reply = await flirt_manager.generate_flirty_reply(message_text)
            if flirt_manager.settings.get("response_delay", 0) > 0:
                await asyncio.sleep(flirt_manager.settings["response_delay"])
            await event.reply(reply)
        except Exception as e:
            logger.error(f"Group Flirt Handler Error: {e}")

    client.remove_event_handler(group_flirt_handler)
    client.add_event_handler(group_flirt_handler, events.NewMessage(incoming=True, func=lambda e: not e.is_private))

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

    async def cmd_delay(event):
        seconds = int(event.pattern_match.group(1))
        await cmd_flirt_delay(event, seconds)
    client.remove_event_handler(cmd_delay)
    client.add_event_handler(cmd_delay, events.NewMessage(pattern=r"\.flirtdelay (\d+)"))

    async def cmd_setall(event):
        status = event.pattern_match.group(1)
        await cmd_flirt_set_all(event, status)
    client.remove_event_handler(cmd_setall)
    client.add_event_handler(cmd_setall, events.NewMessage(pattern=r"\.setflirtall (on|off)"))

    async def cmd_setuser(event):
        user_id = int(event.pattern_match.group(1))
        status = event.pattern_match.group(2)
        await cmd_flirt_set_user(event, user_id, status)
    client.remove_event_handler(cmd_setuser)
    client.add_event_handler(cmd_setuser, events.NewMessage(pattern=r"\.setflirtuser (\d+) (on|off)"))

    async def cmd_blacklist_add(event):
        action = event.pattern_match.group(1)
        user_id = int(event.pattern_match.group(2))
        await cmd_flirt_blacklist(event, action, user_id)
    client.remove_event_handler(cmd_blacklist_add)
    client.add_event_handler(cmd_blacklist_add, events.NewMessage(pattern=r"\.flirtblacklist (add|remove) (\d+)"))

    async def cmd_blacklist_list(event):
        await cmd_flirt_blacklist(event, "list")
    client.remove_event_handler(cmd_blacklist_list)
    client.add_event_handler(cmd_blacklist_list, events.NewMessage(pattern=r"\.flirtblacklist list$"))

    logger.info("✅ Auto Flirt: सारे हैंडलर सफलतापूर्वक रजिस्टर हो गए!")
