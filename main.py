import argparse

from service import SIMULATED_WEATHER, get_weather, get_welcome_message


def main(simulated=True, simulated_unavailable=False):
    print(get_welcome_message())
    if simulated:
        cities = ", ".join(city.title() for city in SIMULATED_WEATHER)
        print(f"Modalità simulata: dati fittizi per {cities}.")
    city = input("Inserisci una città: ")

    try:
        weather = get_weather(
            city, simulated=simulated, simulated_unavailable=simulated_unavailable
        )
    except (ValueError, RuntimeError) as error:
        print(str(error))
        return

    print(f"Città: {weather['city']}")
    print(f"Temperatura: {weather['temperature_c']} °C")
    print(f"Descrizione: {weather['description']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consulta il meteo di una città.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--simulato", action="store_true", help="usa dati fittizi senza Internet (predefinito)"
    )
    mode.add_argument(
        "--reale", action="store_true", help="usa il servizio meteo online"
    )
    parser.add_argument(
        "--simula-indisponibile", action="store_true",
        help="simula un servizio meteo non disponibile",
    )
    args = parser.parse_args()
    if args.reale and args.simula_indisponibile:
        parser.error("--simula-indisponibile richiede la modalità simulata")
    main(simulated=not args.reale, simulated_unavailable=args.simula_indisponibile)
