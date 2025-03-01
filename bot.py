import os
import asyncio
from pyrogram import Client, filters, idle
from flask import Flask
from threading import Thread

# Load environment variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_KEYWORD = "@Animes2u"  # Custom keyword added at the beginning of filenames

# Ensure required environment variables are set
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("❌ Missing required environment variables: API_ID, API_HASH, or BOT_TOKEN.")

API_ID = int(API_ID)  # Convert API_ID to int

# Initialize Pyrogram Client
bot = Client("bulk_thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app to keep the bot alive
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 Bot is running!"

# Directory to save thumbnails
THUMB_DIR = "thumbnails"
os.makedirs(THUMB_DIR, exist_ok=True)

# Command to set a thumbnail
@bot.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client, message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await client.download_media(message.photo, file_name=file_path)
    await message.reply_text("✅ Thumbnail saved successfully!")

# Command to change the thumbnail of a file and rename it
@bot.on_message(filters.document)
async def change_thumbnail(client, message):
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")

    if not os.path.exists(thumb_path):
        await message.reply_text("⚠️ No thumbnail found! Send an image with /set_thumb to set one.")
        return

    await message.reply_text("🔄 Changing thumbnail and renaming file...")

    # Download the document
    file_path = await message.download()

    if not file_path:
        await message.reply_text("❌ Failed to download file.")
        return

    # Extract original filename and extension
    original_filename = message.document.file_name
    file_name, file_ext = os.path.splitext(original_filename)

    # Ensure the default keyword is at the beginning
    if not file_name.startswith(DEFAULT_KEYWORD):
        new_filename = f"{DEFAULT_KEYWORD} {file_name}{file_ext}"
    else:
        new_filename = f"{file_name}{file_ext}"

    try:
        # Send the document with the new filename and thumbnail
        await client.send_document(
            chat_id=message.chat.id,
            document=file_path,
            thumb=thumb_path,  # Attach the new thumbnail
            file_name=new_filename,
            caption=f"✅ File renamed and thumbnail changed: {new_filename}",
        )
        await message.reply_text("✅ Done! Here is your updated file.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to change thumbnail: {e}")

# Start command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Hello! Send an image with /set_thumb to set a thumbnail, then send a file to rename and change its thumbnail."
    )

# Function to run Flask in a separate thread
def run_flask():
    port = int(os.environ.get("PORT", 8080))  # Render assigns a dynamic port
    print(f"🌍 Starting Flask server on port {port}...")
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🤖 Bot is starting...")

    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Pyrogram bot
    try:
        bot.start()
        print("✅ Bot is online and ready to receive commands.")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

    # Keep bot running and listening to messages
    idle()

    print("🛑 Bot stopped.")
    bot.stop()
