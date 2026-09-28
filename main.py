import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

# --- معرف حساب الأدمن (المسؤول) ---
ADMIN_ID = 5964212312

# --- متغيرات حفظ الإحصائيات في الذاكرة ---
stats = {
    "total_downloads": 0,
    "users": set()
}

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
    user_id = update.effective_user.id
    stats["users"].add(user_id)
    await update.message.reply_text("أهلاً بك! أرسل لي رابط الفيديو لتحميله فوراً.")

# --- أمر إظهار الإحصائيات ---
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("عذراً، هذا الأمر مخصص لمالك البوت فقط.")
        return

    total_users = len(stats["users"])
    total_downloads = stats["total_downloads"]

    msg = (
        "📊 **إحصائيات البوت:**\n\n"
        f"👤 **عدد المستخدمين:** {total_users}\n"
        f"📥 **إجمالي عمليات التحميل:** {total_downloads}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats["users"].add(user_id)
    
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")):
        return

    msg = await update.message.reply_text("جاري تحميل الفيديو، انتظر لحظة...")

    # خيارات محسّنة لتجاوز قيود يوتيوب وباقي المواقع
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
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
            stats["total_downloads"] += 1
        else:
            await msg.edit_text("حدث خطأ أثناء العثور على الملف المحمل.")
    except Exception as e:
        await msg.edit_text(f"فشل التحميل من يوتيوب: {str(e)}")

def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
