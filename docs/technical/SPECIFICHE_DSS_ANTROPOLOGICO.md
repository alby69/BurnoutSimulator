# Specifiche per il DSS Antropologico e Dinamiche dello Sciame di Agenti

## 1. Introduzione: Il Simulatore come Strumento Antropologico per HR

Il BurnoutSimulator non è semplicemente un gioco o una simulazione accademica isolata, ma un vero e proprio **dispositivo di Decision Support System (DSS) antropologico** pensato per le Risorse Umane e l'alta direzione aziendale. Nelle organizzazioni moderne, i dati quantitativi tradizionali (come l'eNPS, le indagini di clima o i tassi di turnover) offrono solo una panoramica a posteriori, spesso quando il danno culturale è già avvenuto.

Il simulatore colma questa lacuna offrendo un approccio basato sull'**Agent-Based Modeling (ABM)** e sulla **soggettività sintetica**, consentendo di simulare in sicurezza (senza l'effetto Panopticon o bias dell'osservatore) scenari aziendali tossici e di osservare la nascita, l'evoluzione e il collasso delle diverse culture interne.

---

## 2. Come Operano gli Agenti Autonomi: Dinamica e Meccanismi Fondamentali

Gli agenti all'interno della simulazione non sono semplici entità randomiche, ma operano secondo una complessa architettura a tre livelli:

```
+--------------------------------------------------------+
|                      MIND LEVEL                        |
|   PsychologicalProfile (Big Five / Triade Oscura)     |
|   Compliance/Resistance/Negotiation/Escape Bias        |
+--------------------------+-----------------------------+
                           |
                           v
+--------------------------+-----------------------------+
|                     CONTEXT LEVEL                      |
|   Modulazione RPG (Scontro di Tratti e Parametri HR)    |
|   Tossicità, Coesione, Pressione, Competizione        |
+--------------------------+-----------------------------+
                           |
                           v
+--------------------------+-----------------------------+
|                     ACTION LEVEL                       |
|   Scelte nel Motore Narrativo (Engine)                 |
|   Apprendimento Storico e Conseguenze Differite       |
+--------------------------------------------------------+
```

### A. Livello Psicometrico (Tratti e Bias)
Ogni agente è descritto da un profilo basato sul modello internazionale **Big Five (OCEAN)** e sulla **Triade Oscura (Narcisismo, Machiavellismo, Psicopatia)**. Questi tratti non sono statici ma definiscono:
- **I pesi decisionali relativi alle quattro strategie comportamentali**:
  - *Compliance* (Accondiscendenza/Obbedienza)
  - *Resistance* (Resistenza attiva/passiva)
  - *Negotiation* (Negoziazione/Mediazione)
  - *Escape* (Fuga/Distacco/Dimissioni)
- Ad esempio, un agente con alto Nevroticismo e bassa Estroversione tenderà naturalmente verso scelte di *Escape*, mentre un profilo con alta Gradevolezza e Coscienziosità preferirà opzioni di *Compliance* o *Negotiation*.

### B. Modulazione degli Impatti delle Scelte (Meccanica RPG)
La vera forza del modello risiede nella modulazione dell'impatto degli eventi. Se un evento prevede un aumento di stress di $+15$, il valore reale subìto dall'agente viene calcolato dinamico (RPG Modulator):
- **Scontro con i Tratti del Manager**: Se il manager ha tratti tossici (alta Psicopatia), l'aumento di stress viene amplificato (fino a $1.5\times$ o $2\times$) per gli agenti particolarmente Gradevoli ed Empatici (i soggetti più vulnerabili all'abuso di potere).
- **Tratti Intrinseci**: Un agente ad alto Nevroticismo subisce picchi di stress e perdite di salute drasticamente superiori rispetto a un profilo resiliente.
- **Parametri HR ambientali**: Una bassa Coesione Sociale o un'elevata Tossicità Ambientale amplificano e cronicizzano ogni impatto negativo di routine lavorativa.

### C. Apprendimento e Memoria (AgentMemory)
Gli agenti ricordano gli esiti delle proprie decisioni passate. Se una specifica scelta ha portato storicamente a perdite drammatiche di energia o ad aumenti ingestibili di stress, l'agente applicherà un fattore correttivo riducendo drasticamente la probabilità di scegliere nuovamente quella via. Questo mima l'apprendimento e l'adattamento umano a contesti ostili.

---

## 3. Rappresentazione del Comportamento Umano in Aziende Tossiche

Attraverso partite giocate in completa autonomia, lo sciame di agenti rappresenta fedelmente le dinamiche umane reali all'interno di ambienti organizzativi ad alta pressione:

### A. La Deriva Culturale (Cultural Drift) e la perdita di Biodiversità
Quando un'azienda ha parametri HR deteriorati (es. alta Competizione Interna e Tossicità), si assiste a una vera e propria **pressione evolutiva**:
- I profili **Idealisti** e **Protettori** (che cercano di difendere l'etica o i colleghi) subiscono sanzioni reputazionali e picchi di stress insostenibili, portandoli rapidamente al burnout o all'espulsione (dimissioni/licenziamento).
- Sopravvivono invece i profili **Cinici** o **Manipolatori**, in grado di navigare le acque torbide della tossicità politica aziendale.
- Questa dinamica mostra all'HR come un ambiente tossico generi una perdita drammatica di biodiversità psicologica, portando a una cultura monolitica focalizzata solo sulla sopravvivenza o sull'individualismo cinico.

### B. Peer Influence (Pressione dei Pari)
Gli agenti non vivono in silos isolati. All'interno dello sciame, gli agenti si influenzano reciprocamente. La prossimità relazionale e le dinamiche di fazione (Fedelissimi, Ribelli, Gruppo Silenzioso) spingono i tratti OCEAN degli agenti vicini ad allinearsi. Se i "Fedelissimi" diventano la fazione dominante ed esercitano una forte coesione, gli altri agenti subiranno una pressione invisibile che modificherà i loro stessi tratti di personalità (es. riducendo l'apertura mentale e aumentando la sottomissione).

---

## 4. Integrazione con i Sistemi di Supporto alle Decisioni (DSS) per l'Alta Direzione

I dati generati dalle partite autonome alimentano direttamente una suite di strumenti di analisi predittiva e strategica:

### A. Dashboard di Monitoraggio e Segnali Deboli
Il DSS fornisce all'alta direzione quattro moduli integrati:
1. **AgentMonitor (Risk Ranking)**: Calcola in tempo reale il punteggio di rischio (Risk Score 0-100) per ciascun lavoratore virtuale, combinando stress cronico, esaurimento di energia, perdita di autostima ed esposizione a manager tossici. Questo insegna all'HR a identificare i "segnali deboli" prima che si trasformino in dimissioni o assenze prolungate.
2. **AlertSystem (Rilevamento Anomalie)**: Genera notifiche automatiche classificate per severità (Critical, Warning, Info). Ad esempio, intercetta il "trend di incremento rapido dello stress" (es. $+15$ punti in meno di 5 turni), indicando un deterioramento acuto del clima lavorativo.
3. **Turnover Risk Report**: Calcola la probabilità di perdita del personale incrociando lo stress, la compromissione del rapporto con la gerarchia (Manager Rep) e l'occupabilità sul mercato esterno dell'agente.
4. **Collins Cube 3D**: Permette di visualizzare lo stato di salute dello sciame in uno spazio tridimensionale (Stress, Energia, Integrità), rendendo immediatamente evidente la polarizzazione dei lavoratori in sottogruppi a rischio o aree di collasso imminente.

### B. Simulazioni Prospective e A/B Testing delle Policy
L'HR e la direzione aziendale possono utilizzare il DSS in modalità "Laboratorio" per testare l'impatto controfattuale di decisioni strategiche prima di applicarle alla forza lavoro reale:
- *Scenario A*: Aumento della pressione sui risultati (Resource Pressure Slider a 80) e mantenimento di un'alta competizione interna.
- *Scenario B*: Investimento sulla coesione sociale (Social Cohesion Slider a 70) e riduzione della tossicità ambientale tramite trasparenza informativa.
- Lanciando centinaia di partite in autonomia per ciascuno scenario, la direzione può confrontare i tassi di sopravvivenza, i livelli medi di stress e la stabilità delle fazioni emergenti per compiere scelte informate basate su evidenze simulative.

---

## 5. Piano di Implementazione Futuro e Consolidamento delle Funzionalità

Per evolvere ulteriormente il DSS verso uno strumento standardizzato di HR Intelligence, si definisce il seguente piano d'azione:

1. **Predizione Tramite Modelli di Machine Learning**:
   Implementazione di algoritmi predittivi leggeri sul database storico delle simulazioni (`swarm_history`) per identificare con precisione la "giornata di rottura culmine" prima che l'agente entri nella fase di burnout terminale.
2. **Esportazione Scientifica in Formati Standard (CSV/JSON)**:
   Aggiunta di un modulo di esportazione integrato che permetta ad antropologi e analisti esterni di estrarre le serie storiche dei tratti e delle decisioni per studi statistici con strumenti terzi (R, Python Pandas, SPSS).
3. **UI NiceGUI per Sottomoduli Dashboard**:
   Espansione dell'interfaccia utente con pagine dedicate per la visualizzazione dettagliata degli Alert e dei Report storici, consentendo un'analisi retrospettiva approfondita turnazione per turnazione.
