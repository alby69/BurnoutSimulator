# BurnoutSimulator v3.0: Social Laboratory

Gioco di simulazione narrativa sulle dinamiche delle culture aziendali tossiche, attraverso la lente dell'antropologia organizzativa. Progetto accademico per tesina magistrale in HR — Sapienza Università di Roma.

La versione 3.0 introduce il **Social Laboratory**, un framework di agenti autonomi e meta-gameplay psicologico.

## Avvio rapido

```bash
pip install -r requirements.txt
python app.py          # Web UI su http://localhost:8080 (Modalità Laboratorio)
python main.py --cli   # CLI classica
```

## Novità v3.0: Social Laboratory

Il simulatore non è più solo un gioco single-player, ma un laboratorio di osservazione:

- **Agenti Autonomi**: 6 agenti con profili psicologici distinti (Il Performante, L'Idealista, Il Cinico, ecc.) giocano simultaneamente nel laboratorio.
- **Sistema di Possesso (Jump)**: L'utente umano può osservare lo sciame e "possedere" un agente in qualsiasi momento, prendendo il controllo delle sue decisioni.
- **Percorso Psicologico Emergente**: Il sistema traccia i "salti" dell'utente tra gli agenti, costruendo un profilo psicologico dell'osservatore basato sulle affinità elettive con i diversi archetipi.
- **Dashboard Analitica**: Visualizzazione in tempo reale di stress, energia e salute dello sciame, con grafici radar e tracciamento delle decisioni.

## Panoramica Caratteristiche

| Area | Dettaglio |
|---|---|
| **Framework Agenti** | 7 Profili psicologici basati su bias comportamentali |
| **Strategie adattamento** | COMPLIANCE, RESISTANCE, NEGOTIATION, ESCAPE |
| **Archetipi aziendali** | Startup Caotica, Corporate Tossica, Azienda Familiare, Consulting |
| **Finali** | 20+ (classici, fazioni, narrativi, ibridi) |
| **NPC & Fazioni** | Trust/Fear/Respect system; Fedelissimi, Gruppo Silenzioso, Ribelli |
| **Analytics** | Database SQLite per agenti, decisioni e traccia psicologica umana |
| **UI** | Glassmorphism, ECharts integration, responsive mobile, jump system |

## Struttura Progetto

```
burnout-simulator/
├── app.py                 ← Web UI (Social Laboratory & Game)
├── agents/                ← Framework agenti autonomi (v3.0)
│   ├── agent.py           ← Classe Agente
│   ├── personality.py     ← Profili psicologici
│   ├── swarm.py           ← Gestione dello sciame
│   └── memory.py          ← Memoria decisionale agenti
├── human/                 ← Layer giocatore umano (v3.0)
│   ├── human_player.py    ← Traccia psicologica e salti
├── game/                  ← Motore di gioco core (v2.0)
│   ├── engine.py          ← Logica narrativa e fasi carriera
│   └── data/events.json   ← Database eventi narrativi
├── database/              ← Persistenza dati
│   ├── agent_db.py        ← DB per agenti e laboratorio
│   └── analytics.py       ← DB per analytics di gioco
├── tests/                 ← Test suite (v3.0 baseline)
└── docs/                  ← Documentazione aggiuntiva
```

## Documentazione

| Documento | Contenuto |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Installazione locale, Docker, Deploy |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Evoluzione del progetto dalla v1.0 alla v3.0 |
| [docs/PIANO_GRAFICHE.md](docs/PIANO_GRAFICHE.md) | Asset grafici e mappature |

---

*Progetto realizzato per scopi accademici — Antropologia delle Organizzazioni, Sapienza Università di Roma.*
