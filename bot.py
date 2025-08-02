import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery
from aiogram.filters import Command

# --- Конфигурация ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Создание объектов бота ---
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

# --- Описание наших товаров ---
# Ключ - это `payload`, который мы будем использовать в игре
PRODUCTS = {
    "energy-pack-50": {
        "title": "Набор энергии",
        "description": "Покупка 50 единиц энергии для рыбалки!",
        "prices": [{"label": "Энергия", "amount": 500}] # Цена в ЗВЁЗДАХ. 500 = 5.00 XTR
    },
    "energy-can-1": {
        "title": "Энергетическая банка",
        "description": "Одна банка консервированной энергии.",
        "prices": [{"label": "Банка", "amount": 1500}] # 1500 = 15.00 XTR
    }
}

# --- Обработчик команды /buy ---
# По этой команде мы будем тестировать создание счёта
@dp.message(Command("buy"))
async def command_buy_handler(message: Message):
    payload = message.text.split(" ")[1] # Получаем payload из команды, например "energy-pack-50"

    if payload in PRODUCTS:
        product = PRODUCTS[payload]
        print(f"Создаём счёт для товара {payload} для пользователя {message.chat.id}")
        await bot.send_invoice(
            chat_id=message.chat.id,
            title=product["title"],
            description=product["description"],
            payload=payload,
            provider_token="",  # Для ЗВЁЗД токен провайдера не нужен
            currency="XTR",     # Валюта Telegram Stars
            prices=product["prices"],
            start_parameter="example" # Параметр для deep-link, можно оставить пустым
        )
    else:
        await message.answer("Такой товар не найден!")

# --- Обработчик: Предварительный запрос на оплату ---
# Этот обработчик всё так же нужен для подтверждения
@dp.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    print(f"Подтверждаем платёж за {pre_checkout_query.invoice_payload}")
    await pre_checkout_query.answer(ok=True)


# --- Обработчик: Успешный платёж ---
@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload

    print(f"--- УСПЕШНЫЙ ПЛАТЁЖ: {payload} от {message.from_user.id} ---")
    # Здесь ты будешь начислять покупку игроку


# --- Основная функция запуска ---
async def main():
    print("Запускаю бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())