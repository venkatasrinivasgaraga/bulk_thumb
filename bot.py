import os
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image

# Telegram API credentials
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Create bot client
app = Client("thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Directory for storing thumbnails
THUMBNAIL_DIR = "thumbnails"
if not os.path.exists(THUMBNAIL_DIR):
    os.makedirs(THUMBNAIL_DIR)

# Dictionary to store user thumbnails
user_thumbnails = {}

@app.on_message(filters.command("start"))
def start(bot, message):
    message.reply_text("Hello! Send me a thumbnail first, then send files to apply that thumbnail.")

@app.on_message(filters.photo)
def save_thumbnail(bot, message):
    user_id = message.from_user.id
    file_path = f"{THUMBNAIL_DIR}/thumb_{user_id}.jpg"

    # Download and resize the thumbnail
    photo = message.photo.file_id
    photo_file = bot.download_media(photo, file_path)

    img = Image.open(photo_file)
    img.thumbnail((320, 180))  # Resize to Telegram's required size
    img.save(file_path, "JPEG", quality=85)

    user_thumbnails[user_id] = file_path
    message.reply_text("✅ Thumbnail saved! Now send me files to apply this thumbnail.")

@app.on_message(filters.document | filters.video)
def change_thumbnail(bot, message: Message):
    user_id = message.from_user.id

    print(f"📂 Received file from user {user_id}")  # Debug log

    if user_id not in user_thumbnails:
        message.reply_text("⚠ Please send a thumbnail first!")
        return

    thumb_path = user_thumbnails[user_id]
    print(f"🖼 Using thumbnail: {thumb_path}")  # Debug log

    file = message.document or message.video
    file_id = file.file_id
    file_name = file.file_name or "file.mp4"

    print(f"⬇ Downloading file: {file_name}")  # Debug log
    downloaded_file = bot.download_media(file_id, f"{THUMBNAIL_DIR}/{file_name}")

    print("🚀 Sending file with new thumbnail...")  # Debug log
    message.reply_document(
        document=downloaded_file,
        thumb=thumb_path,
        caption="✅ Here is your file with the new thumbnail!"
    )

    print("✅ File sent successfully!")  # Debug log
    os.remove(downloaded_file)

print("🤖 Bot is running...")
app.run()
