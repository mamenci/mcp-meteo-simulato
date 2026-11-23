import json
from urllib.parse import quote
from urllib.request import urlopen


def get_weather(city):
    url = f"https://wttr.in/{quote(city, safe='')}?format=j1"

    with urlopen(url, timeout=10) as response:
        data = json.load(response)

    current = data["current_condition"][0]
    return {
        "city": city,
        "temperature_c": current["temp_C"],
        "description": current["weatherDesc"][0]["value"],
    }
