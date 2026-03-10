import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300
ADMIN_USERNAME = "Kroniq_Pensia"

logging.basicConfig(level=logging.INFO)

orders = {}

# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("💰 Купить голдой", callback_data="buy")]
    ]

    text = "Добро пожаловать в клан 3TF"

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# меню покупки
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("100 голды (7 дней)", callback_data="buy100")],
        [InlineKeyboardButton("300 голды (30 дней)", callback_data="buy300")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ]

    await query.message.edit_text(
        "Выберите тариф",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# выбор тарифа
async def buy_select(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == "buy100":
        tariff = "100 голды / 7 дней"
        gold = "100"
    else:
        tariff = "300 голды / 30 дней"
        gold = "300"

    orders[user.id] = {"gold": gold}

    keyboard = [[InlineKeyboardButton("📤 Отправить скрин", callback_data=f"sendscreen_{user.id}")]]

    await context.bot.send_message(
        ADMIN_ID,
        f"Новая покупка\n\n"
        f"User: @{user.username}\n"
        f"ID: {user.id}\n"
        f"Тариф: {tariff}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.message.edit_text(
        "Ожидайте, ваша заявка на рассмотрении администрации"
    )


# админ отправляет скрин
async def send_screen(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])

    orders[user_id]["wait_screen"] = True

    await context.bot.send_message(
        ADMIN_ID,
        "Отправьте скрин покупки"
    )


# медиа
async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id == ADMIN_ID:

        for buyer in orders:

            if orders[buyer].get("wait_screen"):

                await context.bot.forward_message(
                    buyer,
                    update.message.chat_id,
                    update.message.message_id
                )

                keyboard = [
                    [InlineKeyboardButton("✅ Купил", callback_data=f"bought_{buyer}")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
                ]

                await context.bot.send_message(
                    buyer,
                    "После покупки нажмите кнопку",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

                orders[buyer]["wait_screen"] = False

                return


# пользователь нажал купил
async def bought(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])

    keyboard = [[
        InlineKeyboardButton("✅ Принять покупку", callback_data=f"accept_{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
    ]]

    await context.bot.send_message(
        ADMIN_ID,
        f"Пользователь {user_id} нажал КУПИЛ\nПроверьте покупку",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.message.edit_text("Ожидайте проверку покупки")


# решение админа
async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    user_id = int(data.split("_")[1])

    if "accept_" in data:

        orders[user_id]["wait_id"] = True

        await context.bot.send_message(
            user_id,
            "Ваша заявка принята\n\nНапишите свой игровой ID"
        )

    if "reject_" in data:

        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]

        await context.bot.send_message(
            user_id,
            f"Покупка отклонена\nОбратитесь к менеджеру @{ADMIN_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# пользователь отправил id
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id in orders and orders[user.id].get("wait_id"):

        player_id = update.message.text

        keyboard = [[InlineKeyboardButton("📨 Пригласил", callback_data=f"invite_{user.id}")]]

        await context.bot.send_message(
            ADMIN_ID,
            f"Игровой ID пользователя {user.id}\n\nID: {player_id}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text("Ожидайте приглашения в клан")


# пригласил
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[1])

    await context.bot.send_message(
        user_id,
        "Вас пригласили в клан 3TF"
    )


# назад
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await start(update, context)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(buy_select, pattern="buy100|buy300"))
    app.add_handler(CallbackQueryHandler(send_screen, pattern="sendscreen_"))
    app.add_handler(CallbackQueryHandler(bought, pattern="bought_"))
    app.add_handler(CallbackQueryHandler(decision, pattern="accept_|reject_"))
    app.add_handler(CallbackQueryHandler(invite, pattern="invite_"))
    app.add_handler(CallbackQueryHandler(back, pattern="back"))

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

    app.run_polling()


if __name__ == "__main__":
    main()
