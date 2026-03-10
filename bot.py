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

TOKEN = "ТВОЙ_ТОКЕН"
ADMIN_ID = 123456789
ADMIN_USERNAME = "твой_юзер"

logging.basicConfig(level=logging.INFO)

waiting_for_id = set()
cooldown = {}

PLAYERS_FILE = "players.txt"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    keyboard = [[InlineKeyboardButton("📨 Подать заявку", callback_data="apply")]]

    await update.message.reply_text(
        "👋 Добро пожаловать в клан 3TF\n\n"
        "Нажмите кнопку ниже чтобы подать заявку",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    now = time.time()

    if user.id in cooldown and now - cooldown[user.id] < 300:
        await query.message.reply_text("⏳ Подождите 5 минут перед новой заявкой")
        return

    cooldown[user.id] = now

    await query.message.reply_text(
        "📨 Отправьте:\n\n"
        "1️⃣ Скрин профиля с временем\n"
        "2️⃣ Видео 1 катки"
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
        f"📨 Новая заявка\n\n"
        f"👤 @{user.username}\n"
        f"🆔 {user.id}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if "accept_" in data:

        user_id = int(data.split("_")[1])
        waiting_for_id.add(user_id)

        await context.bot.send_message(
            user_id,
            "✅ Вы приняты\n\nНапишите ваш игровой ID"
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


async def get_player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user

    if user.id in waiting_for_id:

        player_id = update.message.text

        with open(PLAYERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user.username} | {user.id} | {player_id}\n")

        await context.bot.send_message(
            ADMIN_ID,
            f"🎮 Новый игрок\n\n"
            f"👤 @{user.username}\n"
            f"🆔 {user.id}\n"
            f"🎯 Игровой ID: {player_id}"
        )

        await update.message.reply_text("✅ ID отправлен администрации")

        waiting_for_id.remove(user.id)


async def players(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
            data = f.read()

        if data == "":
            data = "Нет игроков"

        await update.message.reply_text(f"📋 Игроки:\n\n{data}")

    except:
        await update.message.reply_text("Файл игроков пуст")


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("📋 Список игроков", callback_data="players")],
    ]

    await update.message.reply_text(
        "👑 Админ панель",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "players":

        try:
            with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
                data = f.read()

            if data == "":
                data = "Нет игроков"

            await query.message.reply_text(data)

        except:
            await query.message.reply_text("Файл пуст")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("players", players))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(CallbackQueryHandler(apply, pattern="apply"))
    app.add_handler(CallbackQueryHandler(decision, pattern="accept_|reject_"))
    app.add_handler(CallbackQueryHandler(admin_buttons, pattern="players"))

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_id))

    app.run_polling()


if __name__ == "__main__":
    main()
