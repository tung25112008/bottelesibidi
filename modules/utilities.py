import logging
import json
import base64
import os
import sys
import subprocess
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from config import is_admin

logger = logging.getLogger(__name__)

async def utility_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    # Bỏ qua nếu tin nhắn không có text
    if not update.message or not update.message.text: return
    
    text = update.message.text.strip()
    
    # Tải video từ link Youtube/Tiktok
    if text.startswith("http") and ("youtube.com" in text or "youtu.be" in text or "tiktok.com" in text):
        await update.message.reply_text("📥 Đang xử lý tải video, vui lòng đợi...")
        try:
            # Sử dụng yt-dlp để tải video (cần cài đặt yt-dlp)
            filename = "downloaded_video.mp4"
            if os.path.exists(filename): os.remove(filename)
            
            cmd = [sys.executable, "-m", "yt_dlp", "-f", "best", "-o", filename, text]
            subprocess.run(cmd, check=True)
            
            if os.path.exists(filename):
                with open(filename, "rb") as video:
                    await update.message.reply_video(video=video)
                os.remove(filename)
            else:
                await update.message.reply_text("❌ Lỗi: Không tìm thấy file tải về.")
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi tải video: {e}")
            logger.error(e)
        return

    # Format JSON
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
            formatted = json.dumps(parsed, indent=4, ensure_ascii=False)
            await update.message.reply_text(f"```json\n{formatted}\n```", parse_mode='Markdown')
            return
        except ValueError:
            pass # Không phải JSON hợp lệ

    # Base64 Encode/Decode
    if text.startswith("b64e:"):
        encoded = base64.b64encode(text[5:].encode()).decode()
        await update.message.reply_text(f"🔐 Base64 Encode:\n`{encoded}`", parse_mode='Markdown')
        return
    if text.startswith("b64d:"):
        try:
            decoded = base64.b64decode(text[5:].encode()).decode()
            await update.message.reply_text(f"🔓 Base64 Decode:\n`{decoded}`", parse_mode='Markdown')
        except Exception:
            await update.message.reply_text("❌ Chuỗi Base64 không hợp lệ.")
        return

def setup(application):
    # Bắt tất cả text để kiểm tra xem có phải link tải hay yêu cầu tiện ích không
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, utility_handler), group=1)
