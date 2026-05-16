import logging
import feedparser
import httpx
import datetime
from telegram.ext import ContextTypes
from config import ADMIN_ID, GEMINI_API_KEY
from google import genai

logger = logging.getLogger(__name__)

# Danh sách các RSS feeds để theo dõi
RSS_FEEDS = [
    {"name": "Tin học (VnExpress)", "url": "https://vnexpress.net/rss/so-hoa.rss", "last_link": None}
]

# Lưu ID các repo Github đã thông báo để tránh gửi lại
SEEN_REPOS = set()

async def check_rss_feeds(context: ContextTypes.DEFAULT_TYPE):
    """Kiểm tra RSS feed định kỳ"""
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            if parsed.entries:
                latest = parsed.entries[0]
                if feed["last_link"] != latest.link:
                    feed["last_link"] = latest.link
                    msg = f"📰 *{feed['name']}*\n[{latest.title}]({latest.link})"
                    await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error checking RSS {feed['name']}: {e}")

async def analyze_repo_with_gemini(repo_name, repo_desc):
    if not GEMINI_API_KEY:
        return f"(Chưa có Gemini API Key để phân tích)\n{repo_desc}"
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"Dịch mô tả repository '{repo_name}' sau sang tiếng Việt và phân tích ngắn gọn (khoảng 2-3 câu) xem repo này dùng để làm gì, tính ứng dụng của nó:\n\nMô tả gốc: {repo_desc}"
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"(Lỗi khi gọi AI phân tích)\n{repo_desc}"

async def check_github_repos(context: ContextTypes.DEFAULT_TYPE):
    """Tìm kiếm repo mới và nổi bật trên Github về các skill cụ thể"""
    # Bạn có thể thay đổi danh sách các skill/công nghệ muốn theo dõi tại đây
    skills = ["python", "ai", "machine-learning"] 
    
    # Tìm các repo được tạo trong vòng 7 ngày qua
    date_since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    
    for skill in skills:
        query = f"topic:{skill} created:>{date_since}"
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
        
        try:
            # Dùng httpx (được cài sẵn theo python-telegram-bot) để gửi request bất đồng bộ
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers={"Accept": "application/vnd.github.v3+json"})
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    if items:
                        # Chỉ lấy repo đứng top 1 của mỗi skill để tránh spam
                        top_repo = items[0] 
                        repo_id = top_repo["id"]
                        
                        if repo_id not in SEEN_REPOS:
                            SEEN_REPOS.add(repo_id)
                            
                            original_desc = top_repo['description'] or 'Không có thông tin mô tả.'
                            analysis = await analyze_repo_with_gemini(top_repo['full_name'], original_desc)
                            
                            msg = (
                                f"🐙 *Top Repo Github Mới ({skill.capitalize()})*\n"
                                f"📦 Tên: [{top_repo['full_name']}]({top_repo['html_url']})\n"
                                f"⭐ Stars: {top_repo['stargazers_count']}\n\n"
                                f"💡 *AI Phân tích:*\n{analysis}"
                            )
                            await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Error checking Github for {skill}: {e}")

def setup(application):
    # Lên lịch chạy job kiểm tra RSS mỗi 30 phút (1800 giây)
    application.job_queue.run_repeating(check_rss_feeds, interval=600, first=10)
    
    # Lên lịch chạy job kiểm tra Github mỗi 12 tiếng (43200 giây)
    application.job_queue.run_repeating(check_github_repos, interval=3600, first=20)
