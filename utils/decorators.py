from functools import wraps
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from config.config import Config


# ==========================================
# HELPER FUNCTION
# ==========================================
async def is_owner_or_sudo(event):
    sender_id = event.sender_id

    if hasattr(Config, "OWNER_ID") and sender_id == Config.OWNER_ID:
        return True

    if hasattr(Config, "SUDO_USERS") and sender_id in Config.SUDO_USERS:
        return True

    try:
        me = await event.client.get_me()
        if sender_id == me.id:
            return True
    except Exception:
        pass

    return False


# ==========================================
# 1. ADMIN / OWNER / SUDO DECORATOR
# ==========================================
def authorized_users_only(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event):
            sender_id = event.sender_id

            if await is_owner_or_sudo(event):
                print(f"✅ Owner/Sudo user {sender_id} authorized")
                return await f(event)

            if event.is_private:
                return await f(event)

            try:
                chat = await event.get_chat()

                if hasattr(chat, "admin_rights") and chat.admin_rights:
                    if chat.admin_rights.delete_messages or chat.admin_rights.ban_users:
                        return await f(event)

                if hasattr(chat, "creator") and chat.creator:
                    return await f(event)

                try:
                    participant = await event.client(
                        GetParticipantRequest(
                            channel=chat,
                            participant=sender_id
                        )
                    )

                    if isinstance(
                        participant.participant,
                        (ChannelParticipantAdmin, ChannelParticipantCreator),
                    ):
                        return await f(event)

                except (UserNotParticipantError, ChatAdminRequiredError, AttributeError):
                    pass

            except Exception as e:
                print(e)

            await event.reply(
                "🎭 **Cipher Elite Access Denied**\n\n"
                "❌ Admin/Sudo required."
            )

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# ==========================================
# 2. OWNER & SUDO ONLY
# ==========================================
def rishabh(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event):
            sender_id = event.sender_id

            if not await is_owner_or_sudo(event):
                print(f"❌ Unauthorized access attempt by {sender_id}")
                return

            return await f(event)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# ==========================================
# 3. OWNER & SUDO ONLY (HELP)
# ==========================================
def rishabh_help(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event):

            if not await is_owner_or_sudo(event):
                error_msg = (
                    "🎭 **Cipher Elite Access Restricted!**\n\n"
                    "🔒 Deploy your own bot.\n"
                    "https://github.com/rishabhops/CipherElite"
                )

                if isinstance(event, events.CallbackQuery.Event):
                    await event.answer(error_msg, alert=True)

                elif isinstance(event, events.InlineQuery.Event):
                    await event.answer([])

                else:
                    await event.reply(error_msg)

                return

            return await f(event)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# ==========================================
# OLD COMPATIBILITY
# ==========================================
def sudo_only(func=None):
    return rishabh(func)
