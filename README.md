# BurnoutSimulator

**BurnoutSimulator** è un gioco di simulazione testuale sviluppato in Python, progettato per esplorare le dinamiche delle culture aziendali tossiche attraverso la lente dell'antropologia organizzativa.

Il progetto è stato concepito come strumento didattico e di ricerca per una tesina magistrale in HR presso l'Università Sapienza di Roma.

## Concept Antropologico

Il gioco mette il giocatore nei panni di un neoassunto in un'azienda caratterizzata da dinamiche malsane, ispirate a ricerche recenti e standard di qualità organizzativa (ISO 9001). Le categorie di tossicità esplorate includono:

- **Cultura aziendale problematica**: Mancanza di trasparenza, competizione interna malsana, favoritismi e nepotismo.
- **Gestione inadeguata**: Leadership autoritaria o assente, micromanagement, mancanza di vision e obiettivi chiari.
- **Problemi di Work-Life Balance**: Cultura dell'overwork, aspettative irrealistiche (disponibilità 24/7) e mancanza di flessibilità.
- **Problemi Etici e Comportamentali**: Pratiche poco etiche, discriminazioni e molestie tollerate.
- **Comunicazione Carente**: Discrepanza tra immagine pubblica (es. social media) e realtà interna.

L'obiettivo è osservare come diverse strategie di adattamento influenzano il benessere e la carriera:
- **COMPLIANCE** (Conformismo/Adattamento passivo)
- **RESISTANCE** (Resistenza attiva/Dissenso)
- **NEGOTIATION** (Negoziazione/Mediazione)
- **ESCAPE** (Fuga/Ricerca di alternative)

## Caratteristiche Tecniche

- **Motore di Gioco Leggero**: Sviluppato in Python puro senza dipendenze esterne.
- **Grafo delle Decisioni**: Tracciamento di ogni scelta in un grafo pesato per analisi statistica.
- **Profilazione Finale**: Al termine della partita, il gioco genera un profilo comportamentale basato sulle scelte effettuate.
- **Esportazione Sessioni**: Salvataggio in JSON per analisi dei dati.

## Come Giocare

1. Assicurati di avere Python 3 installato.
2. Clona il repository.
3. Esegui il gioco:
   ```bash
   python3 main.py
   ```

## Struttura del Progetto

- `main.py`: Punto di ingresso e interfaccia utente.
- `game/`:
    - `engine.py`: Logica centrale.
    - `player.py`: Gestione statistiche.
    - `events.py`: Gestione scenari.
    - `graph.py`: Tracciamento decisioni.
    - `save_manager.py`: Sistema di salvataggio.
    - `data/events.json`: Database degli eventi (espandibile).

---
*Progetto realizzato per scopi accademici - Tesina di Antropologia delle Organizzazioni.*
