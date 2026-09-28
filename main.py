
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# التوكن الخاص بك مدمج وجاهز
TOKEN = "8887888837:AAHFL1y6CIdRLtepktcHVpVtvsrqNssHUFY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي أي رابط فيديو (يوتيوب، تيك توك، انستغرام) وسأقوم بتحميله فوراً 🚀")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith(("http://", "https://")):
        return

    msg = await update.message.reply_text("⏳ جاري معالجة الرابط والتحميل...")
    file_path = f"video_{update.message.message_id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'quiet': True
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).download([url]))
        
        await msg.edit_text("⬆️ جاري رفع الفيديو إلى تليجرام...")
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == '__main__':
    main()
