# Server MCP meteo simulato

Il server espone lo strumento `get_weather_mcp`, che usa esclusivamente dati
fittizi del progetto. Non chiama il servizio meteo online.

## Preparazione dopo il clone

In WSL/Linux, dalla cartella del progetto, crea l'ambiente Python e installa
le dipendenze:

```bash
python3 -m venv --copies .venv
./.venv/bin/python -m pip install -r requirements.txt
```

L'installazione richiede Internet; la fonte meteo simulata no.

## Usarlo con Copilot CLI

1. Apri PowerShell nella cartella del progetto e scrivi `wsl` per entrare in Linux.
2. Nella stessa cartella, avvia `copilot`. Se richiesto, conferma la fiducia nella
   cartella dopo aver esaminato la configurazione `.mcp.json`.
3. Usa `/mcp list` per controllare che `meteo-simulato` sia connesso. Se la
   sessione era già aperta prima della configurazione, usa `/mcp reload`.
4. Chiedi: «Usa lo strumento MCP `get_weather_mcp` per il meteo simulato di Roma».
   Approva la chiamata allo strumento se Copilot lo richiede.

Altri esempi: chiedi il meteo simulato di Venezia, oppure chiedi di chiamare lo
strumento con città Roma e `simulated_unavailable` impostato a `true`.

## Eseguire i test

Da PowerShell, aperto nella cartella del progetto:

```powershell
wsl ./.venv/bin/python -B -m unittest -v
```

Il server e l'ambiente `.venv` sono configurati per WSL/Linux. I test MCP avviano
un client di prova che dialoga con il server tramite il protocollo MCP, senza
effettuare chiamate meteo a Internet.
