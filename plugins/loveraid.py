import random
from pyrogram import Client, filters
from ... import app, eor, cdx, sudo_users_only
from ...modules.mongo.raidzone import (
    add_loveraid_user, 
    del_loveraid_user, 
    get_loveraid_users
)

# --------------------------------------------------------------------------------- #
# LOVE QUOTES LIST
# --------------------------------------------------------------------------------- #
LOVE_QUOTES = [
    "You are the reason I smile every day! ❤️",
    "Tumhari baatein hi meri duniya hain! 🥰",
    "I just can't stop thinking about you! 🥺",
    "You are my sunshine on a rainy day! ☀️",
    "Meri aankhon ko sirf tumhari talaash rehti hai! 👀💖",
    "Can I borrow a kiss? I promise I’ll give it back! 😘",
    "Koi itna pyara kaise ho sakta hai? 💕",
    "You stole my heart, but I'll let you keep it. 💘"
]

# --------------------------------------------------------------------------------- #
# 1. ADD LOVE RAID COMMAND (.lr, .lraid)
# --------------------------------------------------------------------------------- #
@app.on_message(cdx(["lr", "lraid", "loveraid"]))
@sudo_users_only
async def add_love_raid(client: Client, message):
    aux = await eor(message, "**🔄 Processing ...**")
    try:
        if message.reply_to_message:
            if not message.reply_to_message.from_user:
                return await aux.edit("**🤖 Error: Cannot target anonymous admins or channels.**")
            user_id = message.reply_to_message.from_user.id
            
        else:
            if len(message.command) < 2:
                return await aux.edit("**🤖 Reply to a user's message or give username/user_id.**")
            
            target = message.command[1].lstrip("@")
            try:
                user = await client.get_users(target)
                user_id = user.id
            except Exception:
                return await aux.edit("**🤖 Error: User not found. Invalid username/ID.**")

        if message.from_user and user_id == message.from_user.id:
            return await aux.edit("**🤣 How Foolish, You Want To Activate Love Raid On Your Own ID❓**")
        
        lraid = await add_loveraid_user(user_id)
        if lraid:
            return await aux.edit("**🤖 Successfully Added Love Raid On This User.**")
        
        return await aux.edit("**🤖 Hey, Love Raid Already Active On This User❗**")
        
    except Exception as e:
        print(f"Error in add_love_raid: {e}")
        return await aux.edit(f"**🤖 An error occurred:** `{e}`")

# --------------------------------------------------------------------------------- #
# 2. DELETE LOVE RAID COMMAND (.dlr, .dlraid)
# --------------------------------------------------------------------------------- #
@app.on_message(cdx(["dlr", "dlraid", "dloveraid"]))
@sudo_users_only
async def del_love_raid(client: Client, message):
    aux = await eor(message, "**🔄 Processing ...**")
    try:
        if message.reply_to_message:
            if not message.reply_to_message.from_user:
                return await aux.edit("**🤖 Error: Cannot target anonymous admins or channels.**")
            user_id = message.reply_to_message.from_user.id
            
        else:
            if len(message.command) < 2:
                return await aux.edit("**🤖 Reply to a user's message or give username/user_id.**")
            
            target = message.command[1].lstrip("@")
            try:
                user = await client.get_users(target)
                user_id = user.id
            except Exception:
                return await aux.edit("**🤖 Error: User not found. Invalid username/ID.**")
        
        if message.from_user and user_id == message.from_user.id:
            return await aux.edit("**🤣 How Foolish, Why Would I Activate Love Raid On Your ID❓**")
        
        lraid = await del_loveraid_user(user_id)
        if lraid:
            return await aux.edit("**🤖 Successfully Removed Love Raid From This User.**")
        
        return await aux.edit("**🤖 Hey, Love Raid Not Active On This User❗**")
        
    except Exception as e:
        print(f"Error in del_love_raid: {e}")
        return await aux.edit(f"**🤖 An error occurred:** `{e}`")

# --------------------------------------------------------------------------------- #
# 3. THE WATCHER (RAID EXECUTOR)
# --------------------------------------------------------------------------------- #
@app.on_message(filters.incoming & ~filters.me, group=3)
async def love_raid_watcher(client: Client, message):
    try:
        # Ignore messages from channels or anonymous admins
        if not message.from_user:
            return
        
        user_id = message.from_user.id
        
        # Get active love raid users from MongoDB
        raided_users = await get_loveraid_users() 
        
        # If the sender is in our database list, send a random love quote
        if raided_users and user_id in raided_users:
            reply_msg = random.choice(LOVE_QUOTES)
            await message.reply_text(reply_msg)
            
    except Exception as e:
        print(f"Love Raid Watcher Error: {e}")
