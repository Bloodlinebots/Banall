import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("ultrafast_ban_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    await message.reply(
        "👋 I'm your UltraFast Ban Bot!\n\nAdd me to a group as admin with ban rights.\n\nUse:\n✅ `/check <group_id>` — to check ban power\n💣 `/banall <group_id>` — to ban all non-admins in warp speed!"
    )


@app.on_message(filters.command("check") & filters.private)
async def check_admin_power(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/check <group_id>`")

    try:
        group_id = int(message.command[1])
        bot_member = await client.get_chat_member(group_id, "me")

        if bot_member.status == "administrator" and bot_member.can_restrict_members:
            await message.reply("✅ I have ban power in that group.")
        else:
            await message.reply("❌ I'm in the group but don't have ban rights.")
    except RPCError as e:
        await message.reply(f"❌ Error: {e}")


@app.on_message(filters.command("banall") & filters.private)
async def ban_all_users(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/banall <group_id>`")

    group_id = int(message.command[1])
    try:
        bot_member = await client.get_chat_member(group_id, "me")
        if bot_member.status != "administrator" or not bot_member.can_restrict_members:
            return await message.reply("❌ I don't have admin + ban permissions in that group.")

        await message.reply("🚨 Initiating mass ban protocol...\n⚔️ Speed: 10 bans/sec\n🛡️ Skipping admins/creators...")

        banned = 0
        failed = 0
        batch = 0

        async for member in client.get_chat_members(group_id):
            if member.status in ["administrator", "creator"]:
                continue
            try:
                await client.ban_chat_member(group_id, member.user.id)
                banned += 1
                batch += 1
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
            except Exception:
                failed += 1

            if batch == 10:
                await asyncio.sleep(1)
                batch = 0

        await message.reply(f"✅ Mass ban complete!\n🔨 Banned: `{banned}`\n❌ Failed: `{failed}`")
    except Exception as e:
        await message.reply(f"❌ Unexpected error: {e}")


app.run()
