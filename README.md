# BurnoutSimulator

**BurnoutSimulator** è un gioco di simulazione narrativa a scelte multiple che esplora le dinamiche delle culture aziendali tossiche attraverso la lente dell'antropologia organizzativa.

Progetto concepito come strumento didattico e di ricerca per una tesina magistrale in HR presso l'Università Sapienza di Roma.

## Concept

Il gioco mette il giocatore nei panni di un neoassunto in un'azienda tossica. Ogni decisione influenza parametri psicologici e sociali (stress, energia, integrità, relazioni) portando a finali diversi.

**Categorie di tossicità esplorate:**
- Micromanagement, mobbing, favoritismo, burnout, scapegoating

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

## Caratteristiche Tecniche

- **Motore narrativo**: Python con sistema di eventi branching e scelte ponderate
- **Tracciamento decisioni**: grafo pesato per analisi statistica delle scelte
- **Profilazione finale**: profilo comportamentale basato su tag accumulati
- **Analytics**: database SQLite con ogni scelta salvata (stats pre/post)
- **20+ finali**: ogni partita produce un ending diverso in base a fazioni, archetipo, profilo
- **4 archetipi aziendali**: Startup Caotica, Corporate Tossica, Azienda Familiare, Consulting
- **Manager con personalità**: Micromanager, Narcisista, Paternalista, Perfezionista
- **Web UI responsive**: NiceGUI — stessa codebase per desktop e mobile
- **Grafica VN**: layout Visual Novel con ritratti NPC animati (SVG inline), tema dinamico per archetipo, gradiente

### Overhaul grafico (2026)

| Fase | Descrizione | Stato |
|------|-------------|-------|
| **F1 — CSS Overhaul** | Gradiente background, card stile VN (`event-card`, `vn-card`), font Inter + JetBrains Mono, scrollbar personalizzata, pulsazioni, responsive raffinato | ✅ |
| **F2 — Facce SVG dinamiche** | 6 espressioni (neutral/happy/worried/angry/stressed/scared) calcolate da trust/fear/stress, sostituiti avatar testuali | ✅ |
| **F3 — Layout Visual Novel** | Ritratto NPC 64px + nome a fianco della card narrativa, NPC ruota per turno, scelte stile dialog VN | ✅ |

## Struttura del Progetto

```
burnout-simulator/
├── app.py                 ← Web UI (NiceGUI) — ~1300 righe
├── main.py                ← CLI / legacy entry point
├── requirements.txt       ← Dipendenze
├── Dockerfile             ← Deploy containerizzato
├── ROADMAP.md             ← Roadmap completo
├── INSTALL.md             ← Guida installazione
├── game/
│   ├── engine.py          ← Motore di gioco centrale (mini-eventi, fasi carriera, soglie)
│   ├── player.py          ← Stato giocatore e NPC, achievement
│   ├── events.py          ← Gestione scenari JSON (Choice con consequences)
│   ├── graph.py           ← Grafo decisionale
│   ├── save_manager.py    ← Salvataggio sessioni
│   └── data/events.json   ← 31 eventi narrativi
├── database/
│   ├── analytics.py       ← Tracciamento scelte (SQLite)
│   └── analytics.db       ← Dati raccolti (generato)
└── assets/                ← Avatar, icone (futuro)
```

## Finali disponibili (20+)

### Classici (4)
- **Burnout** — stress > 90
- **Licenziamento** — manager_rep < 10
- **Dimissioni** — integrity + autostima + energy < 60 cumulativo
- **Sopravvissuto** — 60+ giorni

### Basati su fazioni (4)
- **Il Whistleblower** — Ribelli > 70 + integrity > 60
- **Il Braccio Destro** — Fedelissimi > 70 + manager_rep > 80
- **Lo Spettatore** — Gruppo Silenzioso > 70
- **Il Camaleonte** — tutte le fazioni > 50

### Narrativi differiti (5)
- **Il Respingente Umano** — collega_ringrazia triggerato
- **Il Record** — richiamo_formale triggerato
- **L'Ascesa** — progetto_premio triggerato
- **La Nuova Via** — burnout_startup triggerato
- **L'Eredità** — passaggio_generazionale triggerato

### Extra (5, E5)
- **Il Fondatore Esaurito** — Startup + burnout_risk
- **La Pecora Nera** — Familiare + truth_teller
- **L'Ingranaggio Perfetto** — Consulting + yes_man
- **Il Resistente** — energia bassa + longevità
- **L'Indomabile** — autostima alta

### Manager personality (5, E5)
Incroci archetipo + profilo comportamentale per finali ibridi ulteriori.

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
- **Avatar**: immagini profilo per ogni NPC (vs SVG inline)
- **Espansione scenari**: nuovi eventi e chain narrative
- **Sonoro**: effetti audio per eventi critici

---
*Progetto realizzato per scopi accademici — Tesina di Antropologia delle Organizzazioni.*
