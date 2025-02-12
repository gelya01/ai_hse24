import logging
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from db import SessionLocal
from models.user import User
from models.food_log import FoodLog
from models.water_log import WaterLog
from models.exercise_log import ExerciseLog
from services.plotter import generate_weekly_progress_plot
from sqlalchemy import select, func
from datetime import date, timedelta

router = Router()


@router.message(Command("stats"))
async def show_weekly_stats(message: Message):
    """Генерирует и отправляет графики за последние 7 дней"""
    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(
                "⚠ Вы ещё не заполнили профиль! Используйте /set_profile"
            )
            return

        today = date.today()
        start_date = today - timedelta(days=6)  # Берём последние 7 дней
        dates = [
            (start_date + timedelta(days=i)).isoformat() for i in range(7)
        ]  # Формат дат YYYY-MM-DD

        # 🔹 1. Получаем данные по воде
        water_query = await session.execute(
            select(func.date(WaterLog.timestamp), func.sum(WaterLog.amount))
            .where(WaterLog.user_id == message.from_user.id)
            .where(WaterLog.timestamp >= start_date)
            .group_by(func.date(WaterLog.timestamp))
        )
        water_data = {str(row[0]): row[1] for row in water_query.fetchall()}
        water_values = [water_data.get(day, 0) for day in dates]

        # 🔹 2. Получаем данные по потреблённым калориям
        food_query = await session.execute(
            select(func.date(FoodLog.timestamp), func.sum(FoodLog.calories))
            .where(FoodLog.user_id == message.from_user.id)
            .where(FoodLog.timestamp >= start_date)
            .group_by(func.date(FoodLog.timestamp))
        )
        calorie_data = {str(row[0]): row[1] for row in food_query.fetchall()}
        calorie_values = [calorie_data.get(day, 0) for day in dates]

        # 🔹 3. Получаем данные по сожжённым калориям
        burned_query = await session.execute(
            select(
                func.date(ExerciseLog.timestamp), func.sum(ExerciseLog.calories_burned)
            )
            .where(ExerciseLog.user_id == message.from_user.id)
            .where(ExerciseLog.timestamp >= start_date)
            .group_by(func.date(ExerciseLog.timestamp))
        )
        burned_calories_data = {str(row[0]): row[1] for row in burned_query.fetchall()}
        burned_values = [burned_calories_data.get(day, 0) for day in dates]

        # 🔹 Логирование для отладки
        logging.info(f"📊 Даты: {dates}")
        logging.info(f"💧 Вода: {water_values}")
        logging.info(f"🔥 Калории (съедено): {calorie_values}")
        logging.info(f"🔥 Калории (сожжено): {burned_values}")

        # 🔹 Генерируем график
        plot_buffer = generate_weekly_progress_plot(
            dates, water_values, calorie_values, burned_values
        )

    # 🔹 Отправляем изображение пользователю
    await message.answer_photo(
        photo=BufferedInputFile(plot_buffer.getvalue(), filename="progress.png"),
        caption="📊 Ваш прогресс за неделю",
    )
