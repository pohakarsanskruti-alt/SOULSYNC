import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing from Railway VAriables")
print("BOT TOKEN FOUND: ", BOT_TOKEN is not None)
favorites = {}
playlists = {}


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎧 Play Music", callback_data="play"),
            InlineKeyboardButton("🔍 Search", callback_data="search"),
        ],
        [
            InlineKeyboardButton("❤️ Favorites", callback_data="favorites"),
            InlineKeyboardButton("📂 Playlists", callback_data="playlists"),
        ],
        [
            InlineKeyboardButton("⚙️ Help", callback_data="help"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎵 *Welcome to SOULSYNC*\n\n"
        "Your Personal Music Companion 🎧",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎶 Music Bot Help\n\n"
        "/play <song name> - Search for a song\n"
        "/help - Show this message"
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🎵 Please enter a song name.\nExample:\n/play Believer"
        )
        return

    song = " ".join(context.args)

    await update.message.reply_text("🔍 Searching...")

    url = "https://itunes.apple.com/search"

    params = {
        "term": song,
        "limit": 5,
        "media": "music"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        await update.message.reply_text("❌ Couldn't search right now.")
        return

    data = response.json()

    if data["resultCount"] == 0:
        await update.message.reply_text("❌ No songs found.")
        return

    track = data["results"][0]

    name = track.get("trackName", "Unknown")
    artist = track.get("artistName", "Unknown")
    album = track.get("collectionName", "Unknown")
    preview = track.get("previewUrl")

    message = (
        f"🎵 *{name}*\n\n"
        f"👤 Artist: {artist}\n"
        f"💿 Album: {album}"
    )

    if preview:
     keyboard = [
    [InlineKeyboardButton("▶️ Listen Preview", url=preview)],
    [InlineKeyboardButton("❤️ Add to Favorites", callback_data=f"fav|{name}")],
    [InlineKeyboardButton("📂 Add to Playlist", callback_data=f"plist|{name}")]
]

     reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        reply_markup = None

    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    


async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in favorites or not favorites[user_id]:
        await update.message.reply_text("❤️ Your favorites list is empty.")
        return

    message = "❤️ Your Favorite Songs\n\n"

    for i, song in enumerate(favorites[user_id], start=1):
        message += f"{i}. 🎵 {song}\n"

    await update.message.reply_text(message)



async def playlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in playlists or not playlists[user_id]:
        await update.message.reply_text("📂 Your playlist is empty.")
        return

    message = "📂 Your Playlist\n\n"

    for i, song in enumerate(playlists[user_id], start=1):
        message += f"{i}. 🎵 {song}\n"

    await update.message.reply_text(message)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("fav|"):
        user_id = query.from_user.id
        song = query.data.split("|", 1)[1]

        if user_id not in favorites:
            favorites[user_id] = []

        if song not in favorites[user_id]:
            favorites[user_id].append(song)

        await query.answer("❤️ Added to Favorites!")
        return

    if query.data.startswith("plist|"):
        user_id = query.from_user.id
        song = query.data.split("|", 1)[1]

        if user_id not in playlists:
            playlists[user_id] = []

        if song not in playlists[user_id]:
            playlists[user_id].append(song)

        await query.answer("📂 Added to Playlist!")
        return

    if query.data == "play":
        await query.edit_message_text("🎧 Send:\n/play <song name>")

    elif query.data == "search":
        await query.edit_message_text("🔍 Send:\n/play <song name>")

    elif query.data == "favorites":
        await query.edit_message_text("❤️ Favorites feature coming soon!")

    elif query.data == "playlists":
        await query.edit_message_text("📂 Playlists feature coming soon!")

    elif query.data == "help":
        await query.edit_message_text(
            "🎶 Commands:\n"
            "/play <song>\n"
            "/help"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("favorites", favorites_command))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("playlist", playlist_command))

    print("🎵 Music Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()