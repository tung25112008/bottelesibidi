import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, ADMIN_ID

# Import modules
from modules import task_manager, server_monitor, notification_hub, utilities, study_finance

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Xin lỗi, bot này chỉ phục vụ chủ nhân của nó.")
        return

    welcome_msg = (
        "🤖 *Xin chào! Tôi là Sibidi, trợ lý ảo cá nhân của bạn.*\n\n"
        "Tôi được trang bị các chức năng sau:\n"
        "1️⃣ *Quản lý công việc*: Dùng NLU để đặt lịch nhắc nhở hoặc `/todo` để quản lý việc cần làm.\n"
        "2️⃣ *Giám sát Server*: Dùng `/server` để xem tình trạng hệ thống.\n"
        "3️⃣ *Tiện ích*: Gửi link video để tải, gửi ảnh để convert, gửi JSON để format.\n"
        "4️⃣ *Học tập & Chi tiêu*: Gửi chi tiêu dạng 'ăn trưa 45k' để lưu Google Sheets, `/flashcard` để ôn bài.\n\n"
        "Hãy nhập một lệnh hoặc gửi tin nhắn để tôi hỗ trợ bạn!"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

def main():
    if not TELEGRAM_TOKEN:
        logger.error("Chưa cấu hình TELEGRAM_TOKEN trong .env!")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Core handlers
    application.add_handler(CommandHandler("start", start))

    # Setup module handlers
    task_manager.setup(application)
    server_monitor.setup(application)
    notification_hub.setup(application)
    utilities.setup(application)
    study_finance.setup(application)

    # Run the bot until the user presses Ctrl-C
    logger.info("Sibidi Bot đang chạy...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
