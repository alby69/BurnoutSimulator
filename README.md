# BurnoutSimulator

Gioco di simulazione narrativa a scelte multiplesulle dinamiche delle culture aziendali tossiche, attraverso la lente dell'antropologia organizzativa. Progetto accademico per tesina magistrale in HR — Sapienza Università di Roma.

## Avvio rapido

```bash
pip install nicegui
python app.py          # Web UI su http://localhost:8080
python main.py --cli   # CLI alternativa
```

## Panoramica

| Caratteristica | Dettaglio |
|---|---|
| **Piattaforme** | Web UI (NiceGUI), CLI |
| **Categorie tossicità** | Micromanagement, mobbing, favoritismo, burnout, scapegoating |
| **Strategie adattamento** | COMPLIANCE, RESISTANCE, NEGOTIATION, ESCAPE |
| **Finali** | 20+ (classici, fazioni, narrativi, ibridi) |
| **Archetipi aziendali** | Startup Caotica, Corporate Tossica, Azienda Familiare, Consulting |
| **Personalità manager** | Micromanager Iperattivo, Narcisista Burocratico, Padre/Padrone Paternalista, Perfezionista Senza Tregua |
| **NPC** | 4 (Marco, Giulia, Roberto, Elena) con ritratti dinamici PNG |
| **Fazioni** | Fedelissimi, Gruppo Silenzioso, Ribelli |
| **Tracciamento** | SQLite analytics, grafo decisionale, tempo decisione, achievement |
| **Grafica** | VN glassmorphism, ritratti PNG, icone eventi/stati, emote overlay |

## Struttura

```
burnout-simulator/
├── app.py                 ← Web UI (~2200 righe)
├── main.py                ← CLI / Tkinter entry point
├── requirements.txt       ← Dipendenze
├── Dockerfile             ← Container
├── docs/                  ← Documentazione
│   ├── INSTALL.md         ← Installazione dettagliata
│   ├── ROADMAP.md         ← Roadmap completa (23 milestone)
│   └── PIANO_GRAFICHE.md  ← Asset grafici e mappature
├── game/
│   ├── engine.py          ← Motore di gioco (eventi, fazioni, NPC, fasi carriera)
│   ├── player.py          ← Player + NPC dataclass
│   ├── events.py          ← Event/Choice dataclass + EventManager
│   ├── graph.py           ← Grafo decisionale
│   ├── save_manager.py    ← Salvataggio sessioni
│   └── data/events.json   ← 31 eventi narrativi
├── database/
│   └── analytics.py       ← SQLite: sessioni, scelte, tag
├── static/images/         ← 39 PNG (personaggi, eventi, stati)
│
├── agents/                ← [v3.0] Framework agenti autonomi
├── api/                   ← [v3.0] FastAPI backend
├── engine/                ← [v3.0] Motore psicometrico
├── ml/                    ← [v3.0] ML federato
├── mesh/                  ← [v3.0] P2P mesh networking
├── reflex_app/            ← [v3.0] Porting Reflex
└── tests/                 ← [v3.0] Test suite
```

## Documentazione

| Documento | Contenuto |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Installazione locale, Docker, Render, VPS |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 23 milestone completati (M1-M12, E1-E8, F1-F3) |
| [docs/PIANO_GRAFICHE.md](docs/PIANO_GRAFICHE.md) | Asset grafici, mappature emote/eventi/stati |

## Deploy

```bash
docker build -t burnout-sim . && docker run -p 8080:8080 burnout-sim
```

---

*Progetto realizzato per scopi accademici — Antropologia delle Organizzazioni, Sapienza Università di Roma.*
