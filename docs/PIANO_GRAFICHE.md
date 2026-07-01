# PIANO INTEGRAZIONE GRAFICHE — Burnout Simulator (IMPLEMENTATO)

## Struttura finale asset

```
static/images/                          ← Servito via app.add_static_files('/static/images', 'static/images')
├── personaggi/                         ← 22 ritratti NPC + emote
│   ├── CORP_Manager_Passivo_Aggressivo.png
│   ├── CORP_Collega_Favorito_Arrogante.png
│   ├── CORP_Dipendente_Senior_Cinico.png
│   ├── CORP_HR_Falsa_Empatia.png
│   ├── CORP_Soddisfazione_Cinica.png   (usato anche come emote COMPLIANCE)
│   ├── CORP_Neoassunto_Confuso.png     (usato anche come emote NEGOTIATION)
│   ├── CORP_Sorpresa_Ufficio.png       (usato anche come emote ESCAPE)
│   ├── CORP_Dipendente_Stressato.png   (usato anche come emote RESISTANCE)
│   └── ... (14 altri)
├── eventi/                             ← 12 icone eventi aziendali
│   ├── CORP_EVENTO_Licenziamento.png
│   ├── CORP_EVENTO_Riunione_Inutile.png
│   ├── CORP_EVENTO_Email_Fuori_Orario.png
│   └── ... (9 altri)
└── stati/                              ← 5 icone stati burnout
    ├── CORP_STATO_BURNOUT.png
    ├── CORP_STATO_Crollo_Nervoso.png
    ├── CORP_STATO_Rivolta_Silenziosa.png
    ├── CORP_STATO_Cinismo_Galoppante.png
    └── CORP_STATO_Realizzazione_Brutale.png
```

## Cosa è stato implementato

| Fase | Descrizione | Stato |
|------|-------------|-------|
| **F1** | CSS Overhaul (gradienti, card VN, tema) | ✅ |
| **F2** | Facce SVG dinamiche (6 espressioni) | ✅ Sostituito da F4 |
| **F3** | Layout Visual Novel (portrait + card) | ✅ |
| **F4** | PNG portraits → sostituito SVG inline | ✅ 22 CORP_* immagini |
| **F5** | Event icons nella narrative card | ✅ 12 icone mappate per ID evento |
| **F6** | State icons nella sidebar + game over | ✅ 5 icone STATO |
| **F7** | Emote overlay su portrait scelte | ✅ 4 emote per categoria |
| **F8** | Label effetti in italiano | ✅ EFFECT_LABELS mapping |
| **F9** | Help system integrato | ✅ Dialog esplicativo in 7 sezioni |

## Classificazione icone

### Personaggi — 6 gruppi emotivi

| Gruppo | Immagini |
|--------|----------|
| **Neoassunto** | Sereno, Confuso |
| **Esausto** | Stanco, Stressato, Rassegnato, Deluso, Sconvolto, Spento |
| **Critico** | Burnout Cronico, Scioccato, Senior Cinico |
| **Manager tossico** | Passivo-Aggressivo, Capo Arrabbiato, Direttore Furioso |
| **Corporate tossico** | CEO Minaccioso, HR Falsa Empatia, Collega Arrogante, Sabotatore |
| **Ironico** | Soddisfazione Cinica, Sorpresa Ufficio |

### Emote per categoria scelta

| Categoria | Immagine |
|-----------|----------|
| COMPLIANCE | `CORP_Soddisfazione_Cinica.png` |
| RESISTANCE | `CORP_Dipendente_Stressato.png` |
| NEGOTIATION | `CORP_Neoassunto_Confuso.png` |
| ESCAPE | `CORP_Sorpresa_Ufficio.png` |

## Mappa sostituzioni codice

| Funzione vecchia | Funzione nuova | File |
|------------------|----------------|------|
| `_npc_svg_face()` | `_npc_portrait()` | `app.py` |
| `f"{k[:3].upper()}"` (mini-events) | `_effect_label(k)[:6]` | `app.py` |
| `f"{ek}: ..."` (choice chips) | `_effect_label(ek)` | `app.py` |
| `f"{effect_key}: ..."` (tooltip) | `_effect_label(effect_key)` | `app.py` |
| Nessuno (help) | `_show_help()` | `app.py` |
