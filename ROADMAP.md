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
