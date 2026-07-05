import json
import os
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required. Set it in your .env file.")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]
DB_PATH = os.path.join(os.path.dirname(__file__), "premium_users.json")
BOOKS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "books.json")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://your-app.pages.dev")
KBZ_PAY_QR_URL = os.environ.get("KBZ_PAY_QR_URL", "")
KBZ_PAY_PHONE = os.environ.get("KBZ_PAY_PHONE", "")

PREMIUM_MONTHLY_MMK = 3000
PREMIUM_LIFETIME_MMK = 15000


def load_premium_users():
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_premium_users(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_books():
    try:
        with open(BOOKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def is_premium(telegram_id):
    users = load_premium_users()
    for u in users:
        if u["telegramId"] == telegram_id:
            until = datetime.fromisoformat(u["premiumUntil"])
            if until > datetime.now():
                return True
    return False


def add_premium(telegram_id, plan="monthly"):
    users = load_premium_users()
    now = datetime.now()
    if plan == "lifetime":
        until = now + timedelta(days=36500)
    else:
        until = now + timedelta(days=30)

    for u in users:
        if u["telegramId"] == telegram_id:
            current_until = datetime.fromisoformat(u["premiumUntil"])
            if current_until > now:
                u["premiumUntil"] = (current_until + timedelta(days=30 if plan == "monthly" else 36500)).isoformat()
            else:
                u["premiumUntil"] = until.isoformat()
            u["plan"] = plan
            save_premium_users(users)
            return u["premiumUntil"]

    entry = {
        "telegramId": telegram_id,
        "premiumUntil": until.isoformat(),
        "plan": plan
    }
    users.append(entry)
    save_premium_users(users)
    return entry["premiumUntil"]


def build_search_results(books, query, limit=5):
    q = query.lower()
    matches = []
    for b in books:
        if q in b["title"].lower() or q in b["author"].lower():
            matches.append(b)
        if len(matches) >= limit:
            break
    return matches


def format_book_list(books, user_is_premium):
    lines = []
    for b in books:
        lang_flag = "🇲🇲" if b["lang"] == "ဗမာ" else "🇬🇧"
        premium_marker = " ⭐" if b["premium"] else ""
        lines.append(f"{b['cover']} <b>{b['title']}</b> — {b['author']}")
        lines.append(f"   {lang_flag} {b['lang']} | {b['genre']}{premium_marker}")
        lines.append("")
    return lines


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = (
        f"မင်္ဂလာပါ {user.first_name}! 👋\n\n"
        f"<b>စာအုပ်စင် BookShelf</b> မှ ကြိုဆိုပါတယ်။\n\n"
        f"📚 မြန်မာနဲ့ အင်္ဂလိပ် စာအုပ်တွေကို အခမဲ့ download လုပ်နိုင်ပါတယ်။\n"
        f"⭐ Premium member ဆိုရင် နောက်ထပ် စာအုပ်အများကြီး ထပ်ရပါမယ်။\n\n"
        f"အောက်က ခလုတ်ကိုနှိပ်ပြီး စာအုပ်စင်ကို ဝင်ကြည့်လိုက်ပါ။"
    )
    keyboard = [[InlineKeyboardButton("📚 Browse Books", web_app={"url": MINI_APP_URL})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(welcome, reply_markup=reply_markup)


async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⭐ <b>Premium Membership</b>\n\n"
        f"💰 Monthly: <b>{PREMIUM_MONTHLY_MMK} MMK</b> / month\n"
        f"💎 Lifetime: <b>{PREMIUM_LIFETIME_MMK} MMK</b> (one time)\n\n"
        "<b>Premium member ဖြစ်ရင် ဘာတွေရမလဲ?</b>\n"
        "• Premium သီးသန့်စာအုပ်များ download လုပ်ခွင့်\n"
        "• ကြော်ငြာမပါဝင်\n"
        "• စာအုပ်အသစ်များကို ၃ ရက်စောပြီး download လုပ်ခွင့်\n"
        "• တစ်နေ့ download အကန့်အသတ်မရှိ\n\n"
        "<b>ငွေပေးချေနည်း</b>\n"
    )

    if KBZ_PAY_QR_URL:
        text += (
            f"📱 <b>KBZ Pay</b>\n"
            f"ဖုန်းနံပါတ်: <code>{KBZ_PAY_PHONE}</code>\n"
            f"ငွေလွှဲပြီးရင် Screenshot ကို ဒီ bot ဆီ ပို့ပေးပါ။\n\n"
        )

    text += (
        "⭐ <b>Telegram Stars</b>\n"
        "Coming soon — Telegram Stars နဲ့ တိုက်ရိုက်ငွေပေးချေနိုင်မယ့် စနစ်။\n\n"
        "မေးခွန်းများရှိပါက admin ကို ဆက်သွယ်ပါ။"
    )
    await update.message.reply_html(text)


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only command.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_html(
            "Usage: /verify <telegram_id> <plan>\n"
            "Plan: <code>monthly</code> or <code>lifetime</code>"
        )
        return

    target_id = int(context.args[0])
    plan = context.args[1].lower()

    if plan not in ("monthly", "lifetime"):
        await update.message.reply_text("Plan must be 'monthly' or 'lifetime'.")
        return

    until = add_premium(target_id, plan)
    await update.message.reply_html(
        f"✅ User <code>{target_id}</code> is now premium ({plan}) until <code>{until}</code>."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_premium(user_id):
        users = load_premium_users()
        user_data = next((u for u in users if u["telegramId"] == user_id), None)
        until = datetime.fromisoformat(user_data["premiumUntil"])
        await update.message.reply_html(
            f"⭐ <b>You are a Premium member!</b>\n"
            f"Plan: {user_data['plan']}\n"
            f"Valid until: <code>{until.strftime('%Y-%m-%d')}</code>\n"
            f"Days remaining: <b>{(until - datetime.now()).days}</b>"
        )
    else:
        await update.message.reply_html(
            "သင်က Premium member မဟုတ်သေးပါ။\n\n"
            "Premium ဝယ်ယူရန် /premium ကိုနှိပ်ပါ။"
        )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_html(
            "<b>🔍 Search Books</b>\n\n"
            "ရှာချင်တဲ့ စာအုပ်အမည် (သို့) စာရေးဆရာအမည်ကို ရိုက်ထည့်ပါ။\n\n"
            "Search by title or author name.\n\n"
            "Example:\n"
            "<code>/search gatsby</code>\n"
            "<code>/search သန်းထွန်း</code>"
        )
        return

    query = " ".join(context.args)
    books = load_books()
    results = build_search_results(books, query, limit=5)

    if not results:
        keyboard = [[InlineKeyboardButton("📚 Browse All Books", web_app={"url": MINI_APP_URL})]]
        await update.message.reply_html(
            f"🔍 <b>Search: {query}</b>\n\n"
            "စာအုပ်မတွေ့ပါ။ နောက်တစ်ခု ထပ်ရှာကြည့်ပါ။\n\n"
            "No books found. Try a different search.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    lines = [f"🔍 <b>Search: {query}</b>\n"]
    lines.extend(format_book_list(results, False))

    keyboard = [[InlineKeyboardButton("📚 Browse All Books", web_app={"url": MINI_APP_URL})]]
    await update.message.reply_html(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def genres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = load_books()
    genre_counts = {}
    for b in books:
        g = b["genre"]
        genre_counts[g] = genre_counts.get(g, 0) + 1

    sorted_genres = sorted(genre_counts.items())

    lines = ["📂 <b>Genres</b>\n"]
    for genre, count in sorted_genres:
        lines.append(f"• {genre} ({count} books)")

    keyboard = [[InlineKeyboardButton("📚 Browse by Genre", web_app={"url": MINI_APP_URL})]]
    await update.message.reply_html("\n".join(lines), reply_markup=InlineKeyboardMarkup(keyboard))


async def new_arrivals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = load_books()
    now = datetime.now()
    new_books = []
    for b in books:
        added = datetime.fromisoformat(b["addedAt"])
        if (now - added).days <= 7:
            new_books.append(b)

    if not new_books:
        await update.message.reply_html(
            "📦 <b>New Arrivals</b>\n\n"
            "ဒီတစ်ပတ်အတွင်း စာအုပ်အသစ်များ မရှိသေးပါ။\n"
            "No new arrivals this week. Check back soon!"
        )
        return

    lines = [f"📦 <b>New Arrivals ({len(new_books)} books)</b>\n"]
    lines.extend(format_book_list(new_books, False))

    keyboard = [[InlineKeyboardButton("📚 Browse All", web_app={"url": MINI_APP_URL})]]
    await update.message.reply_html("\n".join(lines), reply_markup=InlineKeyboardMarkup(keyboard))


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>📚 BookShelf Commands</b>\n\n"
        "/start — စတင်ရန် & Mini App ဖွင့်ရန်\n"
        "/search — စာအုပ်ရှာရန် (title or author)\n"
        "/genres — အမျိုးအစားများ ကြည့်ရန်\n"
        "/new — ဒီတစ်ပတ် စာအုပ်အသစ်များ\n"
        "/premium — Premium ဝယ်ယူနည်း\n"
        "/status — သင့် Premium အခြေအနေကြည့်ရန်\n"
        "/help — ဒီစာကိုပြန်ကြည့်ရန်"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("verify", verify))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("genres", genres))
    app.add_handler(CommandHandler("new", new_arrivals))
    app.add_handler(CommandHandler("help", help_cmd))

    logger.info("BookShelf Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
