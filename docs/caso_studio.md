# BurnoutSimulator: Giocare con la Tossicità Aziendale

## Un Caso Studio per l'Antropologia delle Organizzazioni

---

### Introduzione

BurnoutSimulator nasce come progetto di tesi magistrale alla Sapienza, e l'idea di base è piuttosto semplice: costruire un gioco — o meglio, un laboratorio interattivo — che permetta di osservare come le persone (sotto forma di agenti simulati) reagiscono a dinamiche aziendali tossiche. Non è un "gioco gestionale" nel senso classico, perché non c'è un obiettivo di profitto da massimizzare. È più un esperimento mentale: cosa succede a un gruppo di lavoratori quando l'ambiente in cui operano diventa progressivamente insostenibile?

Il progetto è interamente open source, scritto in Python, e si può avviare con due righe di comando. Ma questo è un dettaglio tecnico che vedremo dopo. Quello che conta è il *perché* e il *come*.

---

### 1. Perché Simulare la Tossicità?

L'idea di fondo è che certe dinamiche — il manager narcisista, la riunione inutile alle 18:05, il collega che si prende il merito del tuo lavoro, la scadenza impossibile — non sono "casi isolati" o colpa di singole "mele marce". Sono pattern culturali che si riproducono in modo sistematico in certi tipi di organizzazione. La domanda che il simulatore prova a porsi è: *come cambiano le persone esposte a questi pattern?*

Questa domanda non è nuova, ovviamente. Nella tesina di antropologia delle organizzazioni ([*Analisi Antropologica*](./anthropological/analisi_antropologica.md)) ho discusso i riferimenti teorici che fanno da sfondo: Byung-Chul Han e la società della prestazione, Foucault e il panopticon digitale, Bourdieu e la trasformazione dell'habitus. BurnoutSimulator parte da lì e prova a tradurre quelle intuizioni in un sistema che si può *usare*, non solo leggere. Non vuole dimostrare niente di definitivo, ma offrire uno spazio per interrogarsi: *e se fossi io, in quella situazione, cosa farei?*

---

### 2. Il Cuore del Simulatore: Agenti, Scelte, Conseguenze

Il funzionamento di base è semplice. All'avvio, si sceglie un archetipo aziendale:

- **Startup Caotica** — tutto è urgente, i ruoli sono fittizi, il fondatore è un micromanager iperattivo
- **Corporate Tossica** — processi asfissianti, politica interna, un narcisista burocratico al comando
- **Azienda Familiare** — paternalismo, ricatto affettivo, il "siamo una famiglia" come strumento di controllo
- **Consulting** — metriche ossessive, disponibilità totale, un perfezionista senza tregua

In più, si possono regolare parametri come tossicità ambientale, pressione sulle risorse, competizione interna, coesione sociale. È qui che il simulatore diventa interessante: si possono fare esperimenti A/B. Lanciare la stessa simulazione con alta tossicità e poi con bassa, e vedere come cambia l'evoluzione del gruppo.

#### 2.1 I Profili Psicologici

Il sistema crea uno "sciame" di agenti, ognuno con un profilo psicologico basato sul modello **OCEAN** (Big Five) più la **Triade Oscura**:

| Profilo | Tratti chiave | Come reagisce alla pressione |
|---------|---------------|------------------------------|
| Il Performante | Coscienziosità alta, narcisismo moderato | Si adatta, produce, ma rischia il burnout |
| Il Protettore | Gradevolezza alta, psicopatia bassa | Difende il team, si oppone alle ingiustizie |
| Il Sopravvissuto | Nevroticismo alto, estroversione bassa | Subisce, si ritira, cerca di non farsi notare |
| Il Negoziatore | Apertura alta, gradevolezza alta | Cerca compromessi, prova a mediare |
| Il Cinico | Gradevolezza bassa, machiavellismo alto | Si distacca, non crede più a niente |
| Il Manipolatore | Triade Oscura alta | Usa il sistema a proprio vantaggio |
| L'Idealista | Apertura alta, valori forti | Resistenza aperta, rischia l'isolamento |

Questa varietà di profili non è casuale. L'idea — ripresa dalla discussione sull'habitus di Bourdieu nella tesina — è che persone diverse portano nell'organizzazione disposizioni diverse, e l'ambiente le modifica nel tempo. Un idealista che ripete scelte di COMPLIANCE in un ambiente tossico diventa, col tempo, più cinico e meno aperto. Il sistema di *Trait Evolution* modella proprio questo: la personalità non è fissa, si trasforma con l'esposizione.

#### 2.2 Il Sistema Decisionale

Durante la simulazione, ogni agente affronta eventi narrativi basati su situazioni reali (raccolte da testimonianze e letteratura). Per ogni evento, l'agente può scegliere tra quattro strategie:

- **COMPLIANCE** — assecondare le richieste, anche quando sono irragionevoli
- **RESISTANCE** — opporsi apertamente
- **NEGOTIATION** — cercare un compromesso
- **ESCAPE** — ritirarsi, fisicamente o psicologicamente

Non c'è una scelta "giusta". Ognuna ha effetti diversi su stress, energia, salute, integrità, autostima e rapporti con colleghi e manager. La COMPLIANCE paga sul breve termine (il manager ti vede bene) ma erode l'integrità e accumula stress. La RESISTANCE preserva i valori ma rischia l'isolamento.

Il punto è che le conseguenze non sono deterministiche: dipendono dal profilo dell'agente, dai parametri HR impostati, e dai tratti del manager. È un sistema "a strati" che cerca di riprodurre la complessità di un ambiente reale senza pretese di realismo assoluto.

#### 2.3 Le Fazioni

Gli agenti si aggregano spontaneamente in tre fazioni:

- **Fedelissimi** — allineati al management, strategia prevalente: COMPLIANCE
- **Gruppo Silenzioso** — cercano di sopravvivere senza farsi notare, strategie miste
- **Ribelli** — opposizione aperta, strategia prevalente: RESISTANCE

L'appartenenza a una fazione non è solo estetica: gli agenti con forte legame di fazione beneficiano di una riduzione dello stress (il supporto sociale come ammortizzatore), mentre gli isolati vengono penalizzati. È un modo per modellare quella che nella tesina discuto come *capitale sociale* bourdieusiano.

---

### 3. Il Jump System: L'Osservatore che Entra nel Gioco

La feature forse più interessante, dal punto di vista metodologico, è il **Jump System**. Funziona così: nella modalità Laboratorio, l'utente non si limita a osservare i dati aggregati (stress medio, giorni di sopravvivenza, distribuzione profili). Può "possedere" un agente alla volta, fare scelte per lui, seguirne il percorso. Poi può saltare a un altro agente, e poi a un altro ancora.

Il sistema traccia questi salti e costruisce un profilo dell'osservatore stesso: chi sei? Un esploratore (salti su molti agenti diversi)? Uno stress-avoider (preferisci agenti tranquilli)? Uno selettivo (torni sempre sugli stessi)?

Questa è, in piccolo, l'idea dell'*osservazione partecipante digitale* che discuto nella tesina. L'osservatore non è neutrale: le sue scelte di "possesso" influenzano i dati, e i suoi bias diventano parte dell'analisi. Il Jump System è un tentativo di rendere visibile questa soggettività del ricercatore, invece di nasconderla sotto il mantello dell'oggettività statistica.

---

### 4. La Dashboard e le Metriche di "Salute Organizzativa"

Alla fine di ogni simulazione (o in qualsiasi momento, attraverso la dashboard analytics), si possono vedere i dati aggregati: distribuzione delle scelte per categoria, finali ottenuti, giorni di sopravvivenza media, evoluzione dei profili psicologici nello sciame.

La metrica più interessante è quella che chiamiamo **biodiversità psicologica**. L'idea — che riprendo dal discorso sull'*Antropocene della prestazione* nella tesina — è che un'organizzazione sana non è quella in cui tutti sono Performanti o tutti sono Cinici. È quella in cui profili diversi possono coesistere: Idealisti, Protettori, Negotiatori, Sopravvissuti. Quando la biodiversità crolla e un solo profilo domina lo sciame, l'ecosistema organizzativo è prossimo al collasso.

Il Laboratorio HR permette di testare policy proprio su questo: aumentare la trasparenza riduce la resistenza? La pressione alta favorisce davvero i Performanti o crea più Cinici? Modificare la coesione sociale cambia la distribuzione dei profili?

---

### 5. Limiti e Possibilità Future

BurnoutSimulator è un prototipo, non uno strumento di diagnosi organizzativa certificato. I suoi limiti sono evidenti: le psicologie sono modellate su tratti fissi e categorie discrete (che pure evolvono), gli eventi sono scritti a mano, il numero di agenti nello sciame è limitato. Nessuno pretenderebbe di usarlo per fare assessment aziendali reali.

Ma non è quello il suo scopo. Il simulatore è nato come un modo per *rendere tangibili* delle dinamiche astratte, per dare forma narrativa e interattiva a concetti antropologici che altrimenti restano sulla pagina. È un caso studio che prova a mettere in pratica ciò che la tesina discute in teoria: l'idea che il lavoro contemporaneo produca specifiche forme di sofferenza, che esistano strategie di resistenza e adattamento, che la personalità non sia un dato immutabile ma qualcosa che si trasforma nel tempo in relazione all'ambiente.

Se funziona, è perché qualcuno che ci gioca — uno studente, un HR curioso, un manager con un briciolo di autocoscienza — si ferma un attimo e pensa: *ah, quindi è così che ci si sente. Quindi è così che si arriva al burnout. Quindi è così che si diventa cinici.*

E quello, per un progetto di tesi, forse basta.

---

### Riferimenti alla Tesina

I collegamenti teorici principali sono sviluppati nel documento [*Analisi Antropologica — BurnoutSimulator*](./anthropological/analisi_antropologica.md), che costituisce il quadro teorico di riferimento. In particolare:

- La **trasformazione dell'habitus** (Bourdieu) è modellata dal sistema di Trait Evolution
- Il **panopticon digitale** (Foucault) trova forma nel GCD e nella sorveglianza interiorizzata
- La **liminalità** (Turner) descrive i momenti di crisi e transizione degli agenti
- La **biodiversità psicologica** si ispira alla critica dell'Antropocene della prestazione (Han)
- Il **Jump System** traduce in pratica l'etnografia multisituata (Marcus) e la thick description (Geertz)

Questo documento ne rappresenta invece la traduzione operativa: un caso studio che usa la simulazione come dispositivo di indagine antropologica, senza la pretesa di sostituirsi all'etnografia "sul campo", ma offrendo uno strumento complementare per l'analisi delle culture organizzative.

---

*BurnoutSimulator v3.2 — Progetto per tesina magistrale in HR — Antropologia delle Organizzazioni, Sapienza Università di Roma*
