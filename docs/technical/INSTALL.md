# Installazione

## Requisiti

- Python 3.10 o superiore
- pip
- Connessione internet (per font Inter e JetBrains Mono via Google Fonts)

## Installazione locale

### 1. Clona il repository

```bash
git clone https://github.com/tuo-username/burnout-simulator.git
cd burnout-simulator
```

### 2. Crea un ambiente virtuale (consigliato)

```bash
python3 -m venv venv
source venv/bin/activate      # Linux / macOS
# oppure
venv\Scripts\activate         # Windows
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Avvia

**Web UI (consigliata):**
```bash
python app.py
```
Apri il browser su [http://localhost:8080](http://localhost:8080)

**CLI (terminale):**
```bash
python main.py --cli
```

---

## Installazione con Docker

### Prerequisiti
- Docker installato

### Build e avvio

```bash
docker build -t burnout-sim .
docker run -p 8080:8080 burnout-sim
```

Apri [http://localhost:8080](http://localhost:8080)

Per avviare in background:
```bash
docker run -d -p 8080:8080 --name burnout-sim burnout-sim
```

Per fermare:
```bash
docker stop burnout-sim
```

---

## Deploy su Render (cloud gratuito)

1. Fai push del repository su GitHub
2. Vai su [Render](https://render.com) e clicca **New +** → **Web Service**
3. Connetti il repository GitHub
4. Imposta:
   - **Name**: `burnout-simulator`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Clicca **Create Web Service**

Render assegna un URL pubblico (es. `https://burnout-simulator.onrender.com`).

---

## Deploy su VPS

### Con Nginx (esempio)

```nginx
server {
    listen 80;
    server_name burnout-sim.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Avvia l'app:
```bash
python app.py
```

---

## Modalità di avvio

| Comando | Descrizione |
|---------|-------------|
| `python app.py` | Web UI su porta 8080 (NiceGUI) — modalità classica + laboratorio |
| `python main.py --cli` | Interfaccia testuale (solo classica) |
| `python main.py` | Tkinter GUI (fallback su CLI) |

---

## Prima esecuzione — Modalità Classica

1. Inserisci il tuo nome
2. Scegli l'archetipo aziendale:
   - **Startup Caotica** — overwork, ritmi frenetici (Manager: Micromanager Iperattivo)
   - **Corporate Tossica** — politica interna, micromanagement (Manager: Narcisista Burocratico)
   - **Azienda Familiare** — nepotismo, favoritismi (Manager: Padre/Padrone Paternalista)
   - **Consulting** — KPI ossessivi, reperibilità continua (Manager: Perfezionista Senza Tregua)
3. Leggi gli scenari e scegli come reagire (15 secondi per le scelte critiche!)
4. Ogni NPC ha un ritratto PNG con stato emotivo calcolato da trust/fear/stress
5. Le fazioni (Fedelissimi, Gruppo Silenzioso, Ribelli) influenzano gli NPC e i finali
6. Al termine visualizzerai il report finale con profilo comportamentale, grafico stress/tempo, radar, achievement

## Prima esecuzione — Social Laboratory

1. Clicca "ENTRA NEL LABORATORIO" nella schermata iniziale
2. Osserva 6 agenti autonomi con profili psicologici distinti (7 profili OCEAN+Dark Triad)
3. Clicca "POSSIEDI" su un agente per prenderne il controllo
4. Usa "SALTA" per cambiare agente in qualsiasi momento (il sistema traccia il tuo profilo emergente)
5. Clicca "Avanti N turni" per far avanzare gli agenti non posseduti
6. La **Peer Influence** modifica i tratti OCEAN degli agenti in base alla prossimità sociale
7. La **Cultural Drift** evolve l'archetipo aziendale dominante ogni 5 turni
8. Il **Collins Cube 3D** mostra gli agenti nello spazio Stress/Energia/Integrità

---

## Testing

```bash
# Tutti i test (182 totali)
python -m pytest tests/ -v

# Test v3.5 (Peer Influence, Cultural Drift, Dashboard, Collins Cube)
python -m pytest tests/test_v3_5.py -v

# Test completi unificati (engine, player, swarm, agenti)
python -m pytest tests/test_comprehensive.py -v

# Test legacy
python -m unittest tests/test_agents.py
python -m pytest tests/test_engine.py

# Verifica integrazione v3.1 (agenti, possesso, DB)
PYTHONPATH=. python tests/verify_v3_1.py

# Test E2E con Playwright (richiede app in esecuzione su :8080)
python verify_lab.py
```

## Dati e analytics

Due database SQLite indipendenti:

| Database | Contenuto |
|----------|-----------|
| `database/analytics.db` | Partite classiche: scelte, finali, tempi decisione |
| `database/agents.db` | Laboratorio: agenti, decisioni, salti umani, profili |

Per esplorare:
```bash
sqlite3 database/analytics.db
.tables
SELECT * FROM choice_stats;
```

La dashboard analytics è accessibile dal pulsante "📊 Analytics" nella schermata iniziale e mostra:
- Finali più ottenuti (con barre)
- Distribuzione scelte per categoria
- Sopravvivenza media per archetipo
- Ultime 10 partite giocate

---

## Note tecniche

- **Font**: Inter (UI) e JetBrains Mono (dati) caricati da Google Fonts — richiedono internet alla prima visita. Se offline, NiceGUI usa i fallback di sistema.
- **Dipendenze**: solo `nicegui≥1.4.0` — tutto il resto è libreria standard Python
- **Collaudo**: `docker build -t burnout-sim . && docker run -d -p 8080:8080 burnout-sim && curl http://localhost:8080` deve restituire HTTP 200.
