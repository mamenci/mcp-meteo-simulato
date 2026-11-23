from mcp.server.fastmcp import FastMCP

from service import get_weather


mcp = FastMCP("meteo-simulato")


@mcp.tool()
def get_weather_mcp(city: str, simulated_unavailable: bool = False) -> dict:
    """Restituisce dati meteo fittizi; può simulare un servizio non disponibile."""
    return get_weather(
        city, simulated=True, simulated_unavailable=simulated_unavailable
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
