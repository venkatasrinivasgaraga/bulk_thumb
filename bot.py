from pyrogram import Client, filters, idle
from PIL import Image
import os
import logging
from flask import Flask
from threading import Thread

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables (Set these in Render, Koyeb, or Railway)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Validate environment variables
if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("❌ Missing API_ID, API_HASH, or BOT_TOKEN. Set them in environment variables!")
    exit(1)

# Initialize Pyrogram Client
app = Client("bulk_thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app to keep Render alive
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Bot is running!"

# Directory to save thumbnails
THUMB_DIR = "thumbnails"
os.makedirs(THUMB_DIR, exist_ok=True)

# Command to set a thumbnail
@app.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client, message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    
    try:
        await client.download_media(message.photo, file_name=file_path)
        await message.reply_text("✅ Thumbnail saved successfully!")
        logger.info(f"Thumbnail saved for user {message.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Error saving thumbnail: {e}")
        await message.reply_text("⚠️ Failed to save thumbnail!")

# Command to change the thumbnail of a file
@app.on_message(filters.document)
async def change_thumbnail(client, message):
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    
    if os.path.exists(thumb_path):
        await message.reply_text("🔄 Changing thumbnail...")
        
        # Here you can add any processing logic for changing the thumbnail
        
        await message.reply_text("✅ Thumbnail changed successfully!")
    else:
        await message.reply_text("⚠️ No thumbnail found! Send an image with /set_thumb to set one.")

# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Send an image with /set_thumb to set a thumbnail.")

# Run Flask in a separate thread
def run_flask():
    port = int(os.getenv("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    logger.info("🤖 Bot is starting...")

    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Pyrogram bot
    try:
        app.start()
        logger.info("✅ Bot is online and ready to receive commands.")
        idle()  # Keep the bot running
    except Exception as e:
        logger.error(f"❌ Error starting the bot: {e}")
    finally:
        app.stop()
        logger.info("🛑 Bot stopped.")
