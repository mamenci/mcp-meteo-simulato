import json
import sys
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT = Path(__file__).resolve().parent


class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_tool_discovery_and_responses(self):
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(PROJECT / "mcp_server.py")],
            cwd=str(PROJECT),
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                self.assertIn("get_weather_mcp", [tool.name for tool in tools.tools])

                result = await session.call_tool("get_weather_mcp", {"city": "Roma"})
                self.assertFalse(result.isError)
                data = json.loads(result.content[0].text)
                self.assertEqual(
                    data,
                    {"city": "Roma", "temperature_c": 22.0, "description": "Soleggiato"},
                )

                for arguments, message in (
                    ({"city": ""}, "Inserisci il nome di una città."),
                    ({"city": "Venezia"}, "Città non disponibile nella fonte simulata."),
                    (
                        {"city": "Roma", "simulated_unavailable": True},
                        "Servizio meteo simulato non disponibile.",
                    ),
                ):
                    with self.subTest(arguments=arguments):
                        result = await session.call_tool("get_weather_mcp", arguments)
                        self.assertTrue(result.isError)
                        self.assertIn(message, result.content[0].text)


if __name__ == "__main__":
    unittest.main()
