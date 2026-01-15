from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

from config import *
from database import cur, conn
from utils import normalize_number, detect_country

# -------- Force Join --------
async def check_join(update, context):
    try:
        member = await context.bot.get_chat_member(
            FORCE_JOIN_CHANNEL, update.effective_user.id
        )
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# -------- Start --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()

    if not await check_join(update, context):
        btn = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{FORCE_JOIN_CHANNEL.replace('@','')}")]]
        await update.message.reply_text(
            "⚠️ You must join our channel first",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    if uid not in ADMIN_IDS:
        await user_menu(update)
    else:
        await admin_menu(update)

# -------- User Menu --------
async def user_menu(update):
    buttons = [
        [InlineKeyboardButton("📱 Get Number", callback_data="get_number")],
        [InlineKeyboardButton("🔁 Change Number", callback_data="change_number")],
        [InlineKeyboardButton("🔐 OTP Group", callback_data="otp_group")],
        [InlineKeyboardButton("🧩 Services", callback_data="services")]
    ]
    await update.message.reply_text(
        "Main Menu",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------- Admin Menu --------
async def admin_menu(update):
    buttons = [
        [InlineKeyboardButton("👤 User Management", callback_data="user_mgmt")],
        [InlineKeyboardButton("📂 Upload Number File", callback_data="upload_file")],
        [InlineKeyboardButton("📊 Number Stats", callback_data="stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
    ]
    await update.message.reply_text(
        "Admin Panel",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------- Get Number --------
async def callbacks(update: Update, context):
    q = update.callback_query
    await q.answer()

    if q.data == "get_number":
        cur.execute("SELECT number FROM numbers LIMIT 1")
        row = cur.fetchone()

        if not row:
            await q.message.reply_text("❌ No numbers available")
            return

        num = row[0]
        country = detect_country(num)

        buttons = [
            [InlineKeyboardButton("🔐 OTP Group", url="https://t.me/Rambo_otp_hub")],
            [InlineKeyboardButton("🔁 Change Number", callback_data="change_number")]
        ]

        await q.message.reply_text(
            f"📱 +{num}\n🌍 {country}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif q.data == "upload_file":
        await q.message.reply_text("Send number file (.txt)")

# -------- File Upload (Admin) --------
async def file_handler(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        return

    file = await update.message.document.get_file()
    content = (await file.download_as_bytearray()).decode()

    count = 0
    for line in content.splitlines():
        num = normalize_number(line)
        if num.isdigit():
            cur.execute("INSERT INTO numbers VALUES (?)", (num,))
            count += 1

    conn.commit()

    await update.message.reply_text(
        f"✅ {count} numbers added successfully"
    )

# -------- App --------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callbacks))
app.add_handler(MessageHandler(filters.Document.ALL, file_handler))

app.run_polling()
