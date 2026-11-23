import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import service
import service_iniziale


def initial_response():
    return io.BytesIO(
        b'{"current_condition": [{"temp_C": "22", '
        b'"weatherDesc": [{"value": "Sunny"}]}]}'
    )


class ConfrontoVersioni(unittest.TestCase):
    def test_citta_valida(self):
        with patch("service_iniziale.urlopen", return_value=initial_response()):
            initial = service_iniziale.get_weather("Roma")
        with patch("service.urlopen") as online:
            current = service.get_weather("Roma")
            online.assert_not_called()

        self.assertEqual(initial, {
            "city": "Roma", "temperature_c": "22", "description": "Sunny"
        })
        self.assertEqual(current, {
            "city": "Roma", "temperature_c": 22.0, "description": "Soleggiato"
        })

    def test_citta_vuota(self):
        with patch("service_iniziale.urlopen", return_value=initial_response()) as online:
            initial = service_iniziale.get_weather("  ")
            online.assert_called_once()
        self.assertEqual(initial["city"], "  ")

        with patch("service.urlopen") as online:
            with self.assertRaisesRegex(ValueError, "Inserisci il nome"):
                service.get_weather("  ")
            online.assert_not_called()

    def test_citta_non_trovata(self):
        with HTTPError(
            "https://wttr.in/", 500, "error", {},
            io.BytesIO(b"location not found: location not found"),
        ) as error:
            with patch("service_iniziale.urlopen", side_effect=error):
                with self.assertRaises(HTTPError):
                    service_iniziale.get_weather("Venezia")

        with patch("service.urlopen") as online:
            with self.assertRaisesRegex(ValueError, "non disponibile nella fonte simulata"):
                service.get_weather("Venezia")
            online.assert_not_called()

    def test_servizio_non_disponibile(self):
        with patch("service_iniziale.urlopen", side_effect=URLError("unavailable")):
            with self.assertRaises(URLError):
                service_iniziale.get_weather("Roma")

        with patch("service.urlopen") as online:
            with self.assertRaisesRegex(RuntimeError, "Servizio meteo simulato non disponibile"):
                service.get_weather("Roma", simulated_unavailable=True)
            online.assert_not_called()


if __name__ == "__main__":
    unittest.main()
