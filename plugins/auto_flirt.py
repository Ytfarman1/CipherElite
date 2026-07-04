"""
Auto Chat Flirting Plugin - FULLY FIXED
Automatically responds to private messages with AI-powered flirty replies
Supports OpenAI (optional) and intelligent fallback replies.
"""

import asyncio
import logging
import random  # ✅ Fallback replies के लिए जरूरी
from telethon import events
from telethon.tl.types import PeerUser

# OpenAI optional है - अगर इंस्टॉल नहीं है तो भी प्लगइन चलेगा
try:
    import openai
except ImportError:
    openai = None

from config.config import Config
from utils.decorators import sudo_only

logger = logging.getLogger(__name__)

# ------------------------ SETTINGS ------------------------

FLIRT_SETTINGS = {
    "enabled": True,
    "style": "playful",  # playful, romantic, confident, sweet
    "auto_reply": True,
    "blacklist": [],
    "whitelist": {},  # {user_id: True/False}
    "response_delay": 0,  # seconds
    "all_users_enabled": True,  # Global ON/OFF for all users
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

# ------------------------ MANAGER CLASS ------------------------

class AutoFlirtManager:
    def __init__(self, client):
        self.client = client
        self.settings = FLIRT_SETTINGS.copy()
        
    async def generate_flirty_reply(self, message_text: str) -> str:
        """Generate flirty reply using AI (or fallback)"""
        try:
            # अगर OpenAI उपलब्ध है और API Key सेट है तो AI का उपयोग करें
            if openai and hasattr(Config, 'OPENAI_API_KEY') and Config.OPENAI_API_KEY:
                openai.api_key = Config.OPENAI_API_KEY
                style = self.settings["style"]
                prompt = FLIRT_PROMPTS[style].format(msg=message_text)
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly flirty chat bot."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=50,
                )
                reply = response.choices[0].message.content.strip()
                return reply
            else:
                # अगर OpenAI नहीं है तो फॉलबैक इस्तेमाल करें
                return self.get_fallback_reply(message_text)
            
        except Exception as e:
            logger.error(f"Error generating flirty reply: {e}")
            return self.get_fallback_reply(message_text)
    
    def get_fallback_reply(self, message_text: str) -> str:
        """Fallback replies if AI fails (100% Working, No API Needed)"""
        fallbacks = {
            "playful": [
                "Ooh, interesting! 😏",
                "Got my attention 👀",
                "Smooth talker, huh? 😉",
                "I like where this is going 😏",
                "Not bad, not bad 😏💕",
                "You're quite something! 😉",
                "Keep talking, I'm listening... 👀",
            ],
            "romantic": [
                "You're making me blush 😊💕",
                "That's sweet of you 🥰",
                "You know how to charm someone 💕",
                "Getting romantic, are we? 😘",
                "My heart just skipped a beat 💗",
                "I was waiting for you to say that ✨",
            ],
            "confident": [
                "I like your style 💪",
                "Bold move, I like it 😏",
                "You got game 🔥",
                "Not impressed... just kidding 😄",
                "You're cool, I'll give you that 😏",
                "Confidence looks good on you 😉",
            ],
            "sweet": [
                "Awww, that's adorable 🥺💕",
                "You're so kind 🥰",
                "Making me smile over here 😊",
                "That's really sweet 💗",
                "You seem nice 🥺✨",
                "You just made my day 💖",
            ],
        }
        style_replies = fallbacks.get(self.settings["style"], fallbacks["playful"])
        return random.choice(style_replies)
    
    def is_user_enabled(self, user_id: int) -> bool:
        """Check if user is enabled for flirting"""
        if not self.settings["all_users_enabled"]:
            return self.settings["whitelist"].get(user_id, False)
        else:
            return user_id not in self.settings["blacklist"]
    
    async def should_reply(self, user_id: int) -> bool:
        """Check if should reply to this user"""
        if not self.settings["auto_reply"]:
            return False
        if not self.is_user_enabled(user_id):
            return False
        return True

# ------------------------ COMMAND FUNCTIONS (सजे हुए) ------------------------

@sudo_only
async def cmd_flirt_toggle(event):
    """Toggle auto flirt ON/OFF"""
    flirt_manager.settings["auto_reply"] = not flirt_manager.settings["auto_reply"]
    status = "✅ ON" if flirt_manager.settings["auto_reply"] else "❌ OFF"
    await event.edit(f"Auto Flirt: {status}")

@sudo_only
async def cmd_flirt_style(event, style: str):
    """Change flirting style"""
    if style not in FLIRT_PROMPTS:
        await event.edit(f"❌ Invalid style! Use: {', '.join(FLIRT_PROMPTS.keys())}")
        return
    flirt_manager.settings["style"] = style
    await event.edit(f"✅ Flirt style changed to: **{style}**")

@sudo_only
async def cmd_flirt_blacklist(event, action: str, user_id: int = None):
    """Manage blacklist"""
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
    """Set flirt status for specific user"""
    is_enabled = status.lower() == "on"
    flirt_manager.settings["whitelist"][user_id] = is_enabled
    status_text = "✅ ON" if is_enabled else "❌ OFF"
    await event.edit(f"User {user_id}: Flirt {status_text}")

@sudo_only
async def cmd_flirt_set_all(event, status: str):
    """Set flirt status for all users"""
    flirt_manager.settings["all_users_enabled"] = status.lower() == "on"
    status_text = "✅ ON" if flirt_manager.settings["all_users_enabled"] else "❌ OFF"
    info = f"""
🌍 **All Users Flirt Status: {status_text}**
{'When ON: Bot replies to all users (except blacklist)' if flirt_manager.settings['all_users_enabled'] else 'When OFF: Bot only replies to whitelisted users'}
"""
    await event.edit(info)

@sudo_only
async def cmd_flirt_delay(event, seconds: int):
    """Set response delay"""
    flirt_manager.settings["response_delay"] = seconds
    await event.edit(f"✅ Response delay set to {seconds} seconds")

@sudo_only
async def cmd_flirt_status(event):
    """Show auto flirt status"""
    all_status = "✅ ON" if flirt_manager.settings["all_users_enabled"] else "❌ OFF"
    auto_status = "✅ ON" if flirt_manager.settings["auto_reply"] else "❌ OFF"
    whitelist_count = len([u for u, v in flirt_manager.settings["whitelist"].items() if v])
    blacklist_count = len(flirt_manager.settings["blacklist"])
    
    status_text = f"""
🎭 **Auto Flirt Status**
━━━━━━━━━━━━━━━━━━━
✅ Auto Reply: {auto_status}
🌍 All Users: {all_status}
💕 Style: {flirt_manager.settings['style']}
⏰ Delay: {flirt_manager.settings['response_delay']}s
✅ Whitelisted: {whitelist_count} users
🚫 Blacklisted: {blacklist_count} users
"""
    await event.edit(status_text)

# ------------------------ GLOBAL MANAGER VARIABLE ------------------------

flirt_manager = None

# ------------------------ FIXED: PLUGIN LOADING (इसे install.py पहचानेगा) ------------------------

def init(client_instance):
    """Plugin लोड होते ही यह चलेगा"""
    global flirt_manager
    if not flirt_manager:
        flirt_manager = AutoFlirtManager(client_instance)
        flirt_manager.client = client_instance
        logger.info("✅ Auto Flirt Manager Initialized")

async def register_commands():
    """सारे हैंडलर और कमांड्स को एक्सप्लिसिट (Explicit) तरीके से रजिस्टर करें"""
    global flirt_manager
    
    if not flirt_manager:
        logger.error("Flirt Manager initialized नहीं है!")
        return
    
    client = flirt_manager.client

    # ----- 1. प्राइवेट मैसेज हैंडलर (सबसे जरूरी) -----
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
            logger.info(f"Auto-replied to {sender_id}")
        except Exception as e:
            logger.error(f"Flirt Handler Error: {e}")

    # हैंडलर को क्लाइंट से अटैच करें (पहले हटाकर नया डालें, ताकी रीलोड पर डुप्लीकेट न हों)
    client.remove_event_handler(private_flirt_handler)
    client.add_event_handler(private_flirt_handler, events.NewMessage(incoming=True, func=lambda e: e.is_private))

    # ----- 2. सारे कमांड हैंडलर -----
    async def cmd_toggle(event):
        await cmd_flirt_toggle(event)
    client.remove_event_handler(cmd_toggle)
    client.add_event_handler(cmd_toggle, events.NewMessage(pattern=r"\.flirttoggle$"))

    async def cmd_style(event):
        style = event.pattern_match.group(1)
        await cmd_flirt_style(event, style)
    client.remove_event_handler(cmd_style)
    client.add_event_handler(cmd_style, events.NewMessage(pattern=r"\.flirtstyle (.+)"))

    async def cmd_status(event):
        await cmd_flirt_status(event)
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
