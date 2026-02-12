import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from states import Registration, Valentine
from keyboards import main_menu
import database as db

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user = await db.get_user_by_telegram_id(message.from_user.id)

    if user:
        await message.answer("Ти вже зареєстрований ❤️", reply_markup=main_menu())
    else:
        await message.answer("Введи своє ім'я:")
        await state.set_state(Registration.first_name)


@dp.message(Registration.first_name)
async def reg_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введи своє прізвище:")
    await state.set_state(Registration.last_name)


@dp.message(Registration.last_name)
async def reg_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введи свою групу:")
    await state.set_state(Registration.group_name)


@dp.message(Registration.group_name)
async def reg_group(message: Message, state: FSMContext):
    data = await state.get_data()

    await db.add_user(
        message.from_user.id,
        data["first_name"],
        data["last_name"],
        message.text
    )

    await message.answer("Реєстрація завершена ❤️", reply_markup=main_menu())

    await state.clear()

    # Перевірка відкладених валентинок
    user = await db.get_user_by_telegram_id(message.from_user.id)
    pending = await db.get_pending_valentines(user[1])

    for valentine in pending:
        await message.answer(f"💌 Тобі валентинка:\n\n{valentine[1]}")
        await db.mark_delivered(valentine[0])


@dp.message(F.text == "💌 Написати валентинку")
async def write_valentine(message: Message, state: FSMContext):
    await message.answer("Введи ім'я та прізвище отримувача:")
    await state.set_state(Valentine.recipient)


@dp.message(Valentine.recipient)
async def valentine_recipient(message: Message, state: FSMContext):
    await state.update_data(recipient=message.text)
    await message.answer("Напиши текст валентинки:")
    await state.set_state(Valentine.message)


@dp.message(Valentine.message)
async def valentine_message(message: Message, state: FSMContext):
    data = await state.get_data()
    recipient = await db.get_user_by_fullname(data["recipient"])

    sender_id = message.from_user.id

    if recipient:
        await bot.send_message(
            recipient[1],
            f"💌 Тобі прийшла таємна валентинка:\n\n{message.text}"
        )

        await db.save_valentine(
            sender_id,
            data["recipient"],
            recipient[1],
            message.text,
            1
        )

        await message.answer("Валентинка доставлена ❤️")

    else:
        await db.save_valentine(
            sender_id,
            data["recipient"],
            None,
            message.text,
            0
        )

        await message.answer(
            "Ця людина ще не зареєстрована.\n"
            "Валентинка збережена і буде доставлена після реєстрації ❤️"
        )

    await state.clear()


@dp.message(F.text == "📥 Мої валентинки")
async def my_valentines(message: Message):
    user = await db.get_user_by_telegram_id(message.from_user.id)

    async with db.aiosqlite.connect(db.DB_NAME) as database:
        cursor = await database.execute("""
        SELECT message FROM valentines
        WHERE recipient_id = ?
        """, (user[1],))
        messages = await cursor.fetchall()

    if messages:
        for msg in messages:
            await message.answer(f"💌 {msg[0]}")
    else:
        await message.answer("Поки що валентинок немає ❤️")


async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
