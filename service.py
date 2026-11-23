import json
import math
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

from config import APP_NAME, WEATHER_BASE_URL, WEATHER_TIMEOUT

SIMULATED_WEATHER = {
    "roma": {"temperature_c": 22.0, "description": "Soleggiato"},
    "milano": {"temperature_c": 16.0, "description": "Nuvoloso"},
    "napoli": {"temperature_c": 24.0, "description": "Sereno"},
    "torino": {"temperature_c": 14.0, "description": "Pioggia debole"},
    "firenze": {"temperature_c": 19.0, "description": "Parzialmente nuvoloso"},
}


def get_welcome_message():
    return f"{APP_NAME}: progetto pronto."


def get_weather(city, simulated=True, simulated_unavailable=False):
    if not isinstance(city, str) or not city.strip():
        raise ValueError("Inserisci il nome di una città.")

    if simulated_unavailable and not simulated:
        raise ValueError("L'errore simulato richiede la modalità simulata.")

    city = city.strip()
    if simulated:
        if simulated_unavailable:
            raise RuntimeError("Servizio meteo simulato non disponibile.")
        weather = SIMULATED_WEATHER.get(city.casefold())
        if weather is None:
            raise ValueError("Città non disponibile nella fonte simulata.")
        return {"city": city, **weather}

    url = f"{WEATHER_BASE_URL}/{quote(city, safe='')}?format=j1&lang=it"

    try:
        with urlopen(url, timeout=WEATHER_TIMEOUT) as response:
            data = json.load(response)

        current = data["current_condition"][0]
        temperature = float(current["temp_C"])
        if not math.isfinite(temperature):
            raise ValueError("Temperatura non valida.")
        return {
            "city": city,
            "temperature_c": temperature,
            "description": current["lang_it"][0]["value"],
        }
    except HTTPError as error:
        try:
            with error:
                body = error.read(1024).decode("utf-8", errors="replace").strip()
        except OSError:
            body = ""
        if error.code == 500 and body.casefold() == "location not found: location not found":
            raise ValueError("Città non trovata dal servizio meteo.") from error
        raise RuntimeError("Impossibile ottenere i dati meteo.") from error
    except (URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError("Impossibile ottenere i dati meteo.") from error
