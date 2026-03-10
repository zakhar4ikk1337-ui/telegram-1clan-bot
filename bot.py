from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8771277043:AAF9ot5lj0G0HwGImuLHi-JUNSTKM6TEzz8"
ADMIN_ID = 5889477300  # ваш Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# кнопки тарифа
keyboard = InlineKeyboardMarkup()
keyboard.add(
    InlineKeyboardButton("100 голды", callback_data="gold100"),
    InlineKeyboardButton("200 голды", callback_data="gold200")
)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("🔥 Акция! Выберите тариф:", reply_markup=keyboard)

# обработка 100 голды
@dp.callback_query_handler(lambda c: c.data == "gold100")
async def gold100(callback: types.CallbackQuery):
    user = callback.from_user
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новая заявка!\n\n"
        f"Пользователь: @{user.username}\n"
        f"ID: {user.id}\n"
        f"Тариф: 100 голды"
    )
    await callback.message.answer("✅ Заявка отправлена администратору")
    await callback.answer()

# обработка 200 голды
@dp.callback_query_handler(lambda c: c.data == "gold200")
async def gold200(callback: types.CallbackQuery):
    user = callback.from_user
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новая заявка!\n\n"
        f"Пользователь: @{user.username}\n"
        f"ID: {user.id}\n"
        f"Тариф: 200 голды"
    )
    await callback.message.answer("✅ Заявка отправлена администратору")
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp)
