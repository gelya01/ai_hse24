from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import SessionLocal
from models.user import User
from models.food_log import FoodLog
from models.water_log import WaterLog
from models.exercise_log import ExerciseLog
from sqlalchemy import select, func
from datetime import date

router = Router()


@router.message(Command("check_progress"))
async def check_progress(message: Message):
    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(
                "Вы ещё не заполнили профиль! Используйте /set_profile"
            )
            return

        today = date.today()

        food_calories = await session.execute(
            select(func.sum(FoodLog.calories)).where(
                FoodLog.user_id == message.from_user.id,
                func.date(FoodLog.timestamp) == today,
            )
        )
        food_calories = food_calories.scalar() or 0

        exercise_calories = await session.execute(
            select(func.sum(ExerciseLog.calories_burned)).where(
                ExerciseLog.user_id == message.from_user.id,
                func.date(ExerciseLog.timestamp) == today,
            )
        )
        exercise_calories = exercise_calories.scalar() or 0

        water_ml = await session.execute(
            select(func.sum(WaterLog.amount)).where(
                WaterLog.user_id == message.from_user.id,
                func.date(WaterLog.timestamp) == today,
            )
        )
        water_ml = water_ml.scalar() or 0

        calorie_balance = food_calories - exercise_calories
        rem_water = max(0, user.daily_water * 1000 - water_ml)

    progress_message = (
        f"📊 Прогресс на сегодня:\n\n"
        f"💧 Вода:\n"
        f"   - Выпито: {water_ml} мл из {int(user.daily_water * 1000)} мл\n"
        f"   - Осталось: {rem_water} мл\n\n"
        f"🔥 Калории:\n"
        f"   - Потреблено: {food_calories} ккал из {int(user.daily_calories)} ккал\n"
        f"   - Сожжено: {exercise_calories} ккал\n"
        f"   - Баланс: {calorie_balance} ккал"
    )

    await message.answer(progress_message)
