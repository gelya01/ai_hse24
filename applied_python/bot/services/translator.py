import aiohttp


async def translate_to_english(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": "ru", "tl": "en", "dt": "t", "q": text}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data[0][0][0]
        except aiohttp.ClientResponseError:
            return None
        except aiohttp.ClientError:
            return None
