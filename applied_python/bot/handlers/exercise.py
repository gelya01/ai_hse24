import random
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import SessionLocal
from models.exercise_log import ExerciseLog
from models.user import User
from services.translator import translate_to_english
from services.workout import get_exercise_info

router = Router()

stickers = [
    "CAACAgIAAxkBAAExqd9nq6ou85itPa_B4EKCfIp5AhtVowACYx8AAosjyEqFa8uEhVY3OzYE",
    "CAACAgIAAxkBAAExqeVnq6qAsGZmYKinhGygZEIaILAH6AACjxkAAkiMyUpBH-Q-bjBkzDYE"
    "CAACAgIAAxkBAAExqfNnq6vXQ5rRCBuwa_k1AdFs0dFh5gAC-iIAAr9byUpLYQOhDaYNtzYE",
    "CAACAgIAAxkBAAExqfVnq6v6jAZfJQsM2yojP9Cvkv2v3wACwhsAAvelAAFLym-W5FyKrPQ2BA",
    "CAACAgIAAxkBAAExqflnq6wME5n02MKLErM3UxnW-NM0SgACRxkAAqG6AAFLG3z-FzoJ5qY2BA",
]


@router.message(Command("log_workout"))
async def log_workout(message: Message):
    workout_text = message.text.replace("/log_workout", "").strip()
    parts = workout_text.split()
    if len(parts) < 2 or not parts[-1].isdigit():
        await message.answer(
            "Введите тренировку и время в минутах. Например:\n" "/log_workout бег 30"
        )
        return

    exercise_name = " ".join(parts[:-1])
    duration = int(parts[-1])

    if duration <= 0:
        await message.answer("Длительность тренировки должна быть больше 0 минут!")
        return

    translated_exercise = await translate_to_english(exercise_name)
    exercise_info = await get_exercise_info(translated_exercise, duration)

    if not exercise_info:
        await message.answer(
            "Не удалось определить расход калорий для тренировки. Попробуйте описать тренировку по-другому."
        )
        return

    calories_burned = exercise_info["calories"]
    additional_water = exercise_info["additional_water"]

    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(
                "Вы ещё не заполнили профиль! Используйте /set_profile"
            )
            return

        exercise_log_entry = ExerciseLog(
            user_id=message.from_user.id,
            exercise_name=exercise_name,
            duration=duration,
            calories_burned=calories_burned,
        )
        session.add(exercise_log_entry)

        if additional_water > 0:
            user.daily_water += additional_water / 1000

        await session.commit()

    random_sticker = random.choice(stickers)

    await message.answer(
        f"🏋️‍♂️ Тренировка записана:\n"
        f"🔹 Упражнение: {exercise_name} ({duration} мин)\n"
        f"🔥 Сожжено калорий: {calories_burned} ккал\n"
        f"💧 Дополнительно выпейте: {additional_water:.0f} мл воды!"
    )
    await message.answer_sticker(random_sticker)
