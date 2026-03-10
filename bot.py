import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300
ADMIN_USERNAME = "Kroniq_Pensia"

logging.basicConfig(level=logging.INFO)

waiting_screen = {}

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📨 Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("💰 Покупка в голде", callback_data="buy")]
    ]

    if update.message:
        await update.message.reply_text(
            "Добро пожаловать в клан 3TF",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.callback_query.message.edit_text(
            "Добро пожаловать в клан 3TF",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Кнопка назад
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await start(update, context)

# Подача заявки
async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]

    await query.message.edit_text(
        "Отправьте:\n\n"
        "1️⃣ Скрин профиля с временем\n"
        "2️⃣ Видео 1 катки Закладка бомби (ЗБ)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Покупка
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("100 голды (7 дней)", callback_data="buy7")],
        [InlineKeyboardButton("200 голды (30 дней)", callback_data="buy30")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ]

    await query.message.edit_text(
        "🔥 Акция\n\nВыберите тариф:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Выбор тарифа
async def buy_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == "buy7":
        text = "100 голды / 7 дней"
    else:
        text = "200 голды / 30 дней"

    keyboard = [[
        InlineKeyboardButton("✅ Принять", callback_data=f"acceptbuy_{user.id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"rejectbuy_{user.id}")
    ]]

    await context.bot.send_message(
        ADMIN_ID,
        f"Новая покупка\n\nПользователь: @{user.username}\nID: {user.id}\nТариф: {text}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.message.edit_text("⏳ Ожидание принятия заказа")

# Решение по покупке
async def buy_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if "acceptbuy_" in data:

        user_id = int(data.split("_")[1])

        waiting_screen[ADMIN_ID] = user_id

        await context.bot.send_message(
            ADMIN_ID,
            "Отправьте скрин товара"
        )

        await context.bot.send_message(
            user_id,
            "Администратор принял заказ. Ожидайте скрин."
        )

    if "rejectbuy_" in data:

        user_id = int(data.split("_")[1])

        await context.bot.send_message(
            user_id,
            "Сейчас все администраторы заняты."
        )

# Медиа
async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id == ADMIN_ID and ADMIN_ID in waiting_screen:

        buyer = waiting_screen[ADMIN_ID]

        await context.bot.forward_message(
            buyer,
            update.message.chat_id,
            update.message.message_id
        )

        await context.bot.send_message(
            buyer,
            "После покупки отправьте скрин истории покупок."
        )

        del waiting_screen[ADMIN_ID]

        return

    await context.bot.forward_message(
        ADMIN_ID,
        update.message.chat_id,
        update.message.message_id
    )

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(buy_select, pattern="buy7|buy30"))
    app.add_handler(CallbackQueryHandler(buy_decision, pattern="acceptbuy_|rejectbuy_"))
    app.add_handler(CallbackQueryHandler(back, pattern="back"))

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))

    app.run_polling()

if __name__ == "__main__":
    main()
