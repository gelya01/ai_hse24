import aiohttp
from config import NUTRITIONIX_APP_ID, NUTRITIONIX_API_KEY

WATER_CONSUMPTION_RATES = {
    "running": 15,
    "cardio": 15,
    "hiit": 15,
    "strength training": 10,
    "weightlifting": 10,
    "yoga": 5,
    "stretching": 5,
    "cycling": 12,
    "swimming": 12,
}


async def get_exercise_info(exercise_name, duration):
    url = "https://trackapi.nutritionix.com/v2/natural/exercise"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    json_data = {"query": f"{exercise_name} {duration} min"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=json_data) as response:
                response.raise_for_status()
                data = await response.json()

                if "exercises" not in data:
                    return None
                calories_burned = data["exercises"][0]["nf_calories"]
                exercise_type = data["exercises"][0]["name"].lower()
                water_per_minute = WATER_CONSUMPTION_RATES.get(
                    exercise_type, 10
                )  # по умолчанию 10 мл/мин
                additional_water = water_per_minute * duration

                return {
                    "calories": calories_burned,
                    "additional_water": additional_water,
                }
        except aiohttp.ClientResponseError:
            return None
        except aiohttp.ClientError:
            return None
