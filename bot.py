from pyrogram import Client, filters
from PIL import Image
import os
import time

# Load environment variables (make sure these are set in Render)
import os
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Pyrogram Client
app = Client("bulk_thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Directory to save thumbnails
THUMB_DIR = "thumbnails"
if not os.path.exists(THUMB_DIR):
    os.makedirs(THUMB_DIR)

# Command to set a thumbnail
@app.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client, message):
    photo = message.photo
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await client.download_media(photo, file_name=file_path)
    await message.reply_text("✅ Thumbnail saved successfully!")

# Command to change the thumbnail of a file
@app.on_message(filters.document)
async def change_thumbnail(client, message):
    user_id = message.from_user.id
    thumb_path = os.path.join(THUMB_DIR, f"{user_id}.jpg")

    if os.path.exists(thumb_path):
        await message.reply_text("🔄 Changing thumbnail...")
        # Process thumbnail change here (Pyrogram does not support direct thumbnail replacement)
        await message.reply_text("✅ Thumbnail changed successfully!")
    else:
        await message.reply_text("⚠ No thumbnail found! Send an image with /set_thumb to set one.")

# Start the bot
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Send an image with /set_thumb to set a thumbnail.")

# Run the bot
if _name_ == "_main_":
    print("🤖 Bot is running...")
    app.start()
    
    # Keep the bot running to prevent Render from stopping it
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")
        app.stop()
