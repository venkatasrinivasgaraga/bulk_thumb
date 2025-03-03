import os
import re
import asyncio
import requests
from pyrogram import Client, filters, idle
from flask import Flask
from threading import Thread

# Load environment variables
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_KEYWORD = "[@Animes2u] "

# Ensure required environment variables are set
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("❌ Missing API_ID, API_HASH, or BOT_TOKEN.")

# Initialize Pyrogram Bot
bot = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app for web hosting (keep bot alive)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 Bot is running!"

# Directory for storing user thumbnails
THUMB_DIR = "thumbnails"
os.makedirs(THUMB_DIR, exist_ok=True)

# ✅ Set Thumbnail Command
@bot.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client, message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await client.download_media(message.photo, file_name=file_path)
    await message.reply_text("✅ Thumbnail saved successfully!")

# ✅ File Rename & Thumbnail Change
@bot.on_message(filters.document)
async def rename_file(client, message):
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")

    # Check if thumbnail exists
    if not os.path.exists(thumb_path):
        await message.reply_text("⚠️ No thumbnail found! Use /set_thumb to set one.")
        return

    # Download the document
    file_path = await client.download_media(message)
    if not file_path:
        await message.reply_text("❌ Failed to download file.")
        return

    # Extract filename and extension
    file_name, file_ext = os.path.splitext(message.document.file_name)

    # ✅ Remove unwanted text but KEEP numbers & quality indicators
    clean_name = re.sub(r"@\S+?|(?!E\d+|[0-9]{3,4}p)[^]*?", "", file_name).strip()

    # Ensure the filename starts with [@Animes2u]
    new_filename = f"{DEFAULT_KEYWORD}{clean_name}{file_ext}"
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)

    # Rename the file
    os.rename(file_path, new_file_path)

    try:
        # Send the renamed file with thumbnail
        await client.send_document(
            chat_id=message.chat.id,
            document=new_file_path,
            thumb=thumb_path,
            file_name=new_filename,
            caption=f"✅ Renamed: {new_filename}",
        )
    finally:
        os.remove(new_file_path)  # Ensure temp file is deleted

# ✅ Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Hello! Send an image with /set_thumb to set a thumbnail, then send a file to rename & apply the thumbnail."
    )

# ✅ Keep-Alive Function (Prevents Render from stopping the bot)
async def keep_alive():
    while True:
        try:
            requests.get("https://your-app-name.onrender.com")
        except Exception as e:
            print(f"Keep-alive failed: {e}")
        await asyncio.sleep(120)  # Ping every 2 minutes

# Run Flask in a separate thread
def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render assigns a dynamic port
    print(f"🌍 Starting Flask on port {port}...")
    web_app.run(host="0.0.0.0", port=port)

# ✅ Start the bot
async def main():
    # Start Flask server
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start keep-alive task
    asyncio.create_task(keep_alive())

    async with bot:
        print("✅ Bot is online.")
        await idle()

    print("🛑 Bot stopped.")

# ✅ Fix Event Loop Issue for Render
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
