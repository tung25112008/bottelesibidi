# 🤖 Sibidi Telegram Bot

Sibidi là một trợ lý ảo cá nhân đa năng trên nền tảng Telegram, được viết bằng Python. Bot được thiết kế theo cấu trúc module gọn gàng, tích hợp nhiều tiện ích từ quản lý công việc, giám sát máy chủ đến hỗ trợ AI trực tiếp.

## 🌟 Chức năng nổi bật

1. **✅ Quản lý công việc (Task Manager)**
   - Hẹn giờ thông minh (NLU): Bot tự hiểu các câu lệnh như *"nhắc tôi uống thuốc sau 5 phút"*.
   - Quản lý To-do List: Giao diện tương tác bằng nút bấm nội tuyến (Inline Keyboard) để thêm, sửa, xóa việc cần làm.

2. **🖥️ Giám sát Hệ thống (Server Monitor)**
   - Lấy thông tin tài nguyên hệ thống từ xa (CPU, RAM, Disk usage) trực tiếp qua khung chat Telegram bằng thư viện `psutil`.

3. **🐙 Trung tâm Thông báo (Notification Hub)**
   - **Đọc báo RSS:** Tự động quét và gửi tin tức công nghệ mới nhất mỗi 30 phút.
   - **Săn lùng Github Repo:** Lên lịch tự động tìm kiếm các repository xu hướng trên Github (Python, AI, Machine Learning,...). **Đặc biệt:** Tích hợp AI (Gemini 2.5 Flash) để tự động dịch mô tả repo sang tiếng Việt và đưa ra đánh giá, phân tích nhanh về tính ứng dụng của Repo đó.

4. **🛠️ Tiện ích Tốc hành (Utilities)**
   - Tự động tải video chất lượng cao từ các link YouTube, TikTok qua `yt-dlp`.
   - Chỉnh lề, làm đẹp văn bản JSON lộn xộn.
   - Mã hóa và giải mã chuỗi Base64 cực kỳ nhanh chóng.

5. **📚 Học tập & Tài chính (Study & Finance)**
   - Ghi chú nhanh chi tiêu cá nhân bằng cú pháp rút gọn (VD: *ăn trưa 45k*).
   - Ôn tập kiến thức bằng tính năng `/flashcard` thông qua định dạng Telegram Quiz Poll.

## 🚀 Hướng dẫn cài đặt

**Bước 1: Tải mã nguồn**
```bash
git clone https://github.com/tung25112008/bottelesibidi.git
cd bottelesibidi
```

**Bước 2: Cài đặt thư viện**
Bạn cần sử dụng Python 3.9 trở lên.
```bash
pip install -r requirements.txt
```

**Bước 3: Cấu hình hệ thống**
1. Đổi tên file `.env.example` thành `.env` (hoặc tạo file `.env` mới).
2. Điền các thông số vào file `.env`:
```env
TELEGRAM_TOKEN=token_bot_cua_ban_tu_botfather
ADMIN_ID=id_telegram_cua_ban
GEMINI_API_KEY=api_key_cua_google_gemini
```
*Lưu ý: Bạn bắt buộc phải cấu hình `ADMIN_ID` để bot chỉ nhận lệnh từ một mình bạn, ngăn người lạ sử dụng và đảm bảo tính bảo mật cá nhân.*

**Bước 4: Khởi chạy Bot**
```bash
python main.py
```

## 🧠 Công nghệ sử dụng
- [python-telegram-bot](https://python-telegram-bot.org/) (Asyncio)
- [Google GenAI SDK](https://ai.google.dev/) (Tích hợp Gemini 2.5)
- `psutil`, `httpx`, `yt-dlp`, `feedparser`
