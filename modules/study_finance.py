import logging
import re
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from config import is_admin

logger = logging.getLogger(__name__)

# --- Quản lý chi tiêu ---
async def expense_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    text = update.message.text.lower()
    
    # Cú pháp: [mục đích] [số tiền]k
    # VD: ăn trưa 45k
    match = re.search(r'(.+) (\d+)k$', text)
    if match:
        item = match.group(1).strip()
        amount = int(match.group(2)) * 1000
        
        # Ở đây bạn có thể gọi API của gspread để ghi vào Google Sheets
        # Ví dụ:
        # sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), item, amount])
        
        await update.message.reply_text(f"💰 Đã ghi nhận chi tiêu: {item.capitalize()} - {amount:,} VNĐ")
        return

# --- Học tập (Flashcards) ---
# Danh sách câu hỏi mẫu
flashcards = [
    {"question": "Đâu là framework web phổ biến nhất cho Python?", "options": ["Django", "Flask", "FastAPI", "Tất cả đều đúng"], "correct": 3},
    {"question": "HTTP Status 404 nghĩa là gì?", "options": ["OK", "Not Found", "Server Error", "Bad Request"], "correct": 1}
]
current_card = 0

async def send_flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    global current_card
    if current_card >= len(flashcards):
        current_card = 0 # reset
        
    card = flashcards[current_card]
    
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=card["question"],
        options=card["options"],
        type='quiz',
        correct_option_id=card["correct"],
        is_anonymous=False
    )
    current_card += 1

def setup(application):
    application.add_handler(CommandHandler("flashcard", send_flashcard))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, expense_tracker), group=2)
