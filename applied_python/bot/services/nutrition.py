import aiohttp
from config import NUTRITIONIX_APP_ID, NUTRITIONIX_API_KEY


async def get_nutrition_info(food_text):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    json_data = {"query": food_text}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=json_data) as response:
                response.raise_for_status()
                data = await response.json()
                if "foods" not in data:
                    return None
                return [
                    {"name": item["food_name"], "calories": item["nf_calories"]}
                    for item in data["foods"]
                ]
        except aiohttp.ClientResponseError:
            return None
        except aiohttp.ClientError:
            return None
