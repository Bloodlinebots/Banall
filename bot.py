import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("banall_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply("👋 Bot is online!\nAdd me to a group as admin with ban permissions.")


@app.on_message(filters.command("check") & filters.private)
async def check_group(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /check <group_id>")

    group_id = int(message.command[1])
    try:
        member = await client.get_chat_member(group_id, "me")
        if member.status == "administrator" and member.can_restrict_members:
            await message.reply("✅ Bot is admin in the group *with* ban rights.")
        else:
            await message.reply("❌ Bot is in the group but doesn't have ban rights.")
    except RPCError as e:
        await message.reply(f"❌ Error: {e}")


@app.on_message(filters.command("banall") & filters.private)
async def ban_all(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /banall <group_id>")
    
    group_id = int(message.command[1])
    try:
        bot_member = await client.get_chat_member(group_id, "me")
        if bot_member.status != "administrator" or not bot_member.can_restrict_members:
            return await message.reply("❌ Bot doesn't have admin rights with ban permissions.")

        async for member in client.get_chat_members(group_id):
            if member.status in ["administrator", "creator"]:
                continue
            try:
                await client.ban_chat_member(group_id, member.user.id)
                print(f"Banned {member.user.id}")
            except Exception as e:
                print(f"Failed to ban {member.user.id}: {e}")

        await message.reply("✅ All non-admins (users & bots) banned successfully!")
    except Exception as e:
        await message.reply(f"❌ Failed to execute ban: {e}")


app.run()
