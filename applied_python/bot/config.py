import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")  # для еды и тренировок
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # для получения температуры
