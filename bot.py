
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

waiting_for_id = set()
cooldown = {}

PLAYERS_FILE = "players.txt"

waiting_days = set()
orders = {}
waiting_payment = {}

promo_codes = {
"7days": ["AAA111","AAA112","AAA113","AAA114","AAA115","AAA116","AAA117","AAA118","AAA119","AAA120"],
"30days": ["BBB111","BBB112","BBB113","BBB114","BBB115","BBB116","BBB117","BBB118","BBB119","BBB120"]
}

used_codes = []

# START

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("🎁 Ввести промокод", callback_data="promo")],
        [InlineKeyboardButton("💰 Купить за голду", callback_data="buy")]
    ]

    await update.message.reply_text(
        "👋 Добро пожаловать в клан 3TF",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ЗАЯВКА

async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    now = time.time()

    if user.id in cooldown and now - cooldown[user.id] < 300:
        await query.message.reply_text("⏳ Подождите 5 минут")
        return

    cooldown[user.id] = now

    await query.message.reply_text(
        "Отправьте:\n\n"
        "1️⃣ Скрин профиля\n"
        "2️⃣ Видео катки"
    )


# МЕДИА

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    # если админ отправляет скрин — это скрин оплаты
    if user.id == ADMIN_ID:

        if not waiting_payment:
            return

        buyer_id = list(waiting_payment.keys())[0]

        await context.bot.forward_message(
            buyer_id,
            update.message.chat_id,
            update.message.message_id
        )

        keyboard = [[InlineKeyboardButton("✅ Оплатил", callback_data="paid")]]

        await context.bot.send_message(
            buyer_id,
            "📸 Скрин оплаты\n\nНажмите кнопку после оплаты",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # иначе это заявка игрока

    await context.bot.forward_message(
        ADMIN_ID,
        update.message.chat_id,
        update.message.message_id
    )

    keyboard = [[
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user.id}"),
        InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{user.id}")
    ]]

    await context.bot.send_message(
        ADMIN_ID,
        f"📨 Новая заявка\n\n@{user.username}\n{user.id}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# РЕШЕНИЕ

async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if "accept_" in data:

        user_id = int(data.split("_")[1])
        waiting_for_id.add(user_id)

        await context.bot.send_message(
            user_id,
            "✅ Вы приняты\n\nНапишите игровой ID"
        )

        await query.edit_message_text("Игрок принят")

    if "reject_" in data:

        user_id = int(data.split("_")[1])

        keyboard = [[InlineKeyboardButton(
            "Связаться с админом",
            url=f"https://t.me/{ADMIN_USERNAME}"
        )]]

        await context.bot.send_message(
            user_id,
            "❌ Заявка отклонена",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await query.edit_message_text("Игрок отклонён")


# ПОЛУЧЕНИЕ ID

async def get_player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id in waiting_for_id:

        player_id = update.message.text

        with open(PLAYERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user.username} | {user.id} | {player_id}\n")

        await context.bot.send_message(
            ADMIN_ID,
            f"🎮 Новый игрок\n@{user.username}\nID: {player_id}"
        )

        await update.message.reply_text("✅ ID отправлен")

        waiting_for_id.remove(user.id)
        return


# ПРОМОКОД

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text("🎁 Введите промокод")


async def check_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    code = update.message.text.strip()

    if code in used_codes:
        await update.message.reply_text("⚠️ Промокод уже использован")
        return

    if code in promo_codes["7days"]:

        used_codes.append(code)

        await update.message.reply_text(
            "✅ Промокод активирован\n📅 Доступ на 7 дней"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"🎁 Использован промокод {code} (7 дней)"
        )

        return

    if code in promo_codes["30days"]:

        used_codes.append(code)

        await update.message.reply_text(
            "✅ Промокод активирован\n📅 Доступ на 30 дней"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"🎁 Использован промокод {code} (30 дней)"
        )

        return

    await update.message.reply_text("❌ Неверный промокод")


# ПОКУПКА

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    waiting_days.add(query.from_user.id)

    await query.message.reply_text("Введите количество дней: 7 или 30")


async def days(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id not in waiting_days:
        return

    text = update.message.text

    if text not in ["7","30"]:
        await update.message.reply_text("Можно только 7 или 30")
        return

    days = int(text)
    price = 100 if days == 7 else 300

    orders[user.id] = days
    waiting_days.remove(user.id)

    keyboard = [[InlineKeyboardButton("Купить", callback_data="confirm")]]

    await update.message.reply_text(
        f"{days} дней = {price} голды",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    days = orders[user.id]

    waiting_payment[user.id] = days

    await context.bot.send_message(
        ADMIN_ID,
        f"🛒 Новый заказ\n@{user.username}\n{days} дней"
    )

    await query.message.reply_text("Ожидайте скрин оплаты")


async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    days = waiting_payment[user.id]

    await context.bot.send_message(
        ADMIN_ID,
        f"💰 Игрок @{user.username} оплатил\nЖдёт промокод на {days} дней"
    )


# MAIN

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("players", players))

    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(decision, pattern="accept_|reject_"))

    app.add_handler(CallbackQueryHandler(promo, pattern="promo"))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="confirm"))
    app.add_handler(CallbackQueryHandler(paid, pattern="paid"))

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, days))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_promo))

    app.run_polling()


if __name__ == "__main__":
    main()

