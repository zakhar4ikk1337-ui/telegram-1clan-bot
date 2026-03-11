import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300
ADMIN_USERNAME = "Kroniq_Pensia"

logging.basicConfig(level=logging.INFO)

orders = {}
waiting_days = set()
waiting_id = set()
waiting_promo_input = set()

promo_codes = {
    "7": ["AAA111","AAA112"],
    "30": ["BBB111","BBB112"]
}

used_codes = []

applications = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("💰 Купить за голду", callback_data="buy")],
        [InlineKeyboardButton("🎁 Ввести промокод", callback_data="promo")]
    ]

    await update.message.reply_text(
        "Добро пожаловать в клан 3TF",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if query.data == "apply":

        applications.add(user)
        await query.message.reply_text("Отправьте скрин или видео катки")


    if query.data == "buy":

        waiting_days.add(user)

        await query.message.reply_text(
            "Введите количество дней\n\n"
            "7 дней — 100 голды\n"
            "30 дней — 300 голды"
        )


    if query.data == "promo":

        waiting_promo_input.add(user)

        await query.message.reply_text("Введите промокод")


    if query.data == "confirm":

        order = orders[user]

        username = f"@{query.from_user.username}" if query.from_user.username else user

        await context.bot.send_message(
            ADMIN_ID,
            f"🛒 Новый заказ\n"
            f"👤 {username}\n"
            f"🎮 ID: {order['game_id']}\n"
            f"📅 {order['days']} дней\n\n"
            f"Отправьте скрин оплаты"
        )

        await query.message.reply_text("⏳ Ожидайте скрин оплаты")


    if query.data == "paid":

        username = f"@{query.from_user.username}" if query.from_user.username else user

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Покупатель оплатил\n"
            f"{username}\n\n"
            f"Отправьте промокод"
        )

        await query.message.reply_text("⏳ Ожидайте промокод")


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id
    text = update.message.text.strip()

    if user == ADMIN_ID and context.user_data.get("promo_user"):

        buyer = context.user_data["promo_user"]

        await context.bot.send_message(
            buyer,
            f"🎟 Ваш промокод:\n{text}"
        )

        context.user_data["promo_user"] = None

        await update.message.reply_text("Промокод отправлен")
        return


    if user in waiting_days:

        if text not in ["7","30"]:
            await update.message.reply_text("Введите 7 или 30")
            return

        orders[user] = {"days": text}

        waiting_days.remove(user)
        waiting_id.add(user)

        await update.message.reply_text("Введите игровой ID")
        return


    if user in waiting_id:

        orders[user]["game_id"] = text

        waiting_id.remove(user)

        keyboard = [[InlineKeyboardButton("💰 Купить", callback_data="confirm")]]

        await update.message.reply_text(
            "Нажмите кнопку для оформления",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return


    if user in waiting_promo_input:

        waiting_promo_input.remove(user)

        code = text.upper()

        if code in used_codes:

            await update.message.reply_text("❌ Промокод уже использован")
            return


        if code in promo_codes["7"]:

            used_codes.append(code)

            await update.message.reply_text("✅ Промокод активирован\n7 дней в клане")

            return


        if code in promo_codes["30"]:

            used_codes.append(code)

            await update.message.reply_text("✅ Промокод активирован\n30 дней в клане")

            return


        await update.message.reply_text("❌ Неверный промокод")


async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user in applications:

        username = f"@{update.message.from_user.username}" if update.message.from_user.username else user

        if update.message.photo:

            await context.bot.send_photo(
                ADMIN_ID,
                update.message.photo[-1].file_id,
                caption=f"📨 Заявка\n{username}"
            )

        elif update.message.video:

            await context.bot.send_video(
                ADMIN_ID,
                update.message.video.file_id,
                caption=f"📨 Заявка\n{username}"
            )

        await update.message.reply_text("Заявка отправлена")

        applications.remove(user)

        return


    if user == ADMIN_ID:

        photo = update.message.photo[-1].file_id

        buyer = None

        for u in orders:
            buyer = u
            break

        if not buyer:
            return

        keyboard = [[InlineKeyboardButton("✅ Купил", callback_data="paid")]]

        await context.bot.send_photo(
            buyer,
            photo,
            caption="Оплатите и нажмите кнопку",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        context.user_data["promo_user"] = buyer

        await update.message.reply_text("Скрин отправлен")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))

    app.run_polling()


if __name__ == "__main__":
    main()
