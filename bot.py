import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("ultrafast_ban_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_clients = {}  # Store user_id -> TelethonClient


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    await message.reply(
        "👋 I'm your UltraFast Ban Bot!\n\nAdd me to a group as admin with ban rights.\nOr connect your own session using `/connect <string>`.\n\nCommands:\n✅ `/check <group_id>`\n💣 `/banall <group_id>`"
    )


@app.on_message(filters.command("connect") & filters.private)
async def connect_userbot(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/connect <string>`")

    session = message.command[1]
    user_id = message.from_user.id

    try:
        user_client = TelegramClient(StringSession(session), API_ID, API_HASH)
        await user_client.start()
        user_clients[user_id] = user_client
        me = await user_client.get_me()
        await message.reply(
            f"✅ Userbot connected as <b>{me.first_name}</b> (<code>{me.id}</code>)",
            parse_mode="html"
        )
    except Exception as e:
        await message.reply(f"❌ Failed to connect userbot: <code>{e}</code>", parse_mode="html")


async def has_ban_rights_pyro(client, group_id):
    try:
        bot_member = await client.get_chat_member(group_id, "me")
        return bot_member.status == "administrator" and bot_member.can_restrict_members
    except:
        return False


async def has_ban_rights_telethon(client, group_id):
    try:
        rights = await client.get_permissions(group_id, "me")
        return rights.is_admin and rights.ban_users
    except:
        return False


@app.on_message(filters.command("check") & filters.private)
async def check_admin_power(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/check <group_id>`")

    group_id = int(message.command[1])
    user_id = message.from_user.id

    pyro_has_power = await has_ban_rights_pyro(client, group_id)
    tele_has_power = False

    if user_id in user_clients:
        tele_has_power = await has_ban_rights_telethon(user_clients[user_id], group_id)

    response = "🔍 Ban Power Check:\n\n"
    response += f"🤖 Bot: {'✅ Yes' if pyro_has_power else '❌ No'}\n"
    response += f"👤 UserBot: {'✅ Yes' if tele_has_power else '❌ No'}"

    await message.reply(response)


@app.on_message(filters.command("banall") & filters.private)
async def ban_all_users(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/banall <group_id>`")

    group_id = int(message.command[1])
    user_id = message.from_user.id
    pyro = await has_ban_rights_pyro(client, group_id)
    tele = False
    user_client = None

    if user_id in user_clients:
        user_client = user_clients[user_id]
        tele = await has_ban_rights_telethon(user_client, group_id)

    if not pyro and not tele:
        return await message.reply("❌ Neither bot nor userbot has ban rights in that group.")

    await message.reply("🚨 Initiating MASS BAN...\n🧠 Smart fallback logic activated.\n⚔️ Speed: 40 bans/sec")

    banned = 0
    failed = 0
    batch = 0

    try:
        async for member in client.get_chat_members(group_id):
            if member.status in ["administrator", "creator"]:
                continue

            try:
                if pyro:
                    await client.ban_chat_member(group_id, member.user.id)
                elif tele:
                    await user_client.edit_permissions(group_id, member.user.id, view_messages=False)
                else:
                    failed += 1
                    continue

                banned += 1
                batch += 1

            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
            except Exception:
                failed += 1

            if batch == 40:
                await asyncio.sleep(1)
                batch = 0

        await message.reply(
            f"✅ MASS BAN COMPLETE!\n🔨 Banned: <code>{banned}</code>\n❌ Failed: <code>{failed}</code>",
            parse_mode="html"
        )
    except Exception as e:
        await message.reply(f"❌ Unexpected error: <code>{e}</code>", parse_mode="html")


app.run()
