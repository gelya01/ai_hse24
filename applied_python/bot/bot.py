import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db import init_db
from handlers import start, profile, food, water, exercise, progress, stats, recommend
import logging
from middleware.logging import LoggingMiddleware


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(food.router)
    dp.include_router(water.router)
    dp.include_router(exercise.router)
    dp.include_router(progress.router)
    dp.include_router(stats.router)
    dp.include_router(recommend.router)

    dp.update.middleware(LoggingMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
