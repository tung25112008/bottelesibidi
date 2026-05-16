import logging
import json
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import is_admin, GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Temporary storage for To-do list
todos = []
waiting_for_todo = False

async def nlu_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sử dụng NLU để phân tích nhắc nhở.
    Trong thực tế, bạn có thể gọi API Gemini tại đây để phân tích cú pháp thời gian.
    Vì mục đích demo nhanh, bot sẽ dùng regex cơ bản để bắt các câu nhắc nhở dạng 'Nhắc tôi ... sau X phút/giờ'.
    """
    if not is_admin(update.effective_user.id): return
    global waiting_for_todo
    text = update.message.text
    
    if waiting_for_todo:
        todos.append({"task": text, "done": False})
        waiting_for_todo = False
        await update.message.reply_text(f"✅ Đã thêm '{text}' vào To-Do List.")
        return

    # Basic regex for testing: "nhắc tôi [task] sau [X] phút"
    match = re.search(r'nhắc.* (.*) sau (\d+) phút', text.lower())
    if match:
        task = match.group(1)
        minutes = int(match.group(2))
        
        # Schedule the reminder
        context.job_queue.run_once(reminder_callback, minutes * 60, data={"task": task, "chat_id": update.effective_chat.id})
        await update.message.reply_text(f"✅ NLU Reminder: Đã lên lịch nhắc nhở '{task}' sau {minutes} phút nữa.")
        return
        
    # If using Gemini API, you would implement the parsing here as requested:
    """
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(...)
    """

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.data["chat_id"], text=f"⏰ *NHẮC NHỞ:* {job.data['task']}", parse_mode='Markdown')

async def todo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [
        [InlineKeyboardButton("➕ Thêm Task", callback_data="todo_add")],
        [InlineKeyboardButton("📋 Xem List", callback_data="todo_list")],
        [InlineKeyboardButton("🗑 Xóa Task Đã Xong", callback_data="todo_clear")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛠 *Quản lý To-Do List*:", reply_markup=reply_markup, parse_mode='Markdown')

async def todo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id): return
    await query.answer()
    
    global waiting_for_todo, todos
    if query.data == "todo_add":
        waiting_for_todo = True
        await query.edit_message_text("Nhập nội dung công việc bạn muốn thêm:")
    elif query.data == "todo_list":
        if not todos:
            await query.edit_message_text("🎉 To-Do List của bạn đang trống!")
            return
        
        # Build list with inline buttons to mark as done
        keyboard = []
        for idx, item in enumerate(todos):
            status = "✅" if item["done"] else "⏳"
            keyboard.append([InlineKeyboardButton(f"{status} {item['task']}", callback_data=f"todo_toggle_{idx}")])
        keyboard.append([InlineKeyboardButton("🔙 Quay lại", callback_data="todo_back")])
        await query.edit_message_text("📋 *Danh sách việc cần làm:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif query.data.startswith("todo_toggle_"):
        idx = int(query.data.split("_")[2])
        todos[idx]["done"] = not todos[idx]["done"]
        # Refresh list inline
        keyboard = []
        for i, item in enumerate(todos):
            status = "✅" if item["done"] else "⏳"
            keyboard.append([InlineKeyboardButton(f"{status} {item['task']}", callback_data=f"todo_toggle_{i}")])
        keyboard.append([InlineKeyboardButton("🔙 Quay lại", callback_data="todo_back")])
        await query.edit_message_text("📋 *Danh sách việc cần làm:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    elif query.data == "todo_clear":
        todos = [t for t in todos if not t["done"]]
        await query.edit_message_text("🧹 Đã xóa các công việc hoàn thành.")
    elif query.data == "todo_back":
        await todo_command(update, context) # Re-send menu

def setup(application):
    application.add_handler(CommandHandler("todo", todo_command))
    application.add_handler(CallbackQueryHandler(todo_callback, pattern="^todo_"))
    # Handle text messages for NLU or input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nlu_reminder))
