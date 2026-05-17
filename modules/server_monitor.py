import logging
import psutil
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from config import is_admin

logger = logging.getLogger(__name__)

async def server_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    keyboard = [
        [InlineKeyboardButton("📊 Kiểm tra RAM & CPU", callback_data="svr_stats")],
        [InlineKeyboardButton("💾 Kiểm tra Ổ Cứng", callback_data="svr_disk")],
        [InlineKeyboardButton("🔄 Khởi động lại Bot", callback_data="svr_restart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🖥 *Giám Sát & Điều Khiển Server*:", reply_markup=reply_markup, parse_mode='Markdown')

async def server_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id): return
    await query.answer()
    
    if query.data == "svr_stats":
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        msg = f"📊 *Trạng thái hệ thống:*\n- CPU: `{cpu}%`\n- RAM: `{ram.percent}%` ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)"
        await query.edit_message_text(msg, parse_mode='Markdown')
    elif query.data == "svr_disk":
        # Hỗ trợ Termux trên Android: kiểm tra thư mục home thay vì root '/' để tránh PermissionError
        disk_path = '/data/data/com.termux/files/home' if 'PREFIX' in os.environ else '/'
        try:
            disk = psutil.disk_usage(disk_path)
        except PermissionError:
            disk_path = os.path.expanduser('~')
            disk = psutil.disk_usage(disk_path)
            
        msg = f"💾 *Dung lượng lưu trữ ({disk_path}):*\n- Trống: `{disk.free // (1024**3)}GB` / `{disk.total // (1024**3)}GB` ({disk.percent}% đã dùng)"
        await query.edit_message_text(msg, parse_mode='Markdown')
    elif query.data == "svr_restart":
        await query.edit_message_text("🔄 Đang khởi động lại Bot...")
        # Khởi động lại an toàn cho mọi môi trường (Termux/Windows/Linux)
        os.execl(sys.executable, sys.executable, *sys.argv)

def setup(application):
    application.add_handler(CommandHandler("server", server_command))
    application.add_handler(CallbackQueryHandler(server_callback, pattern="^svr_"))
