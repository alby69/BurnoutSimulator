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

Servono per calcolare il finale (analisi antropologica), ma durante il gioco non danno feedback. Vedi proposta **M4** sotto.

---

## Prossimi miglioramenti

### M1 — FEEDBACK SULLE SCELTE

Dopo ogni scelta, mostrare un **popup temporaneo** con gli effetti reali:

```
┌──────────────────────┐
│  Scelta: COMPLIANCE   │
│                       │
│  Manager Rep:   +2   │
│  Stress:        +3   │
│  Energia:       -2   │
│  Marco Trust:   +2   │
│                      │
│  [OK]                │
└──────────────────────┘
```

- Mostrare per ogni effetto il delta colore (verde positivo, rosso negativo)
- Prima di scegliere: mostrare le **conseguenze stimate** (opzionale, hover/tooltip)

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

| # | Miglioramento | Impatto | Sforzo | Priorità |
|---|---------------|---------|--------|----------|
| M1 | Feedback effetti dopo la scelta | Alto | Basso | 🔴 Alta |
| M2 | Fazioni influenzano NPC | Alto | Medio | 🔴 Alta |
| M3 | Anteprima effetti al passaggio mouse | Medio | Basso | 🔴 Alta |
| M4 | Dialoghi scriptati e conseguenze NPC | Alto | Alto | 🟡 Media |
| M5 | Più finali basati su fazioni | Alto | Medio | 🟡 Media |
| M6 | Storico scelte visibile in partita | Medio | Basso | 🟡 Media |
| M7 | Grafo decisionale interattivo | Basso | Alto | 🟢 Bassa |
| M8 | Mini-eventi giornalieri (routine) | Alto | Medio | 🟡 Media |
| M9 | Dashboard analytics globale | Medio | Medio | 🟢 Bassa |
| M10 | Mobile responsive migliorato | Medio | Basso | 🟡 Media |
| M11 | Tutorial / onboarding | Alto | Medio | 🟡 Media |
| M12 | Eventi con timer | Medio | Basso | 🟢 Bassa |

---

## Come contribuire / priorità consigliata

1. **Partire da M1** (feedback effetti) — poche righe, impatto enorme sul giocatore
2. **M3** (anteprima) — completamento naturale di M1
3. **M2 + M5** (fazioni con peso reale) — dà senso a tutto il sistema
4. **M4** (dialoghi) — trasforma il gioco da "menu di scelte" a "simulazione narrativa"
