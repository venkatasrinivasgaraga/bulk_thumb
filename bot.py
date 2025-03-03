import os
import re
import hashlib
import asyncio
from pyrogram import Client, filters, idle
from flask import Flask
from threading import Thread

# ✅ Load environment variables
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_KEYWORD = "[@Animes2u] "

# Ensure required environment variables are set
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("❌ Missing API_ID, API_HASH, or BOT_TOKEN.")

# ✅ Initialize Pyrogram Bot
bot = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Flask app to keep the bot alive
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "✅ Bot is running!"

# ✅ Directory for storing thumbnails
THUMB_DIR = "thumbnails"
os.makedirs(THUMB_DIR, exist_ok=True)

# ✅ Function to generate a unique file hash
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

# ✅ Set Thumbnail Command
@bot.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client, message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await client.download_media(message.photo, file_name=file_path)
    await message.reply_text("✅ Thumbnail saved successfully!")

# ✅ Rename & Change Thumbnail
@bot.on_message(filters.document)
async def rename_file(client, message):
    print("📩 File received:", message.document.file_name)

    # ✅ Check if a file was sent
    if not message.document:
        await message.reply_text("❌ No document detected.")
        return

    # ✅ Get user thumbnail
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")

    # ✅ Check file size (max 2GB)
    file_size = message.document.file_size
    max_size = 2 * 1024 * 1024 * 1024  # 2GB

    if file_size > max_size:
        await message.reply_text("❌ File is too large (Max: 2GB).")
        return

    await message.reply_text("⏳ Processing file...")

    # ✅ Download the file
    file_path = await client.download_media(message)
    
    if not file_path:
        await message.reply_text("❌ Failed to download file.")
        return

    print("✅ File downloaded:", file_path)

    # ✅ Check for duplicate file using hash
    file_hash = get_file_hash(file_path)
    saved_hash_path = "file_hashes.txt"

    if os.path.exists(saved_hash_path):
        with open(saved_hash_path, "r") as f:
            saved_hashes = f.read().splitlines()
        
        if file_hash in saved_hashes:
            print("⚠️ Duplicate file detected! Skipping...")
            os.remove(file_path)  # Delete duplicate file
            await message.reply_text("⚠️ This file has already been processed!")
            return

    # ✅ Save the file hash to prevent future duplicates
    with open(saved_hash_path, "a") as f:
        f.write(file_hash + "\n")

    # ✅ Extract filename & extension
    file_name, file_ext = os.path.splitext(message.document.file_name)

    # ✅ Remove [@...] (e.g., [@Anime_Artic]) but keep episode numbers, quality, and Dual
    clean_name = re.sub(r"@[^]]*?", "", file_name).strip()

    # ✅ Keep only [E###], [720p], [1080p], [Dual] and remove other brackets
    clean_name = re.sub(r"(?!E\d+|[0-9]{3,4}p|Dual)[^]*?", "", clean_name).strip()

    # ✅ Add prefix
    new_filename = f"{DEFAULT_KEYWORD}{clean_name}{file_ext}"
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)

    print("🔄 Renaming file to:", new_filename)

    # ✅ Rename the file
    os.rename(file_path, new_file_path)

    try:
        # ✅ Send the renamed file with thumbnail
        await client.send_document(
            chat_id=message.chat.id,
            document=new_file_path,
            thumb=thumb_path if os.path.exists(thumb_path) else None,
            file_name=new_filename,
            caption=f"✅ Renamed: {new_filename}",
        )
        print("📤 File sent successfully!")

    except Exception as e:
        print(f"❌ Error sending file: {e}")
        await message.reply_text(f"❌ Error: {e}")

    finally:
        os.remove(new_file_path)  # ✅ Delete temp file after sending

# ✅ Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Hello! Send an image with /set_thumb to set a thumbnail, then send a file to rename & change its thumbnail."
    )

# ✅ Run Flask in a separate thread
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    print(f"🌍 Starting Flask on port {port}...")
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Bot is starting...")

    # ✅ Start Flask server
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # ✅ Start Telegram Bot
    try:
        bot.start()
        print("✅ Bot is online.")
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")

    # ✅ Keep bot running
    idle()

    print("🛑 Bot stopped.")
    bot.stop()
