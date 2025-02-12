from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import SessionLocal
from models.water_log import WaterLog
from models.user import User
from sqlalchemy import select, func
from datetime import date

router = Router()


@router.message(Command("log_water"))
async def log_water(message: Message):
    water_text = message.text.replace("/log_water", "").strip()

    if not water_text.isdigit():
        await message.answer(
            "Введите количество воды в мл. Например:\n" "/log_water 250"
        )
        return

    water_amount = int(water_text)

    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(
                "Вы ещё не заполнили профиль! Используйте /set_profile"
            )
            return

        water_log_entry = WaterLog(user_id=message.from_user.id, amount=water_amount)
        session.add(water_log_entry)
        await session.commit()
        # расчет воды за сегодня
        today = date.today()
        total_water_ml = await session.execute(
            select(func.sum(WaterLog.amount)).where(
                WaterLog.user_id == message.from_user.id,
                func.date(WaterLog.timestamp) == today,
            )
        )
        total_water_ml = total_water_ml.scalar() or 0

        daily_water_ml = int(user.daily_water * 1000)  # из литров в мл
        remaining_water = max(0, daily_water_ml - total_water_ml)

    await message.answer(
        f"💧 Вы выпили {water_amount} мл воды!\n"
        f"📊 Всего за сегодня: {total_water_ml} мл из {daily_water_ml} мл\n"
        f"💧 Осталось выпить: {remaining_water} мл"
    )
