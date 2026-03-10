import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300
ADMIN_USERNAME = "Kroniq_Pensia"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📨 Подать заявку в клан 3TF", callback_data="apply")]]
    await update.message.reply_text(
        "Добро пожаловать в клан 3TF",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Отправьте:\n\n"
        "1️⃣ Скрин профиля с временем\n"
        "2️⃣ Видео 1 катки ММ"
    )

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

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

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(decision, pattern="accept_|reject_"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))

    app.run_polling()

if __name__ == "__main__":
    main()
