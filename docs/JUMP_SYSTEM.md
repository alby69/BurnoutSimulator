# Sistema di Possesso (Jump System) — BurnoutSimulator v3.0

## Panoramica
Il Jump System è il cuore del Social Laboratory. Permette a un giocatore umano di:
- Osservare uno sciame di 6 agenti autonomi che giocano simultaneamente
- Possedere un agente in qualsiasi momento, prendendo il controllo delle sue decisioni
- Saltare tra gli agenti, costruendo un profilo psicologico emergente
- Analizzare il proprio comportamento attraverso dashboard e radar chart

## Architettura del Sistema

```plain
+-------------------------------------------------------------------------+
|                         GIOCATORE UMANO                                 |
|  +--------------+    +--------------+    +--------------------------+   |
|  |  HumanPlayer |--->|  JumpRecord  |--->|  Emergent Profile      |   |
|  |  (traccia)   |    |  (storico)   |    |  (radar analytics)     |   |
|  +--------------+    +--------------+    +--------------------------+   |
+-------------------------------------------------------------------------+
                                    |
                                    | possess / release / jump_to
                                    v
+-------------------------------------------------------------------------+
|                      AGENT SWARM (6 agenti)                             |
|  +---------+ +---------+ +---------+ +---------+ +---------+ +------+|
|  | Agent 1 | | Agent 2 | | Agent 3 | | Agent 4 | | Agent 5 | |Agent 6||
|  | (auto)  | | (auto)  | |(possess)| | (auto)  | | (auto)  | |(auto)||
|  +---------+ +---------+ +---------+ +---------+ +---------+ +------+|
|       |           |           |           |           |          |      |
|       +-----------+-----------+-----------+-----------+----------+      |
|                                    |                                    |
|                                    v                                    |
|                         +---------------------+                         |
|                         |   AgentSwarm        |                         |
|                         |   (coordinatore)    |                         |
|                         +---------------------+                         |
+-------------------------------------------------------------------------+
```

## Componenti

### 1. HumanPlayer (human/human_player.py)
Traccia il percorso psicologico del giocatore umano.

**Attributi principali:**
- `human_id`: UUID univoco del giocatore
- `jump_history`: lista di `JumpRecord` — ogni salto è tracciato
- `current_agent_id`: agente attualmente posseduto
- `preferred_categories`: conteggio delle categorie scelte (COMPLIANCE, RESISTANCE, ecc.)
- `psychological_trace`: timeline completa di azioni e salti

**Metodi chiave:**
- `jump_to(from_agent_id, to_agent_id, from_day, to_day, reason=None, declared_mood=None)`
  Esegue un salto da un agente a un altro. Registra:
    - `from_agent_id`: agente che si sta abbandonando
    - `to_agent_id`: agente che si sta possedendo
    - `from_day` / `to_day`: giorni di gioco (per calcolo durata)
    - `reason`: motivazione opzionale del salto
    - `declared_mood`: stato emotivo dichiarato (Stressato, Arrabbiato, ecc.)
- `record_choice_made(agent_id, choice_category, day)`
  Aggiorna il profilo emergente quando l'umano fa una scelta.
- `get_emergent_profile() -> Dict`
  Calcola il profilo psicologico emergente:
    - `dominant_category`: categoria più scelta
    - `category_distribution`: percentuale per categoria (radar chart)
    - `total_jumps`: numero totale di salti
    - `unique_agents_played`: quanti agenti diversi
    - `avg_stay_duration`: durata media possesso (in giorni)
    - `jump_pattern`: pattern comportamentale (stress_avoider, explorer, selective)

### 2. Agent (agents/agent.py)
Ogni agente può giocare in autonomia o essere posseduto.

**Stato di possesso:**
```python
is_possessed: bool = False       # True se un umano controlla
possessed_by: Optional[str] = None   # ID umano
possession_history: List[Dict] = []   # Storico possessi
```

**Metodi chiave:**
- `possess(human_id: str) -> Dict`
  Attiva il possesso. Registra:
    - timestamp inizio
    - snapshot dello stato al momento del possesso
    - inizializza lista decisioni umane
- `release(human_id: str)`
  Rilascia il possesso. Chiude il record di `possession_history`.
- `human_chooses(choice_idx: int, human_id: str) -> bool`
  Registra una scelta umana:
    - Salva nella memoria come decisione NON automatica
    - Aggiunge al `possession_history` attuale
    - Esegue la scelta nel GameEngine
- `auto_play_turn() -> Optional[Any]`
  Se NON posseduto, l'agente gioca automaticamente usando il profilo psicologico.

### 3. AgentSwarm (agents/swarm.py)
Coordinatore centrale del laboratorio.

**Metodi chiave:**
- `register_human(name: str) -> HumanPlayer`
  Crea un nuovo giocatore umano nel laboratorio.
- `possess_agent(human_id, agent_id, reason=None) -> Dict`
  Flusso completo di possesso:
    - Rilascia agente precedente (se esiste, gestito internamente)
    - Registra il salto in `HumanPlayer.jump_history`
    - Attiva possesso sull'agente
    - Restituisce stato aggiornato
- `human_make_choice(human_id, choice_idx) -> Dict`
  L'umano fa una scelta per l'agente posseduto:
    - Verifica possesso valido
    - Esegue scelta tramite `agent.human_chooses()`
    - Aggiorna profilo umano con `record_choice_made()`
    - **Nota:** Il turno NON viene avanzato qui; è gestito da `_show_choice_feedback()`/`advance()` per garantire consistenza con la modalità classica
- `run_simulation_step() -> Dict`
  Fa avanzare tutti gli agenti NON posseduti di un turno.
- `get_laboratory_view(human_id) -> Dict`
  Vista d'insieme per la UI del laboratorio.
- `_calculate_match_score(human_id, agent) -> int`
  Calcola affinità umano-agente (0-100) basata su:
    - Categorie preferite dall'umano vs bias dell'agente
    - Penalità per agenti già provati (favorisce esplorazione)

### 4. UI — Flusso di Possesso (app.py)

**Schermata Iniziale -> Laboratorio**
```plain
+---------------------------------------------+
|  BURNOUT SIMULATOR                          |
|                                             |
|  [INIZIA CARRIERA]  <- Modalità classica    |
|  [ENTRA NEL LABORATORIO]  <- Modalità v3.0    |
+---------------------------------------------+
```

**Vista Laboratorio**
```plain
+---------------------------------------------------------------------+
|  LABORATORIO AGENTI          Osserva, scegli, salta.                 |
+---------------------------------------------------------------------+
|  STRESS MEDIO: 45%  |  ARCHETIPO CRITICO: Startup  |  AGENTI: 6/6  |
+---------------------------------------------------------------------+
|  IL TUO PERCORSO PSICOLOGICO (Radar Chart)                          |
|  3 salti . 2 agenti                                                 |
+---------------------------------------------------------------------+
| +-------------+ +-------------+ +-------------+                       |
| | Il Performante| | Il Protettore | | Il Sopravvissuto|             |
| | #1          | | #2          | | #3            |             |
| | o Stress 60%| | o Stress 30%| | o Stress 20%  |             |
| | o Energia 40%| | o Energia 70%| | o Energia 80% |             |
| | o Salute 80%| | o Salute 90%| | o Salute 95%  |             |
| |             | |             | |               |             |
| | Fazione: Fed.| | Fazione: Reb.| | Fazione: Gr.S.|             |
| | Affinità: 75%| | Affinità: 45%| | Affinità: 30% |             |
| |             | |             | |               |             |
| | [Possiedi]  | | [Possiedi]  | | [TUO] [Continua]|            |
| | [Dettagli]  | | [Dettagli]  | | [Dettagli]    |             |
| +-------------+ +-------------+ +-------------+                       |
| ... (altri 3 agenti)                                                |
+---------------------------------------------------------------------+
|  [> Avanza 1 turno]  [>> Avanza 5 turni]  [Pausa]                   |
+---------------------------------------------------------------------+
```

**Durante il Possesso (Modalità Gioco)**
```plain
+---------------------------------------------------------------------+
|  POSSESSO AGENTE: Il Performante #1        [SALTA] [LABORATORIO]     |
+---------------------------------------------------------------------+
|  (Interfaccia gioco standard con banner viola in alto)             |
|                                                                     |
|  GIORNO 12  |  Startup Caotica  |  Evento 3/45                     |
|                                                                     |
|  [Marco]    +------------------------------------------+            |
|  (avatar)   |  "Il manager ti chiede di lavorare      |            |
|             |   nel weekend per una scadenza..."       |            |
|             +------------------------------------------+            |
|                                                                     |
|  PRENDI UNA DECISIONE                                               |
|  +--------------------------------------------------------------+   |
|  | A. Accetti, ma chiedi il giorno libero lunedì               |   |
|  |    Stress: +2 | Energia: -3 | Rep.Manager: +3              |   |
|  +--------------------------------------------------------------+   |
|  | B. Rifiuti categoricamente ⏱ 15s                            |   |
|  |    Stress: +5 | Integrità: +5 | Rep.Manager: -5             |   |
|  +--------------------------------------------------------------+   |
|  | C. Trovi una scappatoia tecnica                              |   |
|  |    Stress: +1 | Occupabilità: +2                             |   |
|  +--------------------------------------------------------------+   |
+---------------------------------------------------------------------+
```

**Dialog di Salto**
```plain
+---------------------------------------------------------------------+
|  SALTA A UN ALTRO AGENTE                                           |
|                                                                     |
|  Come ti senti in questo momento?                                   |
|  +----------------------------------------+                         |
|  | [Stressato v]                         |                         |
|  +----------------------------------------+                         |
|                                                                     |
|  +--------------------------------------------------------------+   |
|  | Il Protettore #2                                              |   |
|  | Giorno 8 . Corporate Tossica                                  |   |
|  | Affinità: 62%                                                 |   |
|  |                                          [SALTA QUI]          |   |
|  +--------------------------------------------------------------+   |
|  +--------------------------------------------------------------+   |
|  | Il Sopravvissuto #3                                           |   |
|  | Giorno 15 . Azienda Familiare                                 |   |
|  | Affinità: 38%                                                 |   |
|  |                                          [SALTA QUI]          |   |
|  +--------------------------------------------------------------+   |
|                                                                     |
|                                          [Annulla]                  |
+---------------------------------------------------------------------+
```

## Flusso Dettagliato del Possesso

### Primo possesso
```python
# 1. Utente clicca "ENTRA NEL LABORATORIO"
start_lab_cb():
    human = swarm.register_human(name="Osservatore")
    current_human_id = human.human_id
    screen = "laboratory"

# 2. Utente clicca "Possiedi" su un agente
_start_possession(agent_id):
    result = swarm.possess_agent(current_human_id, agent_id)
    current_agent_id = agent_id
    engine = swarm.agents[agent_id].engine
    session_id = f"possession_{agent_id}_{uuid}"
    screen = "game"

# 3. In swarm.possess_agent():
#    a. Rilascia agente precedente (se c'è)
#    b. human.jump_to(from, to, from_day, to_day, reason)
#    c. agent.possess(human_id)
#    d. Restituisce stato aggiornato
```

### Salto tra agenti
```python
# 1. Utente clicca "SALTA" nel banner di gioco
_render_jump_dialog():
    # Mostra dialog con:
    # - Mood selector (opzionale)
    # - Lista agenti disponibili con match score
    # - Filtro: esclude l'agente attualmente posseduto (current_agent_id)
    # - Pulsante "SALTA QUI" per ogni agente

# 2. Utente seleziona agente e mood
_execute_jump(to_agent_id, mood, dialog):
    # a. Possess nuovo agente (possess_agent gestisce internamente
    #    il rilascio dell'agente precedente — nessun doppio rilascio)
    if not current_human_id:
        ui.notify("Nessun umano registrato.", type="warning")
        return
    result = swarm.possess_agent(current_human_id, to_agent_id,
                                  reason=f"Salto emotivo: {mood}")

    # b. Aggiorna stato globale
    if result.get("success"):
        current_agent_id = to_agent_id
        engine = swarm.agents[to_agent_id].engine
        session_id = f"possession_{to_agent_id}_{uuid}"
        dialog.close()
        page.refresh()
```

### Decisione durante il possesso
```python
# Utente clicca una scelta
_make_choice(idx, event, choice):
    if current_agent_id and current_human_id:
        # Modalità laboratorio
        res = swarm.human_make_choice(current_human_id, idx)
        # Questo internamente:
        # 1. agent.human_chooses(idx, human_id) -> esegue scelta
        # 2. human.record_choice_made(agent_id, category, day) -> aggiorna profilo
        # 3. Salva stato agente (turno NON avanzato qui)
        #
        # L'avanzamento turno è gestito da advance() in _show_choice_feedback(),
        # identico per modalità classica e possesso.
    else:
        # Modalità classica
        engine.handle_choice(idx)
```

## Profilo Psicologico Emergente
Il sistema calcola automaticamente il profilo dell'osservatore basandosi su:

### Metriche
| Metrica | Descrizione | Calcolo |
|---------|-------------|---------|
| `dominant_category` | Categoria scelta più spesso | `max(preferred_categories)` |
| `category_distribution` | Percentuale per categoria | `count / total x 100` |
| `total_jumps` | Numero di salti effettuati | `len(jump_history)` |
| `unique_agents_played` | Agenti diversi provati | `len(set(j.to_agent_id))` |
| `avg_stay_duration` | Durata media possesso | media giorni per salto |
| `jump_pattern` | Pattern comportamentale | Analisi euristica |

### Pattern Riconosciuti
| Pattern | Condizione | Significato |
|---------|------------|-------------|
| `stress_avoider` | >50% salti dichiarano mood "Stressato" | Evita lo stress, cerca agenti più tranquilli |
| `explorer` | >70% salti su agenti diversi | Curioso, vuole provare tutte le prospettive |
| `selective` | Default | Sceglie con criterio, ritorna su preferiti |

### Esempio di Profilo Emergente
```json
{
  "dominant_category": "RESISTANCE",
  "category_distribution": {
    "COMPLIANCE": 15.0,
    "RESISTANCE": 55.0,
    "NEGOTIATION": 20.0,
    "ESCAPE": 10.0
  },
  "total_jumps": 5,
  "unique_agents_played": 4,
  "avg_stay_duration": 3.2,
  "jump_pattern": "explorer"
}
```

## Match Score (Affinità Umano-Agente)
Calcolato in `AgentSwarm._calculate_match_score()`:
```plain
Score base: 50

+ (resistance_bias - 30) / 2    se umano preferisce RESISTANCE
+ (compliance_bias - 50) / 2     se umano preferisce COMPLIANCE
+ (escape_bias - 20) / 2         se umano preferisce ESCAPE
- 10                             se agente già provato

Clamped a [0, 100]
```

| Range | Colore | Significato |
|-------|--------|-------------|
| 70-100 | Verde | Alta affinità — stile decisionale simile |
| 40-69 | Giallo | Affinità media |
| 0-39 | Grigio | Bassa affinità — stile molto diverso |

## Memoria degli Agenti
Ogni agente mantiene una memoria storica (`agents/memory.py`):
```python
class AgentMemory:
    decisions: List[DecisionRecord]       # Tutte le decisioni
    choice_outcomes: Dict[str, List]      # Esiti per ogni choice_id
    event_frequency: Dict[str, int]       # Conteggio eventi
    category_frequency: Dict[str, int]    # Conteggio categorie
```

**Uso nell'apprendimento:**
- `_apply_memory_weights()` in `agent.py` penalizza scelte che in passato hanno causato stress
- Se una scelta ha `avg_stress_change > 5`, il peso viene ridotto del 30%
- Se una scelta ha `avg_stress_change < -3`, il peso viene aumentato del 30%

## API del Sistema di Possesso
Per sviluppatori che vogliono estendere

```python
from agents.swarm import AgentSwarm
from human.human_player import HumanPlayer

# Creare uno sciame
swarm = AgentSwarm(num_agents=6)

# Registrare un umano
human = swarm.register_human("Nome Giocatore")

# Possedere un agente
result = swarm.possess_agent(human.human_id, "agent_abc123")
# result = {
#   "success": True,
#   "agent_state": { ... },
#   "human_profile": { ... }
# }

# Far fare una scelta all'umano
result = swarm.human_make_choice(human.human_id, choice_index=1)
# result = {
#   "success": True,
#   "next_event": Event(...),
#   "stats": { ... },
#   "is_game_over": False
# }

# Far avanzare gli agenti automatici
swarm.run_simulation_step()

# Ottenere vista laboratorio
view = swarm.get_laboratory_view(human.human_id)
# view = {
#   "total_agents": 6,
#   "alive_agents": 5,
#   "possessed_agents": 1,
#   "agents": [ ... ],
#   "human_profile": { ... }
# }

# Ottenere dettagli di un agente
details = swarm.get_agent_detailed_view("agent_abc123")
# details = {
#   "agent": { ... },
#   "memory_summary": { ... },
#   "possession_history": [ ... ]
# }
```

## Limitazioni Note
- **Persistenza:** Il database `agents.db` ha lo schema ma non le funzioni di scrittura. I dati del laboratorio si perdono al riavvio dell'app. *(RISOLTO in v3.1)*
- **Multi-utente:** Lo sciame è globale (variabile globale in `app.py`). Più utenti condividono gli stessi agenti.
- **Auto-play:** Gli agenti non posseduti non avanzano automaticamente; l'utente deve cliccare "Avanza N turni" nel laboratorio.
- **Outcomes:** `memory.record_outcome()` esiste ma non viene mai chiamato. Gli agenti non apprendono dagli esiti reali. *(RISOLTO in v3.1)*
- **Stato UI:** I pulsanti nella UI (SALTA, Possiedi, LABORATORIO, avanzamento turno) sono stati corretti in v3.1.2 per garantire comportamenti coerenti e impedire doppi avanzamenti o doppi rilasci.

## Estensioni Consigliate

### Aggiungere persistenza
Aggiungere funzioni in `agent_db.py`: `save_agent()`, `save_decision()`, `save_jump()`, `save_human_profile()`. Chiamarle in `swarm.py` dopo ogni turno/salto. *(Implementato in v3.1)*

### Aggiungere auto-play periodico
In `app.py`, dopo ogni scelta umana:
```python
ui.timer(30.0, lambda: swarm.run_simulation_step() or page.refresh())
```

### Aggiungere conseguenze del salto
In `Agent.release()` aggiungere:
```python
if self.engine:
    self.engine.player.stress = min(100, self.engine.player.stress + 5)
    self.engine.player.self_esteem = max(0, self.engine.player.self_esteem - 3)
```

---
Documento aggiornato per BurnoutSimulator v3.0 — Social Laboratory
