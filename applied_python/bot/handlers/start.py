from aiogram import Bot
from aiogram import Router
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from aiogram.types import BotCommandScopeDefault

router = Router()


@router.message(Command("start"))
async def start_command(message: Message, bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="set_profile", description="Заполнить профиль"),
            BotCommand(command="log_food", description="Добавить еду"),
            BotCommand(command="log_water", description="Добавить воду"),
            BotCommand(command="log_workout", description="Добавить тренировку"),
            BotCommand(command="check_progress", description="Посмотреть прогресс"),
            BotCommand(
                command="stats", description="Прогресс на графиках за последнюю неделю"
            ),
            BotCommand(command="recommend", description="Получить рекомендации"),
        ],
        scope=BotCommandScopeDefault(),
    )

    await message.answer(
        "Привет! Я — бот-помощник по здоровью и питанию!\n\n"
        "Я помогу тебе отслеживать калории, воду и тренировки.\n"
        "Вот что я умею:\n"
        "🔹 /set_profile — заполнить профиль\n"
        "🔹 /log_food [текст] — добавить еду\n"
        "🔹 /log_water [текст] — добавить воду\n"
        "🔹 /log_workout [текст] — добавить тренировку\n"
        "🔹 /check_progress — проверить дневной баланс калорий и воды\n"
        "🔹 /stats — графики по потребленным калориям и воде за последнюю неделю\n"
        "🔹 /recommend — получить рекомендации по питанию и тренировкам\n"
        "\n👉 Начни с команды /set_profile, чтобы заполнить свой профиль и начать мне выстраивать твой путь!"
    )
