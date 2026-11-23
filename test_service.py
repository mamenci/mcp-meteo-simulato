import io
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import main
import service


class WeatherTests(unittest.TestCase):
    def test_valid_city(self):
        response = io.BytesIO(
            b'{"current_condition": [{"temp_C": "22.5", '
            b'"lang_it": [{"value": "Soleggiato"}]}]}'
        )
        with patch("service.urlopen", return_value=response) as urlopen:
            result = service.get_weather(" New York ", simulated=False)

        self.assertEqual(
            result,
            {"city": "New York", "temperature_c": 22.5, "description": "Soleggiato"},
        )
        self.assertIsInstance(result["temperature_c"], float)
        urlopen.assert_called_once_with(
            "https://wttr.in/New%20York?format=j1&lang=it", timeout=10
        )

    def test_empty_city_does_not_call_source(self):
        with patch("service.urlopen") as urlopen:
            with self.assertRaisesRegex(ValueError, "Inserisci il nome"):
                service.get_weather("  ")
            urlopen.assert_not_called()

    def test_city_not_found_by_service(self):
        error = HTTPError(
            "https://wttr.in/", 500, "error", {},
            io.BytesIO(b"location not found: location not found"),
        )
        with patch("service.urlopen", side_effect=error):
            with self.assertRaisesRegex(ValueError, "Città non trovata"):
                service.get_weather("Città inventata", simulated=False)

    def test_geocoding_provider_failure_is_not_city_not_found(self):
        error = HTTPError(
            "https://wttr.in/", 500, "error", {},
            io.BytesIO(b"location not found: upstream error: opencage: invalid response"),
        )
        with patch("service.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "Impossibile ottenere"):
                service.get_weather("Roma", simulated=False)

    def test_unavailable_source(self):
        for error in (URLError("unavailable"), TimeoutError("timeout")):
            with self.subTest(error=type(error).__name__):
                with patch("service.urlopen", side_effect=error):
                    with self.assertRaisesRegex(RuntimeError, "Impossibile ottenere"):
                        service.get_weather("Roma", simulated=False)

    def test_invalid_source_response(self):
        responses = [
            b"{}",
            b"not json",
            b'{"current_condition": [{"temp_C": "nan", "lang_it": [{"value": "Sereno"}]}]}',
            b'{"current_condition": [{"temp_C": "22", "weatherDesc": [{"value": "Sunny"}]}]}',
        ]
        for response in responses:
            with self.subTest(response=response):
                with patch("service.urlopen", return_value=io.BytesIO(response)):
                    with self.assertRaisesRegex(RuntimeError, "Impossibile ottenere"):
                        service.get_weather("Roma", simulated=False)

    def test_simulated_city_without_network(self):
        with patch("service.urlopen") as urlopen:
            result = service.get_weather(" roma ", simulated=True)
            urlopen.assert_not_called()
        self.assertEqual(
            result,
            {"city": "roma", "temperature_c": 22.0, "description": "Soleggiato"},
        )

    def test_added_simulated_cities_without_network(self):
        for city in ("Napoli", "Torino", "Firenze"):
            with self.subTest(city=city), patch("service.urlopen") as urlopen:
                result = service.get_weather(city)
                self.assertEqual(result["city"], city)
                self.assertIsInstance(result["temperature_c"], float)
                self.assertTrue(result["description"])
                urlopen.assert_not_called()

    def test_unknown_simulated_city_without_network(self):
        with patch("service.urlopen") as urlopen:
            with self.assertRaisesRegex(ValueError, "non disponibile nella fonte simulata"):
                service.get_weather("Venezia", simulated=True)
            urlopen.assert_not_called()

    def test_simulated_unavailable_without_network(self):
        with patch("service.urlopen") as urlopen:
            with self.assertRaisesRegex(RuntimeError, "Servizio meteo simulato non disponibile"):
                service.get_weather("Roma", simulated_unavailable=True)
            urlopen.assert_not_called()

    def test_default_source_is_simulated(self):
        with patch("service.urlopen") as urlopen:
            self.assertEqual(service.get_weather("Roma")["description"], "Soleggiato")
            urlopen.assert_not_called()

    def test_unavailable_simulation_cannot_use_real_source(self):
        with patch("service.urlopen") as urlopen:
            with self.assertRaisesRegex(ValueError, "richiede la modalità simulata"):
                service.get_weather("Roma", simulated=False, simulated_unavailable=True)
            urlopen.assert_not_called()

    def test_main_displays_weather(self):
        weather = {"city": "Roma", "temperature_c": 22.0, "description": "Soleggiato"}
        with patch("builtins.input", return_value="Roma"), \
             patch("main.get_weather", return_value=weather) as get_weather, \
             patch("builtins.print") as print_message:
            main.main()

        get_weather.assert_called_once_with(
            "Roma", simulated=True, simulated_unavailable=False
        )
        print_message.assert_any_call("Città: Roma")
        print_message.assert_any_call("Temperatura: 22.0 °C")
        print_message.assert_any_call("Descrizione: Soleggiato")

    def test_main_displays_errors(self):
        with patch("builtins.input", return_value=""), \
             patch("builtins.print") as print_message:
            main.main()

        print_message.assert_any_call("Inserisci il nome di una città.")

    def test_simulated_mode_from_command_line(self):
        result = subprocess.run(
            [sys.executable, "-B", "main.py"],
            input="Roma\n", text=True, capture_output=True, check=True,
        )
        self.assertIn("Modalità simulata", result.stdout)
        self.assertIn("Napoli, Torino, Firenze", result.stdout)
        self.assertIn("Temperatura: 22.0 °C", result.stdout)
        self.assertIn("Descrizione: Soleggiato", result.stdout)

    def test_unavailable_simulation_from_command_line(self):
        result = subprocess.run(
            [sys.executable, "-B", "main.py", "--simula-indisponibile"],
            input="Roma\n", text=True, capture_output=True, check=True,
        )
        self.assertIn("Servizio meteo simulato non disponibile", result.stdout)

    def test_real_and_unavailable_simulation_are_incompatible(self):
        result = subprocess.run(
            [sys.executable, "-B", "main.py", "--reale", "--simula-indisponibile"],
            input="Roma\n", text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("richiede la modalità simulata", result.stderr)


if __name__ == "__main__":
    unittest.main()
