import subprocess
import os
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Foydalanuvchilar tili
user_languages = {}

# Tilga mos xabarlar
messages = {
    'uz': {
        'welcome': "Salom! Instagram videosini yuboring (havola ko'rinishida).",
        'downloading': "🎬 Video yuklanmoqda, iltimos kuting...",
        'error': "Kechirasiz, video yuklab bo‘lmadi. Iltimos, to‘g‘ri havola yuboring.",
        'choose_lang': "Tilni tanlang:",
    },
    'ru': {
        'welcome': "Привет! Отправьте ссылку на видео из Instagram.",
        'downloading': "🎬 Загрузка видео, пожалуйста подождите...",
        'error': "Извините, не удалось скачать видео. Пожалуйста, отправьте правильную ссылку.",
        'choose_lang': "Выберите язык:",
    },
    'en': {
        'welcome': "Hello! Please send an Instagram video link.",
        'downloading': "🎬 Downloading the video, please wait...",
        'error': "Sorry, failed to download. Please send a correct link.",
        'choose_lang': "Choose your language:",
    }
}


# Video yuklovchi funksiyasi
def download_instagram_video(url):
    try:
        timestamp = str(int(time.time()))
        output_template = f'video_{timestamp}.%(ext)s'

        result = subprocess.run(
            ['yt-dlp', '-o', output_template, url],
            capture_output=True,
            text=True
        )
        print("yt-dlp chiqishi:", result.stdout)
        print("yt-dlp xatolari:", result.stderr)

        for ext in ['mp4', 'webm', 'mkv']:
            file = f'video_{timestamp}.{ext}'
            if os.path.exists(file):
                return file
        return None
    except Exception as e:
        print("Xatolik:", e)
        return None


# Tilni aniqlash
def get_lang(user_id):
    return user_languages.get(user_id, 'uz')


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id)
    await update.message.reply_text(messages[lang]['welcome'])


# /language komandasi
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        [["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(messages[get_lang(update.effective_user.id)]['choose_lang'], reply_markup=reply_markup)


# Til tanlash tugmasi
async def handle_language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_choice = update.message.text
    user_id = update.effective_user.id

    if lang_choice == "🇺🇿 O'zbek":
        user_languages[user_id] = 'uz'
    elif lang_choice == "🇷🇺 Русский":
        user_languages[user_id] = 'ru'
    elif lang_choice == "🇬🇧 English":
        user_languages[user_id] = 'en'
    else:
        return

    await update.message.reply_text(messages[get_lang(user_id)]['welcome'])


# Instagram havolalarni qabul qilish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text(messages[lang]['error'])
        return

    await update.message.reply_text(messages[lang]['downloading'])

    video_file = download_instagram_video(url)
    if video_file:
        await update.message.reply_video(video=open(video_file, 'rb'))
        os.remove(video_file)
    else:
        await update.message.reply_text(messages[lang]['error'])


# Botni ishga tushirish
if __name__ == '__main__':
    app = ApplicationBuilder().token("8040877346:AAEJBr6k-eNHTeT9DDdHsbaeeP7-31PjlDA").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(MessageHandler(filters.Regex("🇺🇿|🇷🇺|🇬🇧"), handle_language_choice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()
