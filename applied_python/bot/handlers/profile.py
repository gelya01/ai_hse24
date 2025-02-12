from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import SessionLocal
from models.user import User
from services.calculations import calculate_daily_calories, calculate_daily_water
from services.weather import get_temperature
from services.translator import translate_to_english

router = Router()


class ProfileState(StatesGroup):
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_activity = State()
    waiting_for_city = State()
    waiting_for_goal = State()


@router.message(Command("set_profile"))
async def set_profile_start(message: Message, state: FSMContext):
    await message.answer("Выберите ваш пол: мужчина / женщина")
    await state.set_state(ProfileState.waiting_for_gender)


@router.message(ProfileState.waiting_for_gender)
async def set_gender(message: Message, state: FSMContext):
    gender = message.text.lower()
    if gender not in ["мужчина", "женщина"]:
        await message.answer("Пожалуйста, введите 'мужчина' или 'женщина'.")
        return
    await state.update_data(gender=gender)
    await message.answer("Введите ваш возраст (от 12 до 100):")
    await state.set_state(ProfileState.waiting_for_age)


@router.message(ProfileState.waiting_for_age)
async def set_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (12 <= int(message.text) <= 100):
        await message.answer(
            "Введите корректный возраст целым числом (от 12 до 100 лет)."
        )
        return
    await state.update_data(age=int(message.text))
    await message.answer("Введите ваш вес в кг (30-300):")
    await state.set_state(ProfileState.waiting_for_weight)


@router.message(ProfileState.waiting_for_weight)
async def set_weight(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (30 <= int(message.text) <= 300):
        await message.answer("Введите корректный вес целым числом (30-300 в кг).")
        return
    await state.update_data(weight=int(message.text))
    await message.answer("Введите ваш рост в см (100-250):")
    await state.set_state(ProfileState.waiting_for_height)


@router.message(ProfileState.waiting_for_height)
async def set_height(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (100 <= int(message.text) <= 250):
        await message.answer("⚠ Введите корректный рост целым числом (100-250 см).")
        return
    await state.update_data(height=int(message.text))
    await message.answer(
        "Какой у вас уровень активности? Введите цифру (1-5):\n"
        "1. Минимальный (сидячий образ жизни)\n"
        "2. Лёгкий (1-3 тренировки в неделю)\n"
        "3. Средний (3-5 тренировок в неделю)\n"
        "4. Высокий (5-7 тренировок в неделю)\n"
        "5. Очень высокий (спорт ежедневно, профессиональный спортсмен(ка))"
    )
    await state.set_state(ProfileState.waiting_for_activity)


@router.message(ProfileState.waiting_for_activity)
async def set_activity(message: Message, state: FSMContext):
    if message.text not in ["1", "2", "3", "4", "5"]:
        await message.answer("Введите число от 1 до 5.")
        return
    activity_levels = [1.2, 1.375, 1.55, 1.725, 1.9]
    await state.update_data(activity=activity_levels[int(message.text) - 1])
    await message.answer("Введите ваш город:")
    await state.set_state(ProfileState.waiting_for_city)


@router.message(ProfileState.waiting_for_city)
async def set_city(message: Message, state: FSMContext):
    city = message.text.strip()
    translated_city = await translate_to_english(city)
    temperature = await get_temperature(translated_city)
    await state.update_data(city=city, temperature=temperature)
    await message.answer(
        "Какая у вас цель? Выберите одну:\n"
        "🔹 Похудение\n"
        "🔹 Поддержание\n"
        "🔹 Набор массы"
    )
    await state.set_state(ProfileState.waiting_for_goal)


@router.message(ProfileState.waiting_for_goal)
async def set_goal(message: Message, state: FSMContext):
    goal = message.text.lower()
    if goal not in ["похудение", "поддержание", "набор массы"]:
        await message.answer(
            "Введите цель: 'Похудение', 'Поддержание' или 'Набор массы'."
        )
        return
    await state.update_data(goal=goal)

    user_data = await state.get_data()

    daily_calories = calculate_daily_calories(
        user_data["weight"],
        user_data["height"],
        user_data["age"],
        user_data["gender"],
        user_data["activity"],
        goal,
    )

    daily_water = calculate_daily_water(user_data["weight"], user_data["activity"])

    if user_data["temperature"] and user_data["temperature"] > 25:
        daily_water += 0.5

    user_data.pop(
        "temperature", None
    )  # убираем temperature, потому что такого поля нет в таблице users

    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if user:
            user.age = user_data["age"]
            user.weight = user_data["weight"]
            user.height = user_data["height"]
            user.gender = user_data["gender"]
            user.activity = user_data["activity"]
            user.goal = goal
            user.city = user_data["city"]
            user.daily_calories = daily_calories
            user.daily_water = daily_water
        else:
            user = User(
                id=message.from_user.id,
                **user_data,
                daily_calories=daily_calories,
                daily_water=daily_water,
            )
        session.add(user)
        await session.commit()

    await message.answer(
        f"✅ Профиль сохранён!\n\n"
        f"📊 Ваша суточная норма:\n"
        f"🔥 Калории: {daily_calories:.0f} ккал\n"
        f"💧 Вода: {daily_water:.1f} л\n"
    )
    await state.clear()
