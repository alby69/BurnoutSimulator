# BurnoutSimulator v3.5 — Social Physics & HR Intelligence

Gioco di simulazione narrativa sulle dinamiche delle culture aziendali tossiche, attraverso la lente dell'antropologia organizzativa. Progetto accademico per tesina magistrale in HR — Sapienza Università di Roma.

v3.5 introduce **Social Physics** (Peer Influence, Cultural Drift), **Dashboard Unificata** (AgentMonitor, AlertSystem, Reports, TimelineViewer), **Visualizzazione 3D Collins Cube** e **CI/CD pipeline**.

## Avvio rapido

```bash
pip install -r requirements.txt
python app.py          # Web UI su http://localhost:8080
# oppure
docker build -t burnout-sim . && docker run -d -p 8080:8080 burnout-sim
```

## Panoramica

| Componente | Stato |
|---|---|
| **Motore narrativo** (v2.0) | 31 eventi, 76 scelte, 4 archetipi aziendali, 15+ finali |
| **Framework agenti** (v3.2+) | 7 profili psicologici OCEAN+Dark Triad, Peer Influence, Cultural Drift |
| **DSS & Analytics** (v3.2) | Visualizzazione dinamica bio-diversità, HR DSS report, Top Performers |
| **Dashboard Intelligence** (v3.5) | AgentMonitor, AlertSystem, Reports (3 tipi), TimelineViewer |
| **Collins Cube 3D** (v3.5) | Scatter3D Stress/Energia/Integrità con rotazione automatica |
| **Jump System** (v3.0) | Possesso umano, salto tra agenti con filtro mood, profilo emergente |
| **CI/CD** (v3.5) | GitHub Actions: lint (ruff) + 182 test automatici |
| **Parametri HR** | Tossicità, Pressione, Coesione, Competizione, Supporto, Trasparenza |

## Modalità di gioco

**Classica** — Single-player narrativo: gestisci il tuo destino in un'azienda tossica.

**Laboratorio HR** — Decision Support System: lancia simulazioni multiple su uno sciame di 6 agenti. Osserva come la bio-diversità psicologica evolve in base ai parametri organizzativi. Peer influence e deriva culturale modificano i tratti OCEAN degli agenti in tempo reale.

## Novità v3.5

- **Peer Influence Avanzata**: gli agenti si influenzano reciprocamente i tratti OCEAN basati su prossimità di fazioni e stress
- **Pressione Culturale Dinamica**: l'archetipo aziendale evolve in base alla media OCEAN/Dark Triad degli agenti, modificando i parametri HR ogni 5 turni
- **Dashboard Unificata**: 4 moduli — AgentMonitor (risk ranking), AlertSystem (soglie critiche), Reports (HR DSS + turnover risk), TimelineViewer
- **Collins Cube 3D**: visualizzazione ECharts scatter3D degli agenti nello spazio Stress/Energia/Integrità
- **CI/CD**: GitHub Actions con lint (ruff) e 182 test (pytest)

## Bug Fix Recenti

- **Agente non selezionabile nel laboratorio**: causa era `ui.context.client.id` non stabile dopo `ui.navigate.to("/")`. Fix: stato globale `inspected_agent_id` invece di dict per-client
- **Typewriter troppo lento**: `_reading_speed` ridotto da 50ms a 15ms per carattere. Timer scelta ora aspetta la fine della typewriter prima di partire
- **File eventi mancante**: `GameEngine.__init__` ora cattura `FileNotFoundError` e gestisce graceful degradation
- **Statistiche non clampate**: `check_conditions()` ora clampa tutti gli attributi a [0, 100]

## Struttura Progetto

```
burnout-simulator/
├── app.py                    ← Web UI NiceGUI (classica + laboratorio)
├── main.py                   ← CLI + Tkinter entry point
├── agents/                   ← Framework agenti autonomi
│   ├── agent.py              ← Agente con possesso, auto-play, choice probabilities
│   ├── personality.py        ← 7 profili OCEAN+Dark Triad, peer influence buffer
│   ├── swarm.py              ← Coordinatore sciame, cultural drift, peer influence
│   └── memory.py             ← Memoria decisionale e apprendimento
├── human/
│   └── human_player.py       ← Traccia salti e profilo emergente
├── game/                     ← Motore di gioco core
│   ├── engine.py             ← Logica narrativa, fasi carriera, eventi soglia, varianti
│   ├── player.py             ← Player, NPC, fazioni, achievement, tag comportamentali
│   ├── events.py             ← EventManager, Choice, varianti A/B
│   ├── graph.py              ← Grafo decisionale (ECharts force-directed)
│   ├── logic.py              ← Determinazione finale (15 tipi)
│   ├── save_manager.py       ← Persistenza sessioni JSON
│   └── data/events.json      ← 31 eventi narrativi con 76 scelte
├── engine/                   ← Motore psicologico
│   ├── analysis.py           ← StrategicAnalyzer (analisi strategica agenti)
│   └── psych_engine.py       ← PsychometricEngine modulatore statistiche
├── dashboard/                ← Dashboard Intelligence v3.5
│   └── main_dashboard.py     ← AgentMonitor, AlertSystem, Reports, TimelineViewer, MainDashboard
├── database/                 ← Persistenza SQLite
│   ├── agent_db.py           ← DB agenti, decisioni, salti, profili
│   └── analytics.py          ← DB analytics partite classiche
├── ui/                       ← Interfaccia NiceGUI
│   ├── theme.py              ← Tema scuro, gradienti, animazioni CSS
│   ├── components/           ← Componenti riutilizzabili (metric_card, npc_portrait, etc.)
│   └── pages/                ← Pagine: start, game, laboratory, game_over, analytics, editor
├── static/images/            ← Asset grafici
│   ├── personaggi/           ← 22 ritratti NPC PNG
│   ├── eventi/               ← 12 icone eventi
│   └── stati/                ← 5 icone stati burnout
├── tests/
│   ├── test_comprehensive.py ← 140 test unificati (engine, player, swarm, agenti, UI)
│   ├── test_v3_5.py          ← 31 test v3.5 (peer influence, cultural drift, dashboard, cube)
│   └── test_engine.py        ← 5 test ending resolver
│   └── test_agents.py        ← 4 test framework agenti
│   └── test_jump_penalty.py  ← 1 test penalità salto
│   └── test_analytics.py     ← 1 test flusso analytics
│   └── verify_v3_1.py        ← Verifica integrazione v3.1
├── docs/                     ← Documentazione
│   ├── ROADMAP.md            ← Evoluzione completa v1.0 → v3.5+
│   └── technical/            ← Guide tecniche
│   └── anthropological/      ← Documenti antropologici
└── .github/workflows/test.yml ← CI/CD pipeline
```

## Documentazione

| Documento | Contenuto |
|---|---|
| [docs/technical/INSTALL.md](docs/technical/INSTALL.md) | Installazione locale, Docker, deploy cloud |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Evoluzione completa v1.0 → v3.5 |
| [docs/technical/JUMP_SYSTEM.md](docs/technical/JUMP_SYSTEM.md) | Architettura del sistema di possesso |
| [docs/technical/hr_dss.md](docs/technical/hr_dss.md) | HR Decision Support System |
| [docs/technical/PIANO_GRAFICHE.md](docs/technical/PIANO_GRAFICHE.md) | Mappa asset grafici |
| [docs/anthropological/*.md](docs/anthropological/) | Analisi antropologica, posizione politica, validazione scientifica |

## Testing

```bash
# Tutti i test
python -m pytest tests/ -v

# Solo test specifici
python -m pytest tests/test_v3_5.py -v
python -m pytest tests/test_comprehensive.py -v

# Verifica integrazione
PYTHONPATH=. python tests/verify_v3_1.py
```

182 test totali (140 unificati + 31 v3.5 + 11 legacy).

## Tech Stack

- **Python 3.12** — 100% del codice
- **NiceGUI 3.14** — Web UI reattiva (ECharts, Material Icons, CSS glassmorphism)
- **SQLite3** — Persistenza (2 database indipendenti)
- **Docker** — python:3.12-slim, deploy su Render/VPS
- **GitHub Actions** — CI/CD con ruff + pytest
- **Google Fonts** — Inter (UI), JetBrains Mono (dati)

## Metodologia Antropologica

BurnoutSimulator adotta un approccio di **osservazione partecipante digitale**. Attraverso il *Jump System*, il ricercatore (l'utente HR) può immergersi nella soggettività degli agenti simulati, superando la barriera dei dati puramente quantitativi per comprendere il "senso" delle scelte in un contesto di costrizione.

Il framework teorico si basa sulla critica delle culture del *presentismo* e sulla de-mitizzazione della missione aziendale, trattando il profitto come dato di contesto e il benessere come metrica suprema.

---

*Progetto realizzato per scopi accademici — Antropologia delle Organizzazioni, Sapienza Università di Roma.*
