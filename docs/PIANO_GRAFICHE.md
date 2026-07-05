# PIANO INTEGRAZIONE GRAFICHE — Burnout Simulator (IMPLEMENTATO)

## Struttura finale asset

```
static/images/                          ← 39 PNG totali
├── personaggi/                         ← 22 ritratti NPC
│   ├── CORP_Capo_Arrabbiato.png
│   ├── CORP_CEO_Sorridente_Minaccioso.png
│   ├── CORP_Collega_Favorito_Arrogante.png
│   ├── CORP_Collega_Tossico_Sabotatore.png
│   ├── CORP_Dipendente_Burnout_Cronico.png
│   ├── CORP_Dipendente_Deluso.png
│   ├── CORP_Dipendente_Rassegnato.png
│   ├── CORP_Dipendente_Scioccato.png
│   ├── CORP_Dipendente_Sconvolto.png
│   ├── CORP_Dipendente_Senior_Cinico.png
│   ├── CORP_Dipendente_Sonnolento.png
│   ├── CORP_Dipendente_Spento.png
│   ├── CORP_Dipendente_Stanco.png
│   ├── CORP_Dipendente_Stressato.png   (usato anche come emote RESISTANCE)
│   ├── CORP_Direttore_Furioso.png
│   ├── CORP_HR_Falsa_Empatia.png
│   ├── CORP_Manager_Passivo_Aggressivo.png
│   ├── CORP_Neoassunto_Confuso.png     (usato anche come emote NEGOTIATION)
│   ├── CORP_Neoassunto_Sereno.png
│   ├── CORP_Soddisfazione_Cinica.png   (usato anche come emote COMPLIANCE)
│   ├── CORP_Sorpresa_Ufficio.png       (usato anche come emote ESCAPE)
│   └── CORP_Team_Lead_Pressante.png
├── eventi/                             ← 12 icone eventi aziendali
│   ├── CORP_EVENTO_Bonus_Rifiutato.png
│   ├── CORP_EVENTO_Corso_Formazione_Inutile.png
│   ├── CORP_EVENTO_Dimissioni_Impossibili.png
│   ├── CORP_EVENTO_Email_Fuori_Orario.png
│   ├── CORP_EVENTO_Feedback_Anonimo_Trasparente.png
│   ├── CORP_EVENTO_Festa_Aziendale_Obbligatoria.png
│   ├── CORP_EVENTO_Licenziamento.png
│   ├── CORP_EVENTO_Pausa_Caffe_Obbligatoria.png
│   ├── CORP_EVENTO_Promozione_Finta.png
│   ├── CORP_EVENTO_Riunione_Inutile.png
│   ├── CORP_EVENTO_Straordinario_Forzato.png
│   └── CORP_EVENTO_Team_Building_Forzato.png
└── stati/                              ← 5 icone stati burnout
    ├── CORP_STATO_BURNOUT.png
    ├── CORP_STATO_Cinismo_Galoppante.png
    ├── CORP_STATO_Crollo_Nervoso.png
    ├── CORP_STATO_Realizzazione_Brutale.png
    └── CORP_STATO_Rivolta_Silenziosa.png
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

### Personaggi — 7 gruppi emotivi

| Gruppo | Immagini |
|--------|----------|
| **Neoassunto** | Sereno, Confuso |
| **Esausto** | Stanco, Stressato, Rassegnato, Deluso, Sconvolto, Spento, Sonnolento |
| **Critico** | Burnout Cronico, Scioccato, Senior Cinico |
| **Manager tossico** | Passivo-Aggressivo, Capo Arrabbiato, Direttore Furioso, Team Lead Pressante |
| **Corporate tossico** | CEO Sorridente Minaccioso, HR Falsa Empatia, Collega Favorito Arrogante, Collega Tossico Sabotatore |
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
