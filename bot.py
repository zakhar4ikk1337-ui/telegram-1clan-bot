import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300
ADMIN_USERNAME = "Kroniq_Pensia"

logging.basicConfig(level=logging.INFO)

waiting_screenshot = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку в клан 3TF", callback_data="apply")],
        [InlineKeyboardButton("💰 Покупка в голде", callback_data="buy")]
    ]

    await update.message.reply_text(
        "Добро пожаловать в клан 3TF",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]

    await query.message.reply_text(
        "Отправьте:\n\n"
        "1️⃣ Скрин профиля с временем\n"
        "2️⃣ Видео 1 катки Закладка бомби (ЗБ)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("100 голды (7 дней)", callback_data="buy7")],
        [InlineKeyboardButton("200 голды (30 дней)", callback_data="buy30")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ]

    await query.message.reply_text(
        "🔥 Акция\n\nВыберите тариф:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == "buy7":
        text = "100 голды / 7 дней"
    else:
        text = "200 голды / 30 дней"

    keyboard = [[
        InlineKeyboardButton("✅ Принять заказ", callback_data=f"order_accept_{user.id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"order_reject_{user.id}")
    ]]

    await context.bot.send_message(
        ADMIN_ID,
        f"Новая покупка\n\nПользователь: @{user.username}\nID: {user.id}\nТариф: {text}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.message.reply_text("⏳ Ожидание принятия заказа администратором")

async def order_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if "order_accept_" in data:

        user_id = int(data.split("_")[2])

        waiting_screenshot[query.from_user.id] = user_id

        await context.bot.send_message(
            ADMIN_ID,
            "Отправьте скрин покупки для пользователя"
        )

        await context.bot.send_message(
            user_id,
            "Администратор принял заказ. Ожидайте скрин покупки."
        )

        await query.edit_message_text("Заказ принят")

    if "order_reject_" in data:

        user_id = int(data.split("_")[2])

        await context.bot.send_message(
            user_id,
            "Сейчас все администраторы заняты.\nПопробуйте позже."
        )

        await query.edit_message_text("Заказ отклонён")

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id == ADMIN_ID and user.id in waiting_screenshot:

        buyer_id = waiting_screenshot[user.id]

        await context.bot.forward_message(
            buyer_id,
            update.message.chat_id,
            update.message.message_id
        )

        await context.bot.send_message(
            buyer_id,
            "Купите этот товар и отправьте скрин истории покупок."
        )

        del waiting_screenshot[user.id]

        return

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
        f"Заявка от @{user.username}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if "accept_" in data:

        user_id = int(data.split("_")[1])

        await context.bot.send_message(
            user_id,
            "Поздравляю вы приняты в клан 3TF\nНапишите ваш игровой ID"
        )

        await query.edit_message_text("Игрок принят")

    if "reject_" in data:

        user_id = int(data.split("_")[1])

        keyboard=[[InlineKeyboardButton(
            "Связаться с админом",
            url=f"https://t.me/{ADMIN_USERNAME}"
        )]]

        await context.bot.send_message(
            user_id,
            "Заявка отклонена",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await query.edit_message_text("Игрок отклонён")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку в клан 3TF", callback_data="apply")],
        [InlineKeyboardButton("💰 Покупка в голде", callback_data="buy")]
    ]

    await query.message.reply_text(
        "Главное меню",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(buy_select, pattern="buy7|buy30"))
    app.add_handler(CallbackQueryHandler(order_decision, pattern="order_"))
    app.add_handler(CallbackQueryHandler(back, pattern="back"))

    app.add_handler(CallbackQueryHandler(decision, pattern="accept_|reject_"))

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))

    app.run_polling()

if __name__ == "__main__":
    main()
