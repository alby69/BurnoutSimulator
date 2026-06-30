# BurnoutSimulator

**BurnoutSimulator** è un gioco di simulazione testuale sviluppato in Python, progettato per esplorare le dinamiche delle culture aziendali tossiche attraverso la lente dell'antropologia organizzativa.

Il progetto è stato concepito come strumento didattico e di ricerca per una tesina magistrale in HR presso l'Università Sapienza di Roma.

## Concept Antropologico

Il gioco mette il giocatore nei panni di un neoassunto in un'azienda caratterizzata da:
- **Micromanagement**: controllo eccessivo e mancanza di autonomia.
- **Favoritismo**: avanzamento basato su relazioni personali piuttosto che sul merito.
- **Mobbing**: umiliazioni pubbliche e comportamenti ostili.
- **Burnout**: aspettative irrealistiche e mancanza di equilibrio vita-lavoro.

L'obiettivo non è solo "vincere", ma osservare come diverse strategie di adattamento (**Compliance**, **Resistance**, **Negotiation**, **Escape**) influenzano il benessere del dipendente e la sua traiettoria professionale.

## Caratteristiche Tecniche

- **Motore di Gioco Leggero**: Sviluppato in Python puro senza dipendenze esterne.
- **Grafo delle Decisioni**: Ogni scelta viene tracciata in un grafo pesato, permettendo l'analisi statistica delle decisioni più frequenti.
- **Sistema di Statistiche**: Gestione di 8 parametri chiave (Energia, Umore, Reputazione, Assertività, Resilienza, ecc.).
- **Esportazione Sessioni**: I dati di gioco vengono salvati in formato JSON per analisi post-partita.

## Come Giocare

1. Assicurati di avere Python 3 installato.
2. Clona il repository.
3. Esegui il gioco con il comando:
   ```bash
   python3 main.py
   ```

## Struttura del Progetto

- `main.py`: Punto di ingresso del gioco.
- `game/`:
    - `engine.py`: Logica centrale e gestione dei turni.
    - `player.py`: Gestione delle statistiche del personaggio.
    - `events.py`: Caricamento e gestione degli scenari narrativi.
    - `graph.py`: Tracciamento del grafo decisionale.
    - `save_manager.py`: Sistema di salvataggio sessioni.
    - `data/events.json`: Database degli eventi tossici.

## Finali Possibili

- **Burnout**: Esaurimento totale dell'energia.
- **Licenziamento**: Perdita totale della reputazione aziendale.
- **Quiet Quitting**: Il morale scende sotto la soglia critica.
- **Promozione**: Alta reputazione e preparazione tecnica.
- **Sopravvivenza**: Raggiungimento del limite di tempo (365 giorni).

---
*Progetto realizzato per scopi accademici - Tesina di Antropologia delle Organizzazioni.*
