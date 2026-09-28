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

# --- التوكن الخاص بك ---
TOKEN = "8887888837:AAHFL1y6CIdRLtepktcHVpVtvsrqNssHUFY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي أي رابط فيديو (يوتيوب، تيك توك، انستغرام) وسأقوم بتحميله فوراً 🚀")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith(("http://", "https://")):
        return

    msg = await update.message.reply_text("جاري التحميل... انتظر لحظة ⏳")
    file_path = f"video_{update.message.message_id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).download([url]))
        
        await msg.edit_text("جاري رفع الفيديو إلى تليجرام ⬆️")
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"حدث خطأ أثناء التحميل: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    # تشغيل خادم الويب في الخلفية
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # تشغيل البوت
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is running...")
    app.run_polling()
