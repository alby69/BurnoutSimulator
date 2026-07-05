# BurnoutSimulator v3.2 — HR Strategic Laboratory

Gioco di simulazione narrativa sulle dinamiche delle culture aziendali tossiche, attraverso la lente dell'antropologia organizzativa. Progetto accademico per tesina magistrale in HR — Sapienza Università di Roma.

Il simulatore v3.2 introduce un **Decision Support System (DSS)** avanzato per l'analisi del rischio burnout sistemico attraverso lo studio dell'evoluzione dello sciame di agenti.

## Avvio rapido

```bash
pip install -r requirements.txt
python app.py          # Web UI su http://localhost:8080
python main.py --cli   # CLI classica
```

## Panoramica

| Componente | Stato |
|---|---|
| **Motore narrativo** (v2.0) | 31 eventi, 76 scelte, 4 archetipi aziendali, 15+ finali |
| **Framework agenti** (v3.2) | 7 profili psicologici, Peer Influence, Trait Evolution |
| **DSS & Analytics** (v3.2) | Visualizzazione dinamica bio-diversità, Report dettagliato, Top Performers |
| **Jump System** (v3.0) | Possesso umano, salto tra agenti con filtro mood |
| **Grafica** | Dashboard espressiva, CSS glassmorphism, ECharts avanzati |
| **Parametri HR** | Tossicità, Pressione, Coesione, Competizione, Supporto, Trasparenza |

## Modalità di gioco

**Classica** — Single-player narrativo: gestisci il tuo destino in un'azienda tossica.

**Laboratorio HR** — Decision Support System: lancia simulazioni multiple simultanee su uno sciame di agenti. Osserva come la bio-diversità psicologica (profili OCEAN) evolve in base ai parametri organizzativi impostati. Identifica i "Top Performers" e analizza i report decisionali raggruppati per tipologia per trarre insight strategici.

## Struttura Progetto

```
burnout-simulator/
├── app.py                    ← Web UI NiceGUI (classica + laboratorio)
├── main.py                   ← CLI + Tkinter entry point
├── agents/                   ← Framework agenti autonomi
│   ├── agent.py              ← Agente con possesso e auto-play
│   ├── personality.py        ← 7 profili psicologici (OCEAN+Dark Triad)
│   ├── swarm.py              ← Coordinatore sciame
│   └── memory.py             ← Memoria decisionale e apprendimento
├── human/
│   └── human_player.py       ← Traccia salti e profilo emergente
├── game/                     ← Motore di gioco core
│   ├── engine.py             ← Logica narrativa, fasi carriera, eventi soglia
│   ├── player.py             ← Player, NPC, fazioni, achievement
│   ├── events.py             ← EventManager, Choice
│   ├── graph.py              ← Grafo decisionale (ECharts force-directed)
│   ├── save_manager.py       ← Persistenza sessioni JSON
│   └── data/events.json      ← 31 eventi narrativi con 76 scelte
├── engine/                   ← Motore psicologico
│   ├── psych_engine.py       ← PsychometricEngine modulatore statistiche
│   └── data/keywords_ontology.json
├── database/                 ← Persistenza SQLite
│   ├── agent_db.py           ← DB agenti, decisioni, salti, profili
│   └── analytics.py          ← DB analytics partite classiche
├── dashboard/                ← Stub per dashboard avanzate
├── static/images/            ← Asset grafici
│   ├── personaggi/           ← 22 ritratti NPC PNG
│   ├── eventi/               ← 12 icone eventi
│   └── stati/                ← 5 icone stati burnout
├── tests/
│   ├── test_agents.py        ← Unit test framework agenti
│   └── verify_v3_1.py        ← Verifica integrazione v3.1
├── verification/             ← Screenshot E2E (Playwright)
├── docs/                     ← Documentazione
└── assets/                   ← (vuoto)
```

## Documentazione

| Documento | Contenuto |
|---|---|
| Documento | Contenuto |
|---|---|
| [docs/technical/INSTALL.md](docs/technical/INSTALL.md) | Installazione locale, Docker, deploy |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Evoluzione completa v1.0 → v3.2 |
| [docs/technical/JUMP_SYSTEM.md](docs/technical/JUMP_SYSTEM.md) | Architettura del sistema di possesso |
| [docs/anthropological/osservazione_partecipante.md](docs/anthropological/osservazione_partecipante.md) | Taglio divulgativo/antropologico sul sistema |

## Testing

```bash
python tests/test_agents.py     # Unit test
python tests/verify_v3_1.py     # Verifica integrazione
python verify_lab.py            # E2E (richiede app in esecuzione + Playwright)
```

## Tech Stack

- **Python 3.12** — 100% del codice
- **NiceGUI ≥ 1.4.0** — Web UI reattiva (ECharts, Material Icons, responsive)
- **SQLite3** — Persistenza (2 database indipendenti)
- **Docker** — python:3.12-slim, deploy su Render/VPS
- **Google Fonts** — Inter (UI), JetBrains Mono (dati)

---

*Progetto realizzato per scopi accademici — Antropologia delle Organizzazioni, Sapienza Università di Roma.*
