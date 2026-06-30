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

### M2 — FAZIONI VISIBILI E REATTIVE

Ogni NPC dovrebbe appartenere a una fazione:

| NPC | Fazione |
|-----|----------|
| Marco (Manager) | Fedelissimi (naturale) |
| Giulia (Collega) | Fedelissimi (opportunista) |
| Roberto (Mentor) | Gruppo Silenzioso (deluso) |
| Elena (HR) | Gruppo Silenzioso (passiva) |

**Effetto:** se la tua affinità con una fazione sale, gli NPC di quella fazione migliorano rapporto con te. Se scende, potrebbero remarti contro.

Esempio: `faction_Fedelissimi > 70` → Marco ti dà più bonus, ma Roberto ti perde rispetto (vedi in te un "yes man").

### M3 — BARRA DELLE CONSEGUENZE PRIMA DELLA SCELTA

Prima di cliccare una scelta, mostrare un **anteprima degli effetti** al passaggio del mouse:

```
[1. Rispondi immediatamente]
    ⚡ Energia: -2  |  🔥 Stress: +2  |  📊 Rep: +2
```

### M4 — SISTEMA DI DIALOGO E CONSEGUENZE NPC

- Aggiungere **dialoghi scriptati** dopo certe scelte (es. Marco ti chiama in privato)
- Le relazioni NPC dovrebbero influenzare gli eventi futuri (es. se Marco Trust < 20, eventi più ostili; se > 80, eventi più favorevoli)
- Feedback testuale subito dopo la scelta: *"Marco annuisce soddisfatto"* / *"Giulia evita il tuo sguardo"*

### M5 — PIÙ FINALI PESATI SULLE FAZIONI

Attualmente 8 finali basati quasi solo sulle statistiche. Aggiungere finali basati sulle **fazioni**:

| Condizione | Finale |
|---|---|
| Ribelli > 70 e Integrity > 60 | Il Whistleblower |
| Fedelissimi > 70 e Manager Rep > 80 | Il Braccio Destro |
| Gruppo Silenzioso > 70 | Lo Spettatore |
| Tutte le fazioni > 50 | Il Camaleonte |

### M6 — STORICO SCELTE VISUALE (DURANTE LA PARTITA)

Nel pannello laterale, aggiungere una sezione **STORICO** con le ultime scelte:

- Icona ridimensionata per ogni scelta recente
- Colore in base alla categoria (COMPLIANCE = blu, RESISTANCE = rosso, NEGOTIATION = giallo, ESCAPE = verde)

### M7 — GRAFO DECISIONALE INTERATTIVO

Schermata "Statistiche Avanzate" con un grafo delle scelte fatte finora:

```
[evento_1] ──COMPLIANCE──→ [evento_3]
    │
    └──RESISTANCE──→ [evento_2] ──NEGOTIATION──→ [evento_5]
```

Usabile con la libreria `pyvis` o un canvas HTML.

### M8 — SCENARI GIORNALIERI (MORNING ROUTINE)

Prima dell'evento principale, un **mini-evento** casuale che modifica le statistiche di base:

- *"Trovi traffico, arrivi in ufficio già stressato"* → Stress +5
- *"Un collega ti offre un caffè"* → Energia +3, Trust Collega +2
- *"Ricevi una mail di un headhunter"* → Employability +5, Stress -2

### M9 — PROFILO UTENTE GLOBALE (ANALYTICS DASHBOARD)

Usando i dati già raccolti in `database/analytics.db`:

- Dashboard `/analytics` con:
  - Classifica finali più ottenuti
  - Percentuale scelte per categoria
  - Tempo medio sopravvivenza per archetipo aziendale
  - Scenario più tossico (top 3)
  - Heatmap delle scelte

### M10 — RESPONSIVE MOBILE MIGLIORATO

La sidebar a sinistra va in overflow su mobile. Sostituire con:

- Stats collassabili in un drawer (icona hamburger)
- Schede navigabili: STATS | STORIA | FAZIONI
- Bottoni delle scelte più grandi per touch

### M11 — TUTORIAL / ONBOARDING INTERATTIVO

Prima partita guidata con tooltip esplicativi:

- *"Questa barra mostra il tuo livello di stress. Se arriva a 100% perdi."*
- *"Le tue scelte influenzano le fazioni. Vedrai il feedback qui."*
- *"Ogni NPC ha fiducia, rispetto e paura verso di te."*

### M12 — EVENTI A TEMPO (DECISIONI CON TIMER)

Alcuni eventi critici potrebbero avere un **timer** per la scelta (30 secondi):

- Simula la pressione di dover decidere velocemente
- Se scade il timer: scelta di default (COMPLIANCE passiva) o scelta casuale
- Aggiunge tensione e realismo

---

## Tabella riepilogativa

| # | Miglioramento | Impatto | Sforzo | Stato |
|---|---------------|---------|--------|-------|
| M1 | Feedback effetti dopo la scelta | Alto | Basso | ✅ Fatto |
| M2 | Fazioni influenzano NPC | Alto | Medio | 🔴 Da fare |
| M3 | Anteprima effetti al passaggio mouse | Medio | Basso | ✅ Fatto |
| M4 | Dialoghi scriptati e conseguenze NPC | Alto | Alto | 🟡 Da fare |
| M5 | Più finali basati su fazioni | Alto | Medio | 🔴 Da fare |
| M6 | Storico scelte visibile in partita | Medio | Basso | ✅ Fatto |
| M7 | Grafo decisionale interattivo | Basso | Alto | 🟢 Da fare |
| M8 | Mini-eventi giornalieri (routine) | Alto | Medio | 🟡 Da fare |
| M9 | Dashboard analytics globale | Medio | Medio | 🟢 Da fare |
| M10 | Mobile responsive migliorato | Medio | Basso | 🟡 Da fare |
| M11 | Tutorial / onboarding | Alto | Medio | 🟡 Da fare |
| M12 | Eventi con timer | Medio | Basso | 🟢 Da fare |

---

## Priorità consigliata

1. **M2 + M5** (fazioni con peso reale) — dà senso a tutto il sistema fazioni
2. **M4** (dialoghi) — trasforma il gioco da "menu di scelte" a "simulazione narrativa"
3. **M8** (mini-eventi giornalieri) — più varietà tra un evento e l'altro
4. **M11** (tutorial) — fondamentale per nuovi giocatori
5. **M10** (mobile) — migliora l'esperienza su telefono
