# Roadmap — BurnoutSimulator

## Stato attuale

**Tutti i 23 miglioramenti pianificati (M1-M12 + E1-E8 + F1-F3) sono implementati.**
**Tutte le 6 fasi del Social Laboratory (L1-L6) sono implementate.**

---

## v2.0 — Core Game (Completato)

### M1-M12: Miglioramenti narrativi e UI

| # | Miglioramento | Impatto | Sforzo |
|---|---------------|---------|--------|
| M1 | Feedback effetti dopo la scelta (dialog con delta colorati) | Alto | Basso |
| M2 | Fazioni influenzano NPC (sync automatico dopo ogni scelta) | Alto | Medio |
| M3 | Tooltip anteprima effetti al passaggio mouse | Medio | Basso |
| M4 | Conseguenze narrative differite (eventi triggerati N turni dopo) | Alto | Alto |
| M5 | Finali basati sulle fazioni (Il Whistleblower, Il Braccio Destro, Lo Spettatore, Il Camaleonte) | Alto | Medio |
| M6 | Storico scelte visibile in sidebar con pallini colorati | Medio | Basso |
| M7 | Grafo decisionale interattivo ECharts force-directed | Basso | Alto |
| M8 | Mini-eventi giornalieri (15 scenari di routine) | Alto | Medio |
| M9 | Dashboard analytics globale (finali, categorie, sopravvivenza) | Medio | Medio |
| M10 | Mobile responsive (sidebar toggle, breakpoint <768px) | Medio | Basso |
| M11 | Tutorial interattivo a 5 step onboarding | Alto | Medio |
| M12 | Timer 15s su scelte critiche con auto-click | Medio | Basso |

### E1-E8: Extra post-roadmap

| # | Miglioramento | Impatto | Sforzo |
|---|---------------|---------|--------|
| E1 | Personalità Manager per archetipo (Micromanager, Narcisista, Paternalista, Perfezionista) | Alto | Medio |
| E2 | 7 eventi su soglia (stress>80, energia<20, salute<25, autostima<20, rep<20, fazioni>70) | Alto | Basso |
| E3 | Grafico stress/tempo ECharts nel report finale | Alto | Basso |
| E4 | 5 fasi carriera (Prova → Primo Progetto → Operativa → Ristrutturazione → Sopravvivenza) | Medio | Basso |
| E5 | 5 finali incrociati archetipo+profilo (Fondatore Esaurito, Pecora Nera, Ingrassaggio Perfetto, Resistente, Indomabile) | Alto | Medio |
| E6 | Tracking tempo di decisione per scelta (ms, media, rapide/lente) | Medio | Basso |
| E7 | 12 achievement (Sempre Disponibile, Zerbino Ufficiale, Vivere al Limite, Senza Filtro, Muro di Berlino, ecc.) | Basso | Basso |
| E8 | Modalità "Casi Reali" (badge sugli eventi) | Basso | Basso |

### F1-F3: Overhaul grafico

| # | Fase | Descrizione |
|---|------|-------------|
| F1 | CSS Overhaul | Background gradiente, card VN con bordo accentato, palette per archetipo, font Inter+JetBrains Mono, scrollbar personalizzata |
| F2 | Facce SVG dinamiche (poi sostituite da PNG in F4) | 6 espressioni (neutral/happy/worried/angry/stressed/scared) |
| F3 | Layout Visual Novel | Ritratto NPC 64px + nome affiancato alla card, scelte stile VN |

### Asset grafici aggiuntivi (post-F3)

| # | Fase | Descrizione |
|---|------|-------------|
| F4 | PNG portraits → 22 immagini CORP_* in `static/images/personaggi/` |
| F5 | 12 icone eventi mappate per ID evento in `static/images/eventi/` |
| F6 | 5 icone stati burnout in `static/images/stati/` |
| F7 | 4 emote per categoria scelta (COMPLIANCE, RESISTANCE, NEGOTIATION, ESCAPE) |
| F8 | Label effetti in italiano (EFFECT_LABELS mapping) |
| F9 | Help system integrato (dialog esplicativo 7 sezioni) |

---

## v3.2 — HR Strategic Laboratory (In Corso)

| # | Componente | Descrizione | Stato |
|---|------------|-------------|-------|
| L7 | HR Parameters Input | Interfaccia per definire Tossicità, Pressione, Coesione e Competizione | Completato |
| L8 | Trait Evolution | Evoluzione dinamica di OCEAN tratti basata su scelte ed esiti | Completato |
| L9 | Social Capital System | Bonus/Malus stress basati sull'integrazione nelle fazioni | Completato |
| L10 | HR Anonymous Mode | Refactoring UI per analisi anonima e orientata ai dati DSS | Completato |
| L11 | Predictive Analytics | Espansione dashboard con visualizzazione dinamica evoluzione profili | Completato |
| L12 | Policy Simulation | Lancio simulazioni multiple contemporanee (A/B Testing massivo) | Completato |

---

## v3.0 — Social Laboratory (Completato)

| # | Componente | Descrizione |
|---|------------|-------------|
| L1 | Core Agent Framework | 7 archetipi psicologici con OCEAN+Dark Triad (Big Five + Machiavellismo, Narcisismo, Psicopatia) |
| L2 | Autonomous Swarm | 6 agenti indipendenti con GameEngine separato e decisioni pesate |
| L3 | Human Jump System | Possesso agenti, salto tra prospettive, rilascio, storico salti |
| L4 | Observer Analytics | Profilo psicologico emergente dell'umano (categorie, pattern, durata) |
| L5 | Lab UI Overhaul | Vista 3 colonne, radar chart ECharts, emotional weather, swarm stats, jump dialog |
| L6 | Agent Persistence | Schema DB esteso (`agents.db`) per agenti, decisioni, salti, profilo umano |

### Profili psicologici implementati

| Profilo | COMPLIANCE | RESISTANCE | NEGOTIATION | ESCAPE | Tratti distintivi |
|---------|:----------:|:----------:|:-----------:|:-----:|-------------------|
| Il Performante | 70 | 20 | 60 | 10 | Narcisismo alto, Coscienziosità alta |
| Il Protettore | 20 | 70 | 50 | 30 | Gradevolezza alta, Psicopatia bassa |
| Il Sopravvissuto | 20 | 40 | 30 | 70 | Neuroticismo alto, Apertura bassa |
| Il Negoziatore | 40 | 20 | 80 | 30 | Gradevolezza alta, Estroversione media |
| Il Cinico | 10 | 60 | 20 | 60 | Psicopatia alta, Gradevolezza bassa |
| Il Manipolatore | 50 | 30 | 70 | 20 | Machiavellismo alto, Coscienziosità media |
| L'Idealista | 20 | 80 | 40 | 20 | Apertura alta, Neuroticismo basso |

### Jump System

- **Possesso**: l'umano prende il controllo di un agente, le sue scelte vengono tracciate separatamente
- **Salto**: cambio d'agente con registrazione di `from_agent_id`, `to_agent_id`, giorno, motivo, mood dichiarato
- **Profilo emergente**: calcolato da `HumanPlayer.get_emergent_profile()` — categoria dominante, distribuzione percentuale, pattern (stress_avoider/explorer/selective), durata media possesso
- **Match score**: affinità 0-100 tra umano e agente basata su bias del profilo vs preferenze umane

---

## Dettaglio implementazioni

### M4 — Conseguenze differite
3 scelte esistenti triggerano eventi dopo N turni (es. difendi un collega → 2 turni dopo arriva `collega_ringrazia`). 5 nuovi eventi narrativi: `collega_ringrazia`, `richiamo_formale`, `progetto_premio`, `burnout_startup`, `passaggio_generazionale`. Badge "N in sospeso" nella UI.

### E6 — Tracking tempo decisione
`_decision_start` timestamp al render evento, calcolato in `_make_choice`, salvato in `analytics.db`, mostrato nel report (media, scelta più rapida, più lenta).

### E7 — Achievement
Sbloccati a soglie di tag (yes_man≥10/20, burnout_risk≥5/10, truth_teller≥8/15, boundary_setter≥8/15, survivor≥10/20, days_survived≥30/60).

### F4-F9 — Asset grafici
22 PNG personaggi in 6 gruppi emotivi (Neoassunto, Esausto, Critico, Manager tossico, Corporate tossico, Ironico). 12 icone eventi. 5 icone stati. Emote per categoria scelta. Label effetti. Help system.

---

## v3.5 — Social Physics & HR Intelligence (Completato)

| # | Componente | Descrizione | Stato |
|---|------------|-------------|-------|
| S1 | CI/CD Pipeline | GitHub Actions workflow per test e lint automatici | Completato |
| S2 | Peer Influence Avanzata | Agenti influenzano tratti OCEAN reciproci basati su prossimità di fazioni e stress | Completato |
| S3 | Pressione Culturale Dinamica | Archetipo aziendale evolve in base alla media OCEAN/Dark Triad degli agenti | Completato |
| S4 | Dashboard Unificata | 4 moduli: AgentMonitor (risk ranking), AlertSystem (soglie critiche), Reports (HR DSS + turnover risk), TimelineViewer | Completato |
| S5 | Visualizzazione 3D Collins Cube | Scatter3D ECharts con Stress/Energia/Integrità, colori per profilo, rotazione automatica | Completato |
| S6 | Test Coverage | 31 nuovi test per tutte le funzionalità v3.5 (peer influence, cultural drift, dashboard, cube) | Completato |

### S1 — CI/CD Pipeline
Workflow GitHub Actions in `.github/workflows/test.yml`: esegue `ruff check` + `pytest` su ogni push/PR.

### S2 — Peer Influence Avanzata
In `agents/personality.py`:
- `peer_influence(other_profiles, proximity_weights)`: accumula delta OCEAN in buffer
- `apply_peer_influence_buffer()`: applica il buffer modificando i tratti
In `agents/swarm.py`:
- `_apply_peer_influence()`: chiamato in ogni `run_simulation_step()`, calcola prossimità basata su similarità fazioni (60%) e differenza stress (40%)

### S3 — Pressione Culturale Dinamica
In `agents/swarm.py`:
- `_apply_cultural_drift()`: calcola media OCEAN+DarkTriad, determina archetipo dominante (Startup/Corporate/Familiare/Consulting), modifica HR params ogni 5 turni
- `_get_cultural_drift_info()`: esposto in `get_laboratory_view()` e mostrato nella UI lab

### S4 — Dashboard Unificata
In `dashboard/main_dashboard.py`:
- **MainDashboard**: hub unificato con overview, alert aggregati, top risk ranking
- **AgentMonitor**: risk ranking con 6 fattori (stress, energia, salute, autostima, rep, vulnerabilità psicologica), trend metric
- **AlertSystem**: 7 tipi di alert (stress_critico, energia_critica, salute_critica, burnout_imminente, trend_stress_rapido, stress_alto, autostima_critica) con severità critical/warning/info
- **Reports**: 3 tipi report (summary, hr_dss con raccomandazioni, turnover_risk con ranking), report per singolo agente
- **TimelineViewer**: timeline decisioni per agente o globale, filtro per giorno

### S5 — Visualizzazione 3D Collins Cube
In `ui/pages/laboratory_page.py`: ECharts `scatter3D` con assi Stress (x), Energia (y), Integrità (z), colori per profilo psicologico, simboli diamond per agenti posseduti, rotazione automatica.

### S6 — Test Coverage
31 nuovi test in `tests/test_v3_5.py` che coprono:
- Peer influence (buffer, applicazione, swarm integration, single-agent edge case)
- Cultural drift (score generation, HR param modification, lab view exposure)
- AgentMonitor (risk ranking, sorting, field presence, trend)
- AlertSystem (evaluation, field presence, severity, history)
- Reports (summary, hr_dss, turnover_risk, agent report, empty swarm)
- TimelineViewer (global/agent timeline, events by day)
- MainDashboard (overview, with/without swarm)
- Collins Cube (data presence, range validation)

---

## Future

- **Multi-utente** (sciame dedicato per sessione, non globale)
- **Integrazione ML**: Modello predittivo sul rischio di dimissioni di massa
- **UI dedicata** per i moduli della dashboard (pagine NiceGUI per AlertSystem, Reports, TimelineViewer)
- **Localizzazione completa** IT/EN per tutti i contenuti narrativi
- **Esportazione dati** scientifica (CSV/JSON strutturato per analisi antropologiche)

---

*Documento aggiornato per BurnoutSimulator v3.5 — Social Physics & HR Intelligence. Ultimo aggiornamento: Luglio 2026.*
