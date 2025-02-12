from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import SessionLocal
from models.user import User
from services.recommendations import get_recommendations

router = Router()


@router.message(Command("recommend"))
async def recommend_food_and_workout(message: Message):
    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(
                "Вы ещё не заполнили профиль! Используйте /set_profile"
            )
            return
        recommendations = get_recommendations(user.goal)

    await message.answer(f"Рекомендации по питанию и тренировкам:\n\n{recommendations}")
