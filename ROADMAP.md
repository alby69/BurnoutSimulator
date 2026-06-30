# Roadmap — BurnoutSimulator

## Come funzionano le FAZIONI (risposta alla tua domanda)

Le tre fazioni rappresentano il **posizionamento sociale** del giocatore nell'ecosistema aziendale:

| Fazione | Valore iniziale | Cosa significa |
|---------|:-:|----------------|
| **Fedelissimi** | 0% | Ti allinei al management, non metti in discussione, esegui |
| **Gruppo Silenzioso** | 50% | La maggioranza silenziosa — fai il tuo lavoro senza esporsi |
| **Ribelli** | 0% | Ti opponi attivamente, segnali, difendi i confini |

Le percentuali cambiano in base alle tue scelte. Ogni effetto `faction_Ribelli: +3` o `faction_Fedelissimi: +2` negli eventi modifica questi valori.

**Problema attuale:** le fazioni sono solo numeri a schermo. Non influenzano:
- quali NPC si schierano con te
- quali eventi ti capitano
- dialoghi o conseguenze diverse in base alla reputazione

Servono per calcolare il finale (analisi antropologica), ma durante il gioco non danno feedback. Vedi proposta **M2** sotto.

---

## Completati ✅

### ✅ M1 — FEEDBACK SULLE SCELTE

Dopo ogni scelta si apre un **dialog** con gli effetti reali:

```
┌──────────────────────┐
│  Esito della scelta   │
│  [COMPLIANCE]         │
│                       │
│  ▼ Stress      +3    │
│  ▲ Rep. Manager +2   │
│  ▼ Energia     -2    │
│  ▲ Marco Trust +2    │
│                      │
│  [Continua]          │
└──────────────────────┘
```

- Delta colorato (verde ↑ positivo, rosso ↓ negativo)
- Sfondo dipende dal segno (verde/rosso)
- Categoria della scelta mostrata come badge

### ✅ M3 — ANTEPRIMA EFFETTI AL PASSAGGIO MOUSE

Al passaggio del mouse su ogni scelta, un **tooltip** mostra gli effetti:

```
Tooltip:
  manager_rep: +2
  stress: +3
  energy: -2
  npc_Marco_trust: +2
```

Implementato con `ui.tooltip()` nativo NiceGUI — funziona su desktop e mobile (tap lungo).

### ✅ M6 — STORICO SCELTE VISIBILE IN PARTITA

Nella sidebar, sotto le RELAZIONI, compare **ULTIME SCELTE** con le ultime 5 decisioni:

- Ogni scelta ha un pallino colorato in base alla categoria (blu COMPLIANCE, rosso RESISTANCE, giallo NEGOTIATION, verde ESCAPE)
- Testo troncato a 40 caratteri
- Si aggiorna automaticamente a ogni turno

---

## Prossimi miglioramenti

### ✅ M2 — FAZIONI VISIBILI E REATTIVE

Ogni NPC appartiene a una fazione:

| NPC | Fazione |
|-----|----------|
| Marco (Manager) | Fedelissimi (naturale) |
| Giulia (Collega) | Fedelissimi (opportunista) |
| Roberto (Mentor) | Gruppo Silenzioso (deluso) |
| Elena (HR) | Gruppo Silenzioso (passiva) |

**Effetto:** se la tua affinità con una fazione sale, gli NPC di quella fazione migliorano rapporto con te. Se scende, potrebbero remarti contro.

Esempio: `faction_Fedelissimi > 70` → Marco ti dà più bonus, ma Roberto ti perde rispetto (vede in te un "yes man").

Implementato con `_sync_factions_to_npcs()` in `engine.py`, chiamato dopo ogni scelta in `handle_choice()`.

### M3 — BARRA DELLE CONSEGUENZE PRIMA DELLA SCELTA

Prima di cliccare una scelta, mostrare un **anteprima degli effetti** al passaggio del mouse:

```
[1. Rispondi immediatamente]
    ⚡ Energia: -2  |  🔥 Stress: +2  |  📊 Rep: +2
```

### ✅ M4 — SISTEMA DI CONSEGUENZE DIFFERITE

- Le scelte con `consequences` in `events.json` innescano eventi narrativi dopo N turni (es. difendi un collega → 2 turni dopo arriva l'evento `collega_ringrazia`)
- 3 scelte esistenti triggerano eventi differiti, più 5 nuovi eventi narrativi (`collega_ringrazia`, `richiamo_formale`, `progetto_premio`, `burnout_startup`, `passaggio_generazionale`)
- Eventi differiti mostrati come badge "N in sospeso" nella UI

### ✅ M5 — PIÙ FINALI PESATI SULLE FAZIONI

Aggiunti 4 finali basati sulle **fazioni** in `determine_ending()` in `app.py`:

| Condizione | Finale |
|---|---|
| Ribelli > 70 e Integrity > 60 | Il Whistleblower |
| Fedelissimi > 70 e Manager Rep > 80 | Il Braccio Destro |
| Gruppo Silenzioso > 70 | Lo Spettatore |
| Tutte le fazioni > 50 | Il Camaleonte |

I finali fazione hanno priorità più alta dei finali classici nel sistema di punteggio.

### M6 — STORICO SCELTE VISUALE (DURANTE LA PARTITA)

Nel pannello laterale, aggiungere una sezione **STORICO** con le ultime scelte:

- Icona ridimensionata per ogni scelta recente
- Colore in base alla categoria (COMPLIANCE = blu, RESISTANCE = rosso, NEGOTIATION = giallo, ESCAPE = verde)

### ✅ M7 — GRAFO DECISIONALE INTERATTIVO

Dialog accessibile dal pulsante `hub` nella barra superiore (gioco) e dal report finale:

- Grafo force-directed ECharts con nodi colorati per categoria evento
- Archi colorati per categoria scelta (COMPLIANCE blu, RESISTANCE rosso, ecc.)
- Strumenti: zoom, pan, trascinamento nodi, focus su adiacenza
- Mostra i percorsi effettivamente percorsi dal giocatore, con connessioni narrativ

### ✅ M8 — SCENARI GIORNALIERI (MORNING ROUTINE)

Prima dell'evento principale, un **mini-evento** casuale (da 15 scenari in `engine.MINI_EVENTS`) che modifica le statistiche di base:

- *"Trovi traffico, arrivi in ufficio già stressato"* → Stress +5
- *"Un collega ti offre un caffè"* → Energia +3, Trust Collega +2
- *"Ricevi una mail di un headhunter"* → Employability +5, Stress -2

Eseguito all'inizio di `next_turn()`, mostrato in una card grigia prima dell'evento principale.

### ✅ M9 — PROFILO UTENTE GLOBALE (ANALYTICS DASHBOARD)

Usando i dati già raccolti in `database/analytics.db`:

- Dashboard `analytics` screen in `app.py` con:
  - Classifica finali più ottenuti (con barre)
  - Percentuale scelte per categoria (colorate)
  - Sopravvivenza media per archetipo aziendale (con barre proporzionali)
  - Ultime 10 partite giocate
  - Accessibile dal pulsante "📊 Analytics" nella schermata iniziale

### ✅ M10 — RESPONSIVE MOBILE MIGLIORATO

Mobile toggle per la sidebar:

- Sidebar nascosta su schermi <768px via CSS `stats-sidebar` class
- Pulsante `bar_chart` visibile solo su mobile nella barra superiore, apre il dialog statistiche
- Breakpoint responsive con classi Tailwind `lg:hidden` e `stats-sidebar`

### ✅ M11 — TUTORIAL / ONBOARDING INTERATTIVO

Prima partita guidata con overlay modale a 5 step:

- *"Benvenuto"* — introduzione al gioco
- *"Le Statistiche"* — radar e barre, pulsazione in zona critica
- *"Fazioni e NPC"* — avatar colorati per fazione
- *"Le Scelte"* — effetti visibili + timer su scelte critiche
- Ready step finale con "Inizia a giocare"
- Navigabile avanti/indietro

### ✅ M12 — EVENTI A TEMPO (DECISIONI CON TIMER)

1 scelta casuale per evento ha un **timer di 15 secondi**:

- Contatore visivo ⏱ accanto alla scelta
- Auto-click della scelta quando il timer scade
- Integrato via `ui.run_javascript()` con setInterval lato client

---

## Tabella riepilogativa

| # | Miglioramento | Impatto | Sforzo | Stato |
|---|---------------|---------|--------|-------|
| M1 | Feedback effetti dopo la scelta | Alto | Basso | ✅ Fatto |
| M2 | Fazioni influenzano NPC | Alto | Medio | ✅ Fatto |
| M3 | Anteprima effetti al passaggio mouse | Medio | Basso | ✅ Fatto |
| M4 | Conseguenze narrativi differite | Alto | Alto | ✅ Fatto |
| M5 | Più finali basati su fazioni | Alto | Medio | ✅ Fatto |
| M6 | Storico scelte visibile in partita | Medio | Basso | ✅ Fatto |
| M7 | Grafo decisionale interattivo | Basso | Alto | ✅ Fatto |
| M8 | Mini-eventi giornalieri (routine) | Alto | Medio | ✅ Fatto |
| M9 | Dashboard analytics globale | Medio | Medio | ✅ Fatto |
| M10 | Mobile responsive migliorato | Medio | Basso | ✅ Fatto |
| M11 | Tutorial / onboarding | Alto | Medio | ✅ Fatto |
| M12 | Eventi con timer | Medio | Basso | ✅ Fatto |

---

## Priorità consigliata

1. ✅ ~~M2 + M5~~ (fazioni con peso reale) — completato
2. ✅ ~~M4~~ (conseguenze differite) — completato
3. ✅ ~~M8~~ (mini-eventi giornalieri) — completato
4. ✅ ~~M11~~ (tutorial) — completato
5. ✅ ~~M10~~ (mobile) — completato
6. ✅ ~~M12~~ (timer) — completato
7. ✅ ~~M9~~ (dashboard analytics) — completato
8. ✅ ~~M7~~ (grafo decisionale) — completato

Tutti i 12 miglioramenti pianificati sono stati implementati. 🎉

## Extra: miglioramenti post-roadmap

| # | Miglioramento | Impatto | Sforzo | Stato |
|---|---------------|---------|--------|-------|
| E1 | Personalità Manager per archetipo (Micromanager, Narcisista, ecc.) | Alto | Medio | ✅ Fatto |
| E2 | Eventi su soglia (stress>80, energia<20, ecc.) | Alto | Basso | ✅ Fatto |
| E3 | Grafico stress/tempo nel report finale | Alto | Basso | ✅ Fatto |
| E4 | Fasi di carriera (Prova → Primo Progetto → Ristrutturazione → …) | Medio | Basso | ✅ Fatto |
| E5 | 5 nuovi finali incrociando archetipo + profilo | Alto | Medio | ✅ Fatto |
| E6 | Tracking tempo di decisione per scelta | Medio | Basso | ✅ Fatto |
| E7 | 10 nuovi achievement (Senza Filtro, Muro di Berlino, ecc.) | Basso | Basso | ✅ Fatto |
| E8 | Modalità "Casi Reali" | Basso | Basso | ✅ Fatto |

### Descrizioni

- **E1**: ogni archetipo aziendale ha un manager con personalità distinta (stress_bonus passivo, rep_bonus_compliance, crisis_threshold), visibile nella sidebar con descrizione.
- **E2**: 7 eventi triggerati da soglie statistiche (stress, energia, salute, autostima, rep, fazioni) con testo narrativo ed effetti. Si attivano una volta per soglia.
- **E3**: grafico a linee ECharts (Stress + Energia nel tempo) nel report finale, usando `stats_history` in memoria.
- **E4**: 5 fasi (Periodo di Prova → Primo Progetto → Fase Operativa → Ristrutturazione → Sopravvivenza) visibili nella sidebar.
- **E5**: IL FONDATORE ESAURITO (Startup+burnout_risk), IL PECORA NERA (Familiare+truth_teller), L'INGRANAGGIO PERFETTO (Consulting+yes_man), IL RESISTENTE (energia bassa+longevità), L'INDIOMABILE (autostima alta).
- **E6**: `_decision_start` timestamp al render evento, calcolato in `_make_choice`, salvato in `analytics.db` e mostrato nel report (media, rapide, lente).
- **E7**: sbloccati a 8/15 occorrenze per truth_teller e boundary_setter, 20 per yes_man, 10 per burnout_risk e survivor, 30/60 giorni.
- **E8**: checkbox nella schermata iniziale, mostra badge "Caso Reale" sugli eventi in partita.

---

## Overhaul grafico (Giugno 2026)

| # | Fase | Descrizione | Stato |
|---|------|-------------|-------|
| **F1** | CSS Overhaul | Background gradiente, card `event-card` / `vn-card` con bordo accentato (`--theme-accent`), palette per archetipo, font Inter + JetBrains Mono, scrollbar personalizzata, responsive raffinato | ✅ |
| **F2** | Facce SVG dinamiche | Funzione `_npc_svg_face()` in app.py: 6 espressioni (neutral/happy/worried/angry/stressed/scared) calcolate da trust/fear/stress, sostituiti avatar testuali (cerchi con iniziali) con SVG inline | ✅ |
| **F3** | Layout Visual Novel | Ritratto NPC 64px + nome affiancato alla card narrativa, NPC ruota per turno (`history length % 4`), scelte stile dialog VN (tracking uppercase, border accentato, hover glow) | ✅ |

### Dettaglio F1 — CSS Overhaul

- `body::before` con gradienti radiali laterali per profondità
- `vn-card`: bordo `rgba(255,255,255,0.06)`, gradiente interno `#12122a → #0e0e20`, box-shadow
- `event-card`: gradiente `#141430 → #0f0f24`, narrativa font-size 15px, line-height 1.7
- `vn-card-highlight`: `border-top: 2px solid var(--theme-accent, #3b82f6)`
- Sidebar: `stats-sidebar-card` con lo stesso stile delle altre card
- Pulsanti scelta: `choice-btn` con hover translateX(6px), border-color accentato, min-height 52px
- Label sezioni tutte `text-xs uppercase tracking-wider` coerenti
- Scrollbar personalizzata (6px, trasparente, thumb rgba)

### Dettaglio F2 — Facce SVG dinamiche

```python
def _npc_svg_face(nname, ndata) -> str:
    # Determina espressione da trust/fear/stress
    # 6 espressioni → SVG con 3 path (occhi, bocca, sopracciglia)
    # Restituisce <svg> inline 28×32 viewBox
```

Espressioni:
| Condizione | Espressione |
|---|---|
| fear > trust e fear > 40 | `scared` |
| trust < 30 e fear < 20 | `angry` |
| stress > 70 | `stressed` |
| trust < 40 | `worried` |
| trust ≥ 75 | `happy` |
| default | `neutral` |

### Dettaglio F3 — Layout Visual Novel

- Colonna sinistra: ritratto NPC (64px, bordo colorato per fazione, SVG face) + nome
- Colonna destra: card evento (`event-card vn-card-highlight`) con testo narrativo
- NPC portrait ruota tra i 4 NPC (Marco, Giulia, Roberto, Elena) in base a `len(history) % 4`
- "Cosa fai?" in uppercase tracking-wider
- Scelte con effetto hover glow (box-shadow + border-color transition)
- Mini-evento giornaliero adotta stesso stile `event-card`

### Tabella riepilogativa completa

| # | Miglioramento | Impatto | Sforzo | Stato |
|---|---------------|---------|--------|-------|
| M1 | Feedback effetti dopo la scelta | Alto | Basso | ✅ Fatto |
| M2 | Fazioni influenzano NPC | Alto | Medio | ✅ Fatto |
| M3 | Anteprima effetti al passaggio mouse | Medio | Basso | ✅ Fatto |
| M4 | Conseguenze narrativi differite | Alto | Alto | ✅ Fatto |
| M5 | Più finali basati su fazioni | Alto | Medio | ✅ Fatto |
| M6 | Storico scelte visibile in partita | Medio | Basso | ✅ Fatto |
| M7 | Grafo decisionale interattivo | Basso | Alto | ✅ Fatto |
| M8 | Mini-eventi giornalieri (routine) | Alto | Medio | ✅ Fatto |
| M9 | Dashboard analytics globale | Medio | Medio | ✅ Fatto |
| M10 | Mobile responsive migliorato | Medio | Basso | ✅ Fatto |
| M11 | Tutorial / onboarding | Alto | Medio | ✅ Fatto |
| M12 | Eventi con timer | Medio | Basso | ✅ Fatto |
| E1 | Personalità Manager per archetipo | Alto | Medio | ✅ Fatto |
| E2 | Eventi su soglia | Alto | Basso | ✅ Fatto |
| E3 | Grafico stress/tempo nel report | Alto | Basso | ✅ Fatto |
| E4 | Fasi di carriera | Medio | Basso | ✅ Fatto |
| E5 | 5 nuovi finali incrociati | Alto | Medio | ✅ Fatto |
| E6 | Tracking tempo decisione | Medio | Basso | ✅ Fatto |
| E7 | 10 nuovi achievement | Basso | Basso | ✅ Fatto |
| E8 | Modalità Casi Reali | Basso | Basso | ✅ Fatto |
| **F1** | **CSS Overhaul** | Alto | Medio | ✅ Fatto |
| **F2** | **Facce SVG dinamiche** | Alto | Medio | ✅ Fatto |
| **F3** | **Layout Visual Novel** | Alto | Medio | ✅ Fatto |

**Totale: 23 miglioramenti implementati.**
