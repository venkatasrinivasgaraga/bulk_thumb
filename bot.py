import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message

# ✅ Bot Setup
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Directory for storing user thumbnails
THUMB_DIR = "thumbnails"
os.makedirs(THUMB_DIR, exist_ok=True)

# ✅ Function to clean filename
def clean_filename(original_name):
    # ✅ Remove [@Anime_Artic] or any other tags in square brackets (except E### and ###p)
    original_name = re.sub(r"@Anime_Artic", "", original_name, flags=re.IGNORECASE)  # Remove [@Anime_Artic]
    original_name = re.sub(r"(?!E\d{1,4})(?!\d{3,4}p)[^]+", "", original_name)  # Remove all other brackets except E### and ###p

    # ✅ Extract meaningful parts: Title, Episode (E###), Quality (###p)
    match = re.findall(r"[a-zA-Z]+(?:\s[a-zA-Z]+)*|E\d{1,4}|\d{3,4}p", original_name)

    if match:
        clean_name = " ".join(match)  # Join extracted parts with a space
        return f"[@Animes2u] {clean_name}".strip()  # Add prefix
    return f"[@Animes2u] Unknown_File"

# ✅ Command to set a permanent thumbnail
@bot.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client: Client, message: Message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await client.download_media(message.photo, file_name=file_path)
    await message.reply_text("✅ Thumbnail saved successfully!")

# ✅ Command to delete the thumbnail
@bot.on_message(filters.command("del_thumb"))
async def delete_thumbnail(client: Client, message: Message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    if os.path.exists(file_path):
        os.remove(file_path)
        await message.reply_text("✅ Thumbnail deleted!")
    else:
        await message.reply_text("⚠️ No thumbnail found!")

# ✅ File Rename & Process
@bot.on_message(filters.document)
async def rename_file(client: Client, message: Message):
    file_path = await client.download_media(message)

    if not file_path:
        await message.reply_text("❌ Failed to download file.")
        return

    # Extract filename & clean it
    file_name, file_ext = os.path.splitext(message.document.file_name)
    new_filename = clean_filename(file_name) + file_ext
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)

    # ✅ Rename the file
    os.rename(file_path, new_file_path)

    # ✅ Check if user has set a thumbnail
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    if not os.path.exists(thumb_path):
        thumb_path = None  # No thumbnail set

    try:
        # ✅ Send the renamed file only once
        await client.send_document(
            chat_id=message.chat.id,
            document=new_file_path,
            thumb=thumb_path,
            file_name=new_filename,
            caption=f"✅ Renamed: {new_filename}",
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

    # ✅ Delete the renamed file after sending
    os.remove(new_file_path)

# ✅ Start Command
@bot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "👋 Hello! Send a file, and I'll rename it!\n\n"
        "📸 Use `/set_thumb` to set a permanent thumbnail.\n"
        "🗑 Use `/del_thumb` to delete your thumbnail."
    )

# ✅ Start the bot
bot.run()
