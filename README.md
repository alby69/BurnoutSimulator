# BurnoutSimulator

**BurnoutSimulator** è un gioco di simulazione narrativa a scelte multiple che esplora le dinamiche delle culture aziendali tossiche attraverso la lente dell'antropologia organizzativa.

Progetto concepito come strumento didattico e di ricerca per una tesina magistrale in HR presso l'Università Sapienza di Roma.

## Concept

Il gioco mette il giocatore nei panni di un neoassunto in un'azienda tossica. Ogni decisione influenza parametri psicologici e sociali (stress, energia, integrità, relazioni) portando a finali diversi.

**Categorie di tossicità esplorate:**
- Cultura aziendale problematica, gestione inadeguata, work-life balance, problemi etici, comunicazione carente

**Strategie di adattamento:**
- **COMPLIANCE** — Conformismo/Adattamento passivo
- **RESISTANCE** — Resistenza attiva/Dissenso
- **NEGOTIATION** — Negoziazione/Mediazione
- **ESCAPE** — Fuga/Ricerca di alternative

## Piattaforme

| Modalità | Comando | Descrizione |
|----------|---------|-------------|
| **Web UI** | `python app.py` | Interfaccia web responsive (desktop + mobile) con NiceGUI |
| **CLI** | `python main.py --cli` | Versione testuale per terminale |

La web UI è l'interfaccia principale: funziona in qualsiasi browser senza installazione client.

## Screenshot (web UI)

```
┌─────────────────────────────────────────────┐
│ Giorno 5  [Corporate Tossica]          [✕]  │
├───────────────────┬─────────────────────────┤
│ ⚡ Energia    45%  │ RIUNIONE INUTILE         │
│ 🔥 Stress    72%  │                         │
│ ❤️ Salute    68%  │ Sono le 18:05. Ricevi    │
│ 🛡 Integrità  50%  │ un invito urgente per    │
│ ⭐ Autostima  40%  │ una riunione...          │
│ 💼 Occupab.   55%  │                         │
│ 📊 Rep. Man.  42%  │ Cosa fai?               │
│ 🤝 Rep. Team  58%  │                         │
│                    │ A) Partecipi senza fare  │
│ FAZIONI            │    domande               │
│ Fedelissimi: 10%   │ B) Chiedi di rimandare   │
│ Gruppo Sil.: 50%   │ C) Camera spenta,        │
│ Ribelli: 30%       │    lavori ad altro       │
│                    │                         │
│ RELAZIONI          │                         │
│ Marco: T42 R30 F20 │                         │
└───────────────────┴─────────────────────────┘
```

## Caratteristiche Tecniche

- **Motore narrativo**: Python con sistema di eventi branching e scelte ponderate
- **Tracciamento decisioni**: grafo pesato per analisi statistica delle scelte
- **Profilazione finale**: profilo comportamentale basato su tag accumulati
- **Analytics**: database SQLite con ogni scelta salvata (stats pre/post)
- **8 finali**: ogni partita produce un ending diverso in base alle scelte
- **4 archetipi aziendali**: Startup Caotica, Corporate Tossica, Azienda Familiare, Consulting
- **Web UI responsive**: NiceGUI — stessa codebase per desktop e mobile

## Struttura del Progetto

```
burnout-simulator/
├── app.py                 ← Web UI (NiceGUI)
├── main.py                ← CLI / legacy entry point
├── requirements.txt       ← Dipendenze
├── Dockerfile             ← Deploy containerizzato
├── game/
│   ├── engine.py          ← Motore di gioco centrale
│   ├── player.py          ← Stato giocatore e NPC
│   ├── events.py          ← Gestione scenari JSON
│   ├── graph.py           ← Grafo decisionale
│   ├── save_manager.py    ← Salvataggio sessioni
│   └── data/events.json   ← Database eventi
├── database/
│   ├── analytics.py       ← Tracciamento scelte (SQLite)
│   └── analytics.db       ← Dati raccolti (generato)
└── assets/                ← Avatar, icone (futuro)
```

## Deploy

### Render (cloud, gratuito)
1. Push su GitHub
2. Connetti repo a [Render](https://render.com)
3. Imposta: `Start Command` → `python app.py`
4. Deploy automatico

### Docker
```bash
docker build -t burnout-sim .
docker run -p 8080:8080 burnout-sim
```

### VPS
```bash
python app.py
# dietro nginx reverse proxy sulla porta 8080
```

## Sviluppi futuri

- **Reflex**: migrazione a piattaforma completa con login utenti, classifiche, statistiche aggregate, salvataggi cloud
- **Avatar**: immagini profilo per ogni NPC
- **Espansione scenari**: nuovi eventi e chain narrative

---
*Progetto realizzato per scopi accademici — Tesina di Antropologia delle Organizzazioni.*
