from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import SessionLocal
from models.food_log import FoodLog
from models.user import User
from services.nutrition import get_nutrition_info
from services.translator import translate_to_english

router = Router()


@router.message(Command("log_food"))
async def log_food(message: Message):
    food_text = message.text.replace("/log_food", "").strip()

    if not food_text:
        await message.answer(
            "Введите, что вы съели. Указывайте также граммы, если знаете\n"
            "Например:\n"
            "/log_food тарелка куриного супа и два сэндвича\n"
            "/log_food жареные яйца 100г и кофе 200г"
        )
        return

    translated_text = await translate_to_english(food_text)
    nutrition_info = await get_nutrition_info(translated_text)

    if not nutrition_info:
        await message.answer(
            "Не удалось определить калорийность. Попробуйте описать еду по-другому."
        )
        return

    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer(
                "Вы ещё не заполнили профиль! Используйте /set_profile"
            )
            return

        total_calories = 0
        detailed_items = []

        for item in nutrition_info:
            total_calories += int(item["calories"])
            detailed_items.append(f"🍽 {item['name']}: {item['calories']} ккал")

            food_log_entry = FoodLog(
                user_id=message.from_user.id,
                food_name=item["name"],
                calories=item["calories"],
            )
            session.add(food_log_entry)

        await session.commit()

    await message.answer(
        f"✅ Добавлено {len(nutrition_info)} продуктов!\n\n"
        f"{chr(10).join(detailed_items)}\n"
        f"🔥 Всего: {total_calories} ккал"
    )
