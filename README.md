# BurnoutSimulator v3.1 — Social Laboratory

Gioco di simulazione narrativa sulle dinamiche delle culture aziendali tossiche, attraverso la lente dell'antropologia organizzativa. Progetto accademico per tesina magistrale in HR — Sapienza Università di Roma.

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
| **Framework agenti** (v3.0) | 7 profili psicologici OCEAN+Dark Triad, 6 agenti autonomi |
| **Jump System** (v3.0) | Possesso umano, salto tra agenti, profilo psicologico emergente |
| **Grafica** | 22 PNG personaggi, 12 icone eventi, 5 icone stati, CSS glassmorphism |
| **Extra** | 12 achievement, 7 eventi soglia, 15 mini-eventi, 5 fasi carriera, finali incrociati |

## Modalità di gioco

**Classica** — Single-player narrativo: scegli il tuo archetipo aziendale, affronta eventi, gestisci statistiche (energia, stress, salute, integrità, autostima, occupabilità, reputazione), interagisci con 4 NPC (Marco, Giulia, Roberto, Elena) e 3 fazioni, scopri uno dei 15+ finali.

**Laboratorio** — Multi-agente: 6 agenti con profili psicologici distinti giocano simultaneamente. Osserva, possiedi un agente, salta tra prospettive. Il sistema traccia il tuo profilo psicologico emergente in base alle affinità con gli archetipi.

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
| [docs/INSTALL.md](docs/INSTALL.md) | Installazione locale, Docker, deploy |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Evoluzione completa v1.0 → v3.1 |
| [docs/JUMP_SYSTEM.md](docs/JUMP_SYSTEM.md) | Architettura del sistema di possesso |
| [docs/PIANO_GRAFICHE.md](docs/PIANO_GRAFICHE.md) | Asset grafici e mappature |

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
