import logging
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300
ADMIN_USERNAME = "Kroniq_Pensia"

logging.basicConfig(level=logging.INFO)

# заявки
waiting_application = set()

# покупка
waiting_days = set()
waiting_game_id = set()

orders = {}
game_ids = {}

waiting_screenshot_user = None
waiting_confirm_user = None
waiting_promo_user = None

promo_codes = {
    "7days": ["AAA111","AAA112","AAA113","AAA114","AAA115"],
    "30days": ["BBB111","BBB112","BBB113","BBB114","BBB115"]
}

used_codes = []

cooldown = {}

applications = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("💰 Купить за голду", callback_data="buy")],
        [InlineKeyboardButton("🎁 Ввести промокод", callback_data="promo")]
    ]

    await update.message.reply_text(
        f"👋 Добро пожаловать в клан 3TF\n\nАдмин: @{ADMIN_USERNAME}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    waiting_application.add(user.id)

    await query.message.reply_text(
        "📨 Отправьте:\n\n"
        "1️⃣ Скрин профиля\n"
        "2️⃣ Видео катки"
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    waiting_days.add(query.from_user.id)

    await query.message.reply_text(
        "💰 Покупка доступа\n\n"
        "Введите количество дней\n\n"
        "7 дней — 100 голды\n"
        "30 дней — 300 голды"
    )


async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Введите промокод")


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_screenshot_user

    query = update.callback_query
    await query.answer()

    user = query.from_user

    waiting_screenshot_user = user.id

    username = f"@{user.username}" if user.username else f"ID:{user.id}"

    await context.bot.send_message(
        ADMIN_ID,
        f"🛒 Новый заказ\n"
        f"👤 {username}\n"
        f"🎮 ID: {game_ids[user.id]}\n"
        f"📅 {orders[user.id]} дней\n\n"
        f"Отправьте скрин оплаты"
    )

    await query.message.reply_text("⏳ Ожидайте скрин оплаты")


async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_confirm_user, waiting_promo_user

    query = update.callback_query
    await query.answer()

    waiting_promo_user = waiting_confirm_user

    await context.bot.send_message(
        ADMIN_ID,
        "💰 Игрок оплатил\nОтправьте промокод"
    )

    await query.message.reply_text("⏳ Ожидайте промокод")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_promo_user

    user = update.message.from_user
    text = update.message.text.strip()

    # админ отправляет промокод
    if user.id == ADMIN_ID and waiting_promo_user:

        await context.bot.send_message(
            waiting_promo_user,
            f"🎟 Ваш промокод:\n{text}"
        )

        await update.message.reply_text("Промокод отправлен")

        waiting_promo_user = None
        return

    # выбор дней
    if user.id in waiting_days:

        if text not in ["7","30"]:
            await update.message.reply_text("Можно только 7 или 30")
            return

        orders[user.id] = int(text)

        waiting_days.remove(user.id)
        waiting_game_id.add(user.id)

        await update.message.reply_text("🎮 Введите ваш игровой ID")
        return

    # ввод игрового ID
    if user.id in waiting_game_id:

        game_ids[user.id] = text
        waiting_game_id.remove(user.id)

        keyboard = [[InlineKeyboardButton("💰 Купить", callback_data="confirm")]]

        await update.message.reply_text(
            "Нажмите кнопку чтобы оформить покупку",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # проверка промокода
    code = text.upper()

    if code in used_codes:
        await update.message.reply_text("❌ Промокод уже использован")
        return

    if code in promo_codes["7days"]:
        used_codes.append(code)
        await update.message.reply_text("✅ Промокод активирован\n7 дней в клане")
        return

    if code in promo_codes["30days"]:
        used_codes.append(code)
        await update.message.reply_text("✅ Промокод активирован\n30 дней в клане")
        return

    await update.message.reply_text("❌ Промокод не правильний")


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id not in waiting_application:
        return

    username = f"@{user.username}" if user.username else f"ID:{user.id}"

    keyboard = [
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")
        ]
    ]

    if update.message.photo:

        photo = update.message.photo[-1].file_id

        await context.bot.send_photo(
            ADMIN_ID,
            photo,
            caption=f"📨 Новая заявка\n{username}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif update.message.video:

        video = update.message.video.file_id

        await context.bot.send_video(
            ADMIN_ID,
            video,
            caption=f"📨 Новая заявка\n{username}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    await update.message.reply_text("✅ Заявка отправлена")

    waiting_application.remove(user.id)


async def application_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = int(data.split("_")[1])

    if data.startswith("accept"):

        await context.bot.send_message(
            user_id,
            "✅ Ваш запрос приняли\nСкоро вам придет запрос в клан 3TF"
        )

        await query.edit_message_caption("✅ Заявка принята")

    else:

        await context.bot.send_message(
            user_id,
            "❌ Ваш запрос отклонён"
        )

        await query.edit_message_caption("❌ Заявка отклонена")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_screenshot_user, waiting_confirm_user

    user = update.message.from_user

    if user.id != ADMIN_ID:
        return

    if not waiting_screenshot_user:
        return

    photo = update.message.photo[-1].file_id

    keyboard = [[InlineKeyboardButton("✅ Я оплатил", callback_data="paid")]]

    await context.bot.send_photo(
        waiting_screenshot_user,
        photo,
        caption="💰 Оплатите по этому скрину и нажмите кнопку после оплаты",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    waiting_confirm_user = waiting_screenshot_user
    waiting_screenshot_user = None

    await update.message.reply_text("Скрин отправлен покупателю")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(promo, pattern="promo"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="confirm"))
    app.add_handler(CallbackQueryHandler(paid, pattern="paid"))

    app.add_handler(CallbackQueryHandler(application_decision, pattern="accept_"))
    app.add_handler(CallbackQueryHandler(application_decision, pattern="reject_"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()


if __name__ == "__main__":
    main()
