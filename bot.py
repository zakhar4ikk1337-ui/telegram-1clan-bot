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

waiting_promo = {}

promo_codes = {
"7days": ["AAA111","AAA112","AAA113","AAA114","AAA115","AAA116","AAA117","AAA118","AAA119","AAA120"],
"30days": ["BBB111","BBB112","BBB113","BBB114","BBB115","BBB116","BBB117","BBB118","BBB119","BBB120"]
}

used_codes = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("💰 Купить за голду", callback_data="buy")],
        [InlineKeyboardButton("🎁 Ввести промокод", callback_data="promo")]
    ]

    await update.message.reply_text(
        "👋 Добро пожаловать в клан 3TF\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


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


async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Введите промокод")


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    waiting_days.add(query.from_user.id)

    await query.message.reply_text(
        "💰 Покупка доступа\n\n"
        "Введите количество дней:\n\n"
        "7 дней — 100 голды\n"
        "30 дней — 300 голды"
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

    waiting_promo[user.id] = days

    await context.bot.send_message(
        ADMIN_ID,
        f"Игрок оплатил\nОтправьте промокод для {days} дней"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    text = update.message.text.strip()

    # админ отправляет промокод
    if user.id == ADMIN_ID and waiting_promo:

        buyer_id = list(waiting_promo.keys())[0]

        await context.bot.send_message(
            buyer_id,
            f"🎟 Ваш промокод:\n{text}"
        )

        await update.message.reply_text("Промокод отправлен")

        waiting_promo.pop(buyer_id)

        return


    # ввод игрового ID
    if user.id in waiting_for_id:

        with open(PLAYERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user.username} | {user.id} | {text}\n")

        await context.bot.send_message(
            ADMIN_ID,
            f"🎮 Новый игрок\n@{user.username}\nID: {text}"
        )

        await update.message.reply_text("ID отправлен")

        waiting_for_id.remove(user.id)

        return


    # ввод дней
    if user.id in waiting_days:

        if text not in ["7","30"]:
            await update.message.reply_text("Можно только 7 или 30 дней")
            return

        days = int(text)

        if days == 7:
            price = 100
        else:
            price = 300

        orders[user.id] = days
        waiting_days.remove(user.id)

        keyboard = [[InlineKeyboardButton("💰 Купить", callback_data="confirm")]]

        await update.message.reply_text(
            f"📅 {days} дней\n"
            f"💰 Цена: {price} голды\n\n"
            f"Нажмите кнопку чтобы оформить покупку",
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
        await update.message.reply_text("✅ Промокод активирован\n📅 7 дней в клане 3TF")
        return

    if code in promo_codes["30days"]:
        used_codes.append(code)
        await update.message.reply_text("✅ Промокод активирован\n📅 30 дней в клане 3TF")
        return

    await update.message.reply_text("❌ Промокод не правильний")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(promo, pattern="promo"))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="confirm"))
    app.add_handler(CallbackQueryHandler(paid, pattern="paid"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()

