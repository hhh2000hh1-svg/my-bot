import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# --- خادم ويب وهمي لتشغيل الخطة المجانية على Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- التوكين الخاص بك ---
TOKEN = "8887888837:AAFwmzMR-ZdPUsE08AMM2TGoBvYeNXDqAqk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط الفيديو لتحميله فوراً.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith(("http://", "https://")):
        return

    msg = await update.message.reply_text("جاري تحميل الفيديو، انتظر لحظة...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).download([url]))

        video_filename = None
        for file in os.listdir('.'):
            if file.startswith('downloaded_video.'):
                video_filename = file
                break

        if video_filename:
            with open(video_filename, 'rb') as video:
                await update.message.reply_video(video=video)
            os.remove(video_filename)
            await msg.delete()
        else:
            await msg.edit_text("حدث خطأ أثناء العثور على الملف المحمل.")
    except Exception as e:
        await msg.edit_text(f"فشل التحميل: {str(e)}")

def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
