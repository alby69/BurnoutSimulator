import uuid, random, json, sqlite3, os, base64
from typing import Optional
from io import BytesIO
from nicegui import app, ui
from game.engine import (
    GameEngine,
    NPC_FACTION_MAP,
    MANAGER_PERSONALITIES,
    CAREER_PHASES,
)
from database.analytics import (
    init_db,
    create_session,
    end_session,
    record_choice,
    record_tags,
)
from database.agent_db import init_agent_db, save_agent, get_swarm_history
from game.events import Choice
from agents.swarm import AgentSwarm
from engine.analysis import StrategicAnalyzer

# ── State ──
screen: str = "start"
engine: GameEngine | None = None
session_id: str | None = None
swarm: AgentSwarm = AgentSwarm(num_agents=6)
swarm.load_swarm()
current_human_id: str | None = None
current_agent_id: str | None = None
# inspected_agent_id is now per-client to support multi-user safely
client_inspected_agent: dict[str, str] = {}
stats_before: dict = {}
choice_history: list = []
_tutorial_active: bool = False
_tutorial_step: int = 0
_timer_active: bool = False
_decision_start: float = 0.0
_layout_mode: str = "desktop"
_skip_tutorial: bool = False

bars_def = [
    ("Energia", "energy", "#4ade80"),
    ("Stress", "stress", "#f87171"),
    ("Salute", "health", "#22d3ee"),
    ("Integrità", "integrity", "#a78bfa"),
    ("Autostima", "self_esteem", "#fbbf24"),
    ("Occupabilità", "employability", "#34d399"),
    ("Rep. Manager", "manager_rep", "#fb923c"),
    ("Rep. Team", "team_rep", "#60a5fa"),
]

NPC_FACTION_COLORS = {
    "Fedelissimi": "#7c3aed",
    "Gruppo Silenzioso": "#64748b",
    "Ribelli": "#f87171",
}

ARCHETYPE_THEMES = {
    "Startup Caotica": {
        "accent": "#f97316",
        "header": "#ea580c",
        "badge": "warning",
        "glow": "0 0 25px rgba(249,115,22,0.3)",
    },
    "Corporate Tossica": {
        "accent": "#3b82f6",
        "header": "#2563eb",
        "badge": "primary",
        "glow": "0 0 25px rgba(59,130,246,0.3)",
    },
    "Azienda Familiare": {
        "accent": "#22c55e",
        "header": "#16a34a",
        "badge": "positive",
        "glow": "0 0 25px rgba(34,197,94,0.3)",
    },
    "Consulting": {
        "accent": "#a855f7",
        "header": "#9333ea",
        "badge": "secondary",
        "glow": "0 0 25px rgba(168,85,247,0.3)",
    },
}

AGENT_PROFILE_COLORS = {
    "Il Performante": "#f97316",
    "Il Protettore": "#ef4444",
    "Il Sopravvissuto": "#22c55e",
    "Il Negoziatore": "#eab308",
    "Il Cinico": "#64748b",
    "Il Manipolatore": "#ec4899",
    "L'Idealista": "#3b82f6",
}

cat_colors = {
    "COMPLIANCE": "#3b82f6",
    "RESISTANCE": "#ef4444",
    "NEGOTIATION": "#eab308",
    "ESCAPE": "#22c55e",
}

# ── Graphics ──
GRAPHICS_DIR = "static/images"
GFX_PATH = "/static/images"

NPC_DEFAULT = {
    "Marco": "CORP_Manager_Passivo_Aggressivo.png",
    "Giulia": "CORP_Collega_Favorito_Arrogante.png",
    "Roberto": "CORP_Dipendente_Senior_Cinico.png",
    "Elena": "CORP_HR_Falsa_Empatia.png",
}
NPC_SCARED = {
    "Marco": "CORP_Direttore_Furioso.png",
    "Giulia": "CORP_Dipendente_Sconvolto.png",
    "Roberto": "CORP_Dipendente_Scioccato.png",
    "Elena": "CORP_Dipendente_Spento.png",
}
NPC_ANGRY = {
    "Marco": "CORP_Capo_Arrabbiato.png",
    "Giulia": "CORP_Collega_Tossico_Sabotatore.png",
    "Roberto": "CORP_Team_Lead_Pressante.png",
    "Elena": "CORP_Dipendente_Deluso.png",
}
NPC_STRESSED = {
    "Marco": "CORP_Dipendente_Stressato.png",
    "Giulia": "CORP_Dipendente_Stressato.png",
    "Roberto": "CORP_Dipendente_Stanco.png",
    "Elena": "CORP_Dipendente_Spento.png",
}
NPC_WORRIED = {
    "Marco": "CORP_Dipendente_Deluso.png",
    "Giulia": "CORP_Dipendente_Spento.png",
    "Roberto": "CORP_Dipendente_Rassegnato.png",
    "Elena": "CORP_Dipendente_Spento.png",
}
NPC_HAPPY = {
    "Marco": "CORP_Soddisfazione_Cinica.png",
    "Giulia": "CORP_Neoassunto_Sereno.png",
    "Roberto": "CORP_Neoassunto_Confuso.png",
    "Elena": "CORP_Sorpresa_Ufficio.png",
}

EVENT_ICONS = {
    "riunione_inutile": "CORP_EVENTO_Riunione_Inutile.png",
    "esclusione_riunione": "CORP_EVENTO_Riunione_Inutile.png",
    "scadenza_impossibile": "CORP_EVENTO_Straordinario_Forzato.png",
    "compito_extra_non_pagato": "CORP_EVENTO_Straordinario_Forzato.png",
    "doppio_incarico": "CORP_EVENTO_Straordinario_Forzato.png",
    "messaggio_weekend": "CORP_EVENTO_Email_Fuori_Orario.png",
    "commento_reperibilita": "CORP_EVENTO_Email_Fuori_Orario.png",
    "reperibilita_forzata": "CORP_EVENTO_Email_Fuori_Orario.png",
    "capro_espiatorio": "CORP_EVENTO_Licenziamento.png",
    "ritorsione_manager": "CORP_EVENTO_Licenziamento.png",
    "appropriazione_idea": "CORP_EVENTO_Promozione_Finta.png",
    "progetto_premio": "CORP_EVENTO_Promozione_Finta.png",
    "taglio_benefit": "CORP_EVENTO_Bonus_Rifiutato.png",
    "cultura_presenza": "CORP_EVENTO_Festa_Aziendale_Obbligatoria.png",
    "pettegolezzi_ufficio": "CORP_EVENTO_Festa_Aziendale_Obbligatoria.png",
    "sabotaggio_progetto": "CORP_EVENTO_Team_Building_Forzato.png",
    "valutazione_ingiusta": "CORP_EVENTO_Feedback_Anonimo_Trasparente.png",
    "hr_risposta_elusiva": "CORP_EVENTO_Feedback_Anonimo_Trasparente.png",
    "richiamo_formale": "CORP_EVENTO_Corso_Formazione_Inutile.png",
    "commento_inappropriate": "CORP_EVENTO_Corso_Formazione_Inutile.png",
    "passaggio_generazionale": "CORP_EVENTO_Dimissioni_Impossibili.png",
    "commento_scarso_impegno": "CORP_EVENTO_Pausa_Caffe_Obbligatoria.png",
    "commento_agitazione_sindacale": "CORP_EVENTO_Pausa_Caffe_Obbligatoria.png",
}

STATE_ICONS = {
    "Burnout": "CORP_STATO_BURNOUT.png",
    "Crollo_Nervoso": "CORP_STATO_Crollo_Nervoso.png",
    "Rivolta_Silenziosa": "CORP_STATO_Rivolta_Silenziosa.png",
    "Cinismo_Galoppante": "CORP_STATO_Cinismo_Galoppante.png",
    "Realizzazione_Brutale": "CORP_STATO_Realizzazione_Brutale.png",
}

EMOTE_ICONS = {
    "COMPLIANCE": "CORP_Soddisfazione_Cinica.png",
    "RESISTANCE": "CORP_Dipendente_Stressato.png",
    "NEGOTIATION": "CORP_Neoassunto_Confuso.png",
    "ESCAPE": "CORP_Sorpresa_Ufficio.png",
}

EFFECT_LABELS = {
    "stress": "Stress",
    "energy": "Energia",
    "health": "Salute",
    "self_esteem": "Autostima",
    "manager_rep": "Rep. Manager",
    "team_rep": "Rep. Team",
    "integrity": "Integrità",
    "employability": "Occupabilità",
    "npc_Marco_trust": "Fiducia Marco",
    "npc_Marco_fear": "Paura Marco",
    "npc_Marco_respect": "Rispetto Marco",
    "npc_Giulia_trust": "Fiducia Giulia",
    "npc_Giulia_fear": "Paura Giulia",
    "npc_Giulia_respect": "Rispetto Giulia",
    "npc_Roberto_trust": "Fiducia Roberto",
    "npc_Roberto_fear": "Paura Roberto",
    "npc_Roberto_respect": "Rispetto Roberto",
    "npc_Elena_trust": "Fiducia Elena",
    "npc_Elena_fear": "Paura Elena",
    "npc_Elena_respect": "Rispetto Elena",
    "faction_Fedelissimi": "Fedelissimi",
    "faction_Gruppo Silenzioso": "Gruppo Silenzioso",
    "faction_Ribelli": "Ribelli",
}


def _effect_label(key: str) -> str:
    return EFFECT_LABELS.get(key, key.replace("_", " ").title())


def _npc_portrait(nname: str, ndata: dict) -> str:
    trust = ndata.get("trust", 50)
    fear = ndata.get("fear", 0)
    stress = getattr(engine, "player", None) and engine.player.stress or 0

    if fear > trust and fear > 40:
        img = NPC_SCARED.get(nname) or NPC_DEFAULT.get(
            nname, "CORP_Dipendente_Sconvolto.png"
        )
    elif trust < 30 and fear < 20:
        img = NPC_ANGRY.get(nname) or NPC_DEFAULT.get(
            nname, "CORP_Dipendente_Rassegnato.png"
        )
    elif stress > 70:
        img = NPC_STRESSED.get(nname) or NPC_DEFAULT.get(
            nname, "CORP_Dipendente_Stressato.png"
        )
    elif trust < 40:
        img = NPC_WORRIED.get(nname) or NPC_DEFAULT.get(
            nname, "CORP_Dipendente_Stanco.png"
        )
    elif trust >= 75:
        img = NPC_HAPPY.get(nname) or NPC_DEFAULT.get(
            nname, "CORP_Neoassunto_Sereno.png"
        )
    else:
        img = NPC_DEFAULT.get(nname, "CORP_Dipendente_Rassegnato.png")

    return f"{GFX_PATH}/personaggi/{img}"


def _event_icon(event) -> str | None:
    if not hasattr(event, "id") or not event.id:
        return None
    path = EVENT_ICONS.get(event.id)
    if path:
        return f"{GFX_PATH}/eventi/{path}"
    return None


def _state_icon(status: str) -> str | None:
    if not status:
        return None
    s_lower = status.lower()
    for key, path in STATE_ICONS.items():
        key_lower = key.lower().replace("_", " ")
        if key_lower in s_lower or s_lower in key_lower:
            return f"{GFX_PATH}/stati/{path}"
    if "burnout" in s_lower:
        return f"{GFX_PATH}/stati/{STATE_ICONS['Burnout']}"
    return None


def get_stats_dict(eng: GameEngine) -> dict:
    return eng.player.to_dict()["stats"]


def determine_ending(player) -> str:
    endings = []

    # Finali basati sulle fazioni (priorità alta)
    if player.factions["Ribelli"] >= 70 and player.integrity >= 60:
        endings.append(("IL WHISTLEBLOWER", 7))
    if player.factions["Fedelissimi"] >= 70 and player.manager_rep >= 80:
        endings.append(("IL BRACCIO DESTRO", 7))
    if player.factions["Gruppo Silenzioso"] >= 70:
        endings.append(("LO SPETTATORE", 6))
    if all(v >= 50 for v in player.factions.values()):
        endings.append(("IL CAMALEONTE", 5))

    # Nuovi finali combinati (incrociano archetipo + profilo comportamentale)
    arch = player.company_type
    t = player.tags
    if arch == "Startup Caotica" and t.get("burnout_risk", 0) >= 5:
        endings.append(("IL FONDATORE ESAURITO", 6))
    if (
        arch == "Azienda Familiare"
        and t.get("truth_teller", 0) >= 5
        and player.manager_rep <= 30
    ):
        endings.append(("IL PECORA NERA", 6))
    if arch == "Consulting" and t.get("yes_man", 0) >= 10:
        endings.append(("L'INGRANAGGIO PERFETTO", 5))
    if player.energy <= 10 and player.days_survived >= 20:
        endings.append(("IL RESISTENTE", 4))
    if player.self_esteem >= 80 and player.is_alive:
        endings.append(("L'INDIOMABILE", 3))

    # Finali basati sullo stato
    if player.status == "Promosso":
        endings.append(("IL POLITICO", 4))
    elif player.status == "Promozione Tossica":
        endings.append(("IL CINICO", 4))
    elif player.status == "Licenziato":
        endings.append(("IL CINESE", 3))

    # Finali basati sulle statistiche
    if player.integrity >= 80 and player.manager_rep <= 30:
        endings.append(("IL MARTIRE", 3))
    if player.integrity <= 25:
        endings.append(("IL CINICO", 2))
    if player.employability >= 70 and player.is_alive:
        endings.append(("IL FUGGITIVO", 2))
    if player.manager_rep >= 70 and player.integrity >= 70:
        endings.append(("IL RIFORMATORE", 3))
    if "Burnout" in player.status:
        endings.append(("IL CADUTO", 4))

    if not endings:
        endings.append(("IL SOPRAVVISSUTO", 1))

    endings.sort(key=lambda x: x[1], reverse=True)
    return endings[0][0]


# ── UI ──


def _render_stats_section(stats: dict):
    with ui.column().classes("w-full gap-3 mt-2"):
        for label, key, color in bars_def:
            is_critical = stats[key] <= 20 or (key == "stress" and stats[key] >= 80)
            pulse_class = " pulse-danger rounded-lg" if is_critical else ""

            with ui.column().classes(f"w-full gap-1 p-2 {pulse_class}"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label(label.upper()).classes(
                        "text-[10px] font-bold text-gray-400 tracking-tighter"
                    )
                    val = stats[key]
                    val_color = (
                        "#f87171"
                        if (val <= 20 or (key == "stress" and val >= 80))
                        else "#e2e8f0"
                    )
                    ui.label(f"{val}%").style(f"color: {val_color}").classes(
                        "text-[10px] font-black font-mono"
                    )

                bar_color = "#ef4444" if is_critical else color
                ui.linear_progress(
                    value=stats[key] / 100,
                    size="4px",
                    color=bar_color,
                    show_value=False,
                ).classes("rounded-full bg-white/5")


def _render_factions_section(factions: dict):
    ui.label("FAZIONI").classes(
        "text-xs font-bold text-gray-500 uppercase tracking-wider mt-4 mb-1"
    )
    for fname, fscore in factions.items():
        fcol = NPC_FACTION_COLORS.get(fname, "#6b7280")
        aligned = [n for n, f in NPC_FACTION_MAP.items() if f == fname]
        aligned_str = f" ({', '.join(aligned)})" if aligned else ""
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-1"):
                ui.icon("circle", size="8px").style(f"color: {fcol}")
                ui.label(f"{fname}{aligned_str}").classes("text-xs text-gray-400")
            ui.label(f"{fscore}%").classes("text-xs text-gray-300")


def _render_relationships_section(npcs: dict):
    ui.label("RELAZIONI").classes(
        "text-xs font-bold text-gray-500 uppercase tracking-wider mt-4 mb-1"
    )
    for nname, ndata in npcs.items():
        nfaction = NPC_FACTION_MAP.get(nname, "")
        avi_color = NPC_FACTION_COLORS.get(nfaction, "#6b7280")
        trust = ndata["trust"]
        trust_color = (
            "#4ade80" if trust >= 60 else "#f87171" if trust < 35 else "#eab308"
        )
        with ui.row().classes("w-full items-center gap-2"):
            portrait_url = _npc_portrait(nname, ndata)
            ui.image(portrait_url).style(
                f"border-color: {avi_color}; width: 40px; height: 40px; border-radius: 10px; border: 2px solid"
            ).classes("npc-avatar")
            with ui.column().classes("gap-0 flex-1"):
                ui.label(nname).classes("text-xs text-gray-300")
                ui.label(
                    f"Fiducia {trust}%  Rispetto {ndata['respect']}%  Paura {ndata['fear']}%"
                ).style(f"color: {trust_color}").classes("text-[10px]")


@ui.refreshable
def page():
    if screen == "start":
        _render_start()
    elif screen == "laboratory":
        _render_laboratory()
    elif screen == "game":
        _render_game()
        if _tutorial_active:
            _render_tutorial()
    elif screen == "game_over":
        _render_game_over()
    elif screen == "analytics":
        _render_analytics()


def _render_laboratory():
    """Vista principale del laboratorio di agenti migliorata (v3.0)."""
    client_id = ui.context.client.id
    inspected_agent_id = client_inspected_agent.get(client_id)

    lab_view = swarm.get_laboratory_view(current_human_id)
    stats = lab_view["analytics"]

    # Dati per grafico dinamico profili
    history = get_swarm_history(swarm.session_id)

    # Se non c'è un agente ispezionato, scegliamo il primo della lista (spesso quello posseduto)
    if not inspected_agent_id and lab_view["agents"]:
        inspected_agent_id = lab_view["agents"][0]["agent_id"]
        client_inspected_agent[client_id] = inspected_agent_id

    # Cerchiamo i dati dell'agente ispezionato
    inspected_agent = next((a for a in lab_view["agents"] if a["agent_id"] == inspected_agent_id), None)
    if not inspected_agent and lab_view["agents"]:
        inspected_agent = lab_view["agents"][0]
        inspected_agent_id = inspected_agent["agent_id"]

    with ui.column().classes("w-full max-w-[1600px] mx-auto p-4 gap-4 min-h-screen"):

        # --- HEADER: Emotional Weather + Swarm Stats ---
        with ui.row().classes("w-full items-center justify-between p-4 vn-card vn-card-highlight").style("background: rgba(10,10,20,0.8)"):
            with ui.row().classes("items-center gap-6"):
                # Emotional Weather
                avg_stress = stats.get('avg_stress', 0)
                if avg_stress < 40:
                    weather_icon, weather_label, weather_color = "sunny", "SOLEGGIATO", "text-green-400"
                elif avg_stress < 60:
                    weather_icon, weather_label, weather_color = "cloud", "NUVOLOSO", "text-gray-400"
                elif avg_stress < 75:
                    weather_icon, weather_label, weather_color = "thunderstorm", "TEMPORALE", "text-yellow-400"
                else:
                    weather_icon, weather_label, weather_color = "bolt", "TEMPESTA", "text-red-500"

                if stats.get('alive_count', 0) < stats.get('total_agents', 0):
                    weather_icon, weather_label, weather_color = "skull", "COLLASSO", "text-red-900"

                with ui.column().classes("items-center gap-0"):
                    ui.icon(weather_icon, size="32px").classes(weather_color)
                    ui.label(weather_label).classes(f"text-[10px] font-black {weather_color} tracking-tighter")

                ui.separator().props("vertical").classes("bg-white/10 h-10")

                # Global Stats
                with ui.column().classes("gap-0"):
                    ui.label("STRESS MEDIO SCIAME").classes("text-[10px] text-gray-500 font-bold")
                    ui.label(f"{avg_stress}%").classes("text-2xl font-black text-white")

                with ui.column().classes("gap-0"):
                    ui.label("SOGGETTI ATTIVI").classes("text-[10px] text-gray-500 font-bold")
                    ui.label(f"{stats.get('alive_count', 0)}/{len(swarm.agents)}").classes("text-2xl font-black text-green-400")

            ui.label("LABORATORIO ANTROPOLOGICO v3.2").classes("text-xl font-black tracking-[0.2em] text-white/20 absolute left-1/2 -translate-x-1/2")

            with ui.row().classes("items-center gap-4"):
                # Input per numero simulazioni
                with ui.row().classes("items-center gap-2 bg-white/5 p-1 rounded-lg border border-white/10"):
                    ui.label("SIM:").classes("text-[10px] font-bold text-gray-500 ml-2")
                    sim_count = ui.number(value=1, min=1, max=100, step=1).props("dense borderless dark").classes("w-12 text-xs")
                    ui.button(icon="play_arrow", on_click=lambda: _step_simulation(int(sim_count.value))).props("color=green size=sm round").classes("shadow-lg")

                ui.button("10x", on_click=lambda: _step_simulation(10)).props("color=green size=md flat").classes("font-bold")
                ui.button("← MENU", on_click=lambda: globals().update(screen="start") or page.refresh()).props("flat color=gray").classes("text-xs")

        # --- DYNAMIC PROFILE EVOLUTION (NEW) ---
        if len(history) > 1:
            with ui.card().classes("w-full p-4 vn-card").props("flat"):
                ui.label("EVOLUZIONE DINAMICA TRATTI PSICOLOGICI (VALORI MEDI SCIAME)").classes("text-[10px] font-black text-purple-400 tracking-widest mb-4")

                trait_names = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism", "narcissism", "machiavellianism", "psychopathy"]
                trait_labels = ["Apertura", "Coscienziosità", "Estroversione", "Gradevolezza", "Nevroticismo", "Narcisismo", "Machiavellismo", "Psicopatia"]
                series = []

                for i, t_name in enumerate(trait_names):
                    data = []
                    for h in history:
                        avg_stats = json.loads(h["avg_stats_json"])
                        avg_traits = avg_stats.get("avg_traits", {})
                        data.append(round(avg_traits.get(t_name, 50), 1))

                    series.append({
                        "name": trait_labels[i],
                        "type": "line",
                        "smooth": True,
                        "data": data,
                    })

                evolution_option = {
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": trait_labels, "textStyle": {"color": "#999", "fontSize": 10}, "top": 0},
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "xAxis": [{"type": "category", "boundaryGap": False, "data": [h["turn_number"] for h in history]}],
                    "yAxis": [{"type": "value", "min": 0, "max": 100}],
                    "series": series,
                    "backgroundColor": "transparent"
                }
                ui.echart(evolution_option).classes("w-full h-80")

        # --- HR DSS INSIGHTS (NEW) ---
        if stats.get("profile_impact"):
            with ui.row().classes("w-full gap-4 items-stretch"):
                with ui.card().classes("flex-1 p-4 vn-card").props("flat"):
                    ui.label("IMPATTO CULTURALE PER PROFILO (DSS)").classes("text-[10px] font-black text-blue-400 tracking-widest mb-4")
                    with ui.row().classes("w-full gap-4"):
                        for p_name, p_data in stats["profile_impact"].items():
                            with ui.column().classes("flex-1 p-3 bg-white/5 rounded-lg border border-white/10"):
                                ui.label(p_name.upper()).classes("text-[10px] font-black text-gray-300 truncate")
                                with ui.row().classes("w-full justify-between items-end mt-2"):
                                    with ui.column().classes("gap-0"):
                                        ui.label("Stress").classes("text-[8px] text-gray-500")
                                        ui.label(f"{p_data['avg_stress']}%").classes("text-sm font-bold text-red-400")
                                    with ui.column().classes("gap-0"):
                                        ui.label("Sopravvivenza").classes("text-[8px] text-gray-500")
                                        ui.label(f"{p_data['avg_days']}gg").classes("text-sm font-bold text-green-400")
                                    with ui.column().classes("gap-0"):
                                        ui.label("Tasso").classes("text-[8px] text-gray-500")
                                        ui.label(f"{p_data['survival_rate']}%").classes("text-sm font-bold text-blue-400")

        # --- MAIN 3-ZONE LAYOUT ---
        with ui.row().classes("w-full gap-4 items-start no-wrap"):

            # COLONNA SX: Agent Compact List
            with ui.column().classes("w-80 shrink-0 gap-3"):
                ui.label("SOGGETTI").classes("text-xs font-black text-gray-500 tracking-widest ml-1")
                for agent_data in lab_view["agents"]:
                    is_selected = agent_data["agent_id"] == inspected_agent_id
                    _render_agent_compact_card(agent_data, is_selected)

            # AREA CENTRALE: Agent Focus
            with ui.column().classes("flex-1 gap-4"):
                if inspected_agent:
                    # Focus Header
                    with ui.card().classes("w-full p-6 vn-card vn-card-highlight").props("flat"):
                        with ui.row().classes("w-full items-start justify-between"):
                            with ui.column().classes("gap-0"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label(inspected_agent["name"]).classes("text-3xl font-black text-white tracking-tighter")
                                    if inspected_agent["is_possessed"]:
                                        ui.badge("POSSEDUTO", color="purple").classes("px-2 font-black text-[10px]")
                                ui.label(f"{inspected_agent['profile_name']} · {inspected_agent['company_type']} · GIORNO {inspected_agent['day']}").classes("text-sm text-blue-400 font-bold")

                            with ui.row().classes("gap-2"):
                                if inspected_agent["is_possessed"]:
                                    ui.button("CONTINUA", on_click=lambda aid=inspected_agent["agent_id"]: _continue_possession(aid)).props("color=purple icon=bolt").classes("font-bold")
                                else:
                                    ui.button("POSSIEDI", on_click=lambda aid=inspected_agent["agent_id"]: _start_possession(aid)).props("color=blue icon=psychology").classes("font-bold")

                        # Aura Radar Area
                        with ui.row().classes("w-full gap-6 mt-6"):
                            # Radar chart
                            with ui.column().classes("flex-1 items-center"):
                                ui.label("AURA COMPORTAMENTALE").classes("text-[10px] font-black text-gray-500 tracking-widest mb-4")
                                _render_aura_radar(inspected_agent)

                            # Event Showcase
                            with ui.column().classes("w-96 gap-4"):
                                # Report Strategico (NEW)
                                if "strategic_report" in inspected_agent and "discursive_comment" in inspected_agent["strategic_report"]:
                                    ui.label("ANALISI STRATEGICA POSTERIORI").classes("text-[10px] font-black text-purple-400 tracking-widest mb-0")
                                    with ui.card().classes("w-full p-4 vn-card border-l-4 border-purple-500").style("background: rgba(120,50,255,0.05)"):
                                        rep = inspected_agent["strategic_report"]
                                        ui.label(rep["strategy_name"].upper()).classes("text-xs font-black text-purple-300 mb-2")
                                        ui.markdown(rep["discursive_comment"]).classes("text-xs text-gray-300 leading-relaxed italic")

                                ui.label("EVENTO CORRENTE").classes("text-[10px] font-black text-gray-500 tracking-widest mb-0")
                                with ui.card().classes("w-full p-4 vn-card").style("background: rgba(0,0,0,0.3)"):
                                    ui.label(inspected_agent["current_event"].replace("_", " ").upper() if inspected_agent["current_event"] else "NESSUN EVENTO").classes("text-xs font-black text-orange-400 mb-2")
                                    ui.markdown(inspected_agent["current_event_text"]).classes("text-sm text-gray-300 italic line-clamp-3")

                                ui.label("SCELTE & PROBABILITÀ").classes("text-[10px] font-black text-gray-500 tracking-widest mt-2")
                                with ui.column().classes("w-full gap-2"):
                                    for choice in inspected_agent["current_choices"]:
                                        prob = choice.get("probability", 0)
                                        with ui.row().classes("w-full items-center justify-between p-2 bg-white/5 rounded border border-white/10"):
                                            ui.label(choice["text"][:40] + "...").classes("text-[11px] text-gray-400 truncate flex-1")
                                            with ui.row().classes("items-center gap-2"):
                                                ui.label(f"{prob}%").classes("text-[10px] font-black text-gray-500")
                                                ui.label(choice["category"]).classes(f"text-[9px] font-bold px-1 rounded").style(f"background: {cat_colors.get(choice['category'], '#666')}40; color: {cat_colors.get(choice['category'], '#666')}")

                    # Global Metrics of Inspected Agent
                    with ui.row().classes("w-full gap-4"):
                        _metric_card("STRESS", inspected_agent["stress"], "#ef4444")
                        _metric_card("ENERGIA", inspected_agent["energy"], "#22c55e")
                        _metric_card("SALUTE", inspected_agent["health"], "#22d3ee")
                        _metric_card("AUTOSTIMA", inspected_agent["self_esteem"], "#eab308")

            # COLONNA DX: Decision Timeline
            with ui.column().classes("w-80 shrink-0 gap-3"):
                ui.label("CRONOLOGIA SCELTE").classes("text-xs font-black text-gray-500 tracking-widest ml-1")
                with ui.column().classes("w-full gap-1 overflow-y-auto max-h-[80vh] pr-2"):
                    if inspected_agent and inspected_agent["recent_decisions"]:
                        for dec in inspected_agent["recent_decisions"]:
                            _render_timeline_item(dec)
                    else:
                        ui.label("Nessuna decisione registrata").classes("text-xs text-gray-600 italic mt-4 text-center w-full")


def _render_agent_compact_card(agent, is_selected):
    # Determine state color
    status_color = "text-green-400"
    status_icon = "circle"
    border_class = "border-white/5"

    if not agent["alive"]:
        status_color = "text-gray-600"
        status_icon = "cancel"
    elif agent["stress"] > 75 or agent["health"] < 30:
        status_color = "text-red-500"
        status_icon = "error"
        border_class = "border-red-500/50 pulse-danger"
    elif agent["stress"] > 50:
        status_color = "text-yellow-500"
        status_icon = "warning"

    if agent["is_possessed"]:
        status_color = "text-purple-400"
        status_icon = "visibility"

    card_bg = "background: rgba(30,30,50,0.6)" if is_selected else "background: rgba(15,15,30,0.4)"

    with ui.card().classes(f"w-full p-3 vn-card cursor-pointer {border_class}").style(card_bg).on("click", lambda: _inspect_agent(agent["agent_id"])):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            with ui.row().classes("items-center gap-2 flex-1 min-w-0"):
                ui.icon(status_icon, size="14px").classes(status_color)
                ui.label(agent["name"]).classes("text-sm font-bold text-white truncate")
            ui.label(f"G{agent['day']}").classes("text-[10px] font-mono text-gray-500")

        # Stress bar
        with ui.row().classes("w-full items-center gap-2 mt-1"):
            ui.linear_progress(agent["stress"]/100, size="2px", color="red" if agent["stress"] > 75 else "orange" if agent["stress"] > 50 else "blue").classes("flex-1 bg-white/5")
            ui.label(f"{agent['stress']}%").classes("text-[9px] font-mono text-gray-500")

        with ui.row().classes("w-full items-center justify-between mt-1"):
            ui.label(agent["profile_name"].upper()).classes("text-[9px] font-black text-gray-600")
            ui.label(agent["dominant_faction"]).classes("text-[9px] font-bold text-gray-500")


def _render_aura_radar(agent):
    # Cerchiamo l'agente reale nello sciame per accedere al profilo psicometrico
    real_agent = swarm.agents.get(agent["agent_id"])
    if not real_agent:
        return

    profile = real_agent.profile

    # Radar Axes 1: BIG FIVE (OCEAN)
    ocean_axes = [
        {"name": "O", "value": profile.openness},
        {"name": "C", "value": profile.conscientiousness},
        {"name": "E", "value": profile.extraversion},
        {"name": "A", "value": profile.agreeableness},
        {"name": "N", "value": profile.neuroticism},
    ]

    # Radar Axes 2: DARK TRIAD
    dark_axes = [
        {"name": "Narcissism", "value": profile.narcissism},
        {"name": "Machiavellianism", "value": profile.machiavellianism},
        {"name": "Psychopathy", "value": profile.psychopathy},
    ]

    profile_color = AGENT_PROFILE_COLORS.get(agent["profile_name"], "#3b82f6")

    with ui.row().classes("w-full gap-2"):
        # OCEAN Radar
        ocean_option = {
            "title": {"text": "BIG FIVE", "left": "center", "textStyle": {"color": "#555", "fontSize": 10}},
            "radar": {
                "indicator": [
                    {"name": "Openness", "max": 100},
                    {"name": "Conscientiousness", "max": 100},
                    {"name": "Extraversion", "max": 100},
                    {"name": "Agreeableness", "max": 100},
                    {"name": "Neuroticism", "max": 100},
                ],
                "shape": "polygon",
                "axisName": {"color": "#777", "fontSize": 8},
                "splitArea": {"show": False},
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}
            },
            "series": [{
                "type": "radar",
                "data": [{"value": [a["value"] for a in ocean_axes], "areaStyle": {"color": profile_color, "opacity": 0.4}}],
                "symbol": "none",
                "lineStyle": {"width": 2, "color": profile_color}
            }],
            "backgroundColor": "transparent",
        }
        ui.echart(ocean_option).classes("w-1/2 h-64")

        # DARK TRIAD Radar
        dark_option = {
            "title": {"text": "TRIADE OSCURA", "left": "center", "textStyle": {"color": "#555", "fontSize": 10}},
            "radar": {
                "indicator": [
                    {"name": "Narcissism", "max": 100},
                    {"name": "Machiavellianism", "max": 100},
                    {"name": "Psychopathy", "max": 100},
                ],
                "shape": "polygon",
                "axisName": {"color": "#777", "fontSize": 8},
                "splitArea": {"show": False},
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}
            },
            "series": [{
                "type": "radar",
                "data": [{"value": [a["value"] for a in dark_axes], "areaStyle": {"color": "#ef4444", "opacity": 0.4}}],
                "symbol": "none",
                "lineStyle": {"width": 2, "color": "#ef4444"}
            }],
            "backgroundColor": "transparent",
        }
        ui.echart(dark_option).classes("w-1/2 h-64")


def _render_timeline_item(dec):
    cat_col = cat_colors.get(dec["category"], "#666")
    is_auto = dec["was_auto"]

    with ui.row().classes("w-full items-start gap-3 p-2 bg-white/5 rounded border-l-2 mb-1").style(f"border-color: {cat_col}"):
        with ui.column().classes("gap-0 flex-1"):
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(dec["category"]).classes(f"text-[9px] font-black").style(f"color: {cat_col}")
                ui.label(f"G{dec['day']}").classes("text-[9px] text-gray-600 font-mono")

            ui.label(dec["choice_text"]).classes("text-xs text-gray-300 leading-tight mt-1")

            with ui.row().classes("w-full justify-between items-center mt-2"):
                # Impact indicator
                delta = dec.get("stress_delta", 0)
                if delta != 0:
                    delta_col = "text-red-400" if delta > 0 else "text-green-400"
                    delta_sign = "+" if delta > 0 else ""
                    ui.label(f"STRESS {delta_sign}{delta}").classes(f"text-[9px] font-bold {delta_col}")
                else:
                    ui.element("div") # spacer

                ui.icon("smart_toy" if is_auto else "person", size="12px").classes("text-gray-600")


def _metric_card(label, value, color):
    with ui.card().classes("flex-1 p-3 vn-card items-center gap-0").props("flat"):
        ui.label(label).classes("text-[10px] font-black text-gray-500 tracking-tighter")
        ui.label(f"{value}%").classes("text-xl font-black").style(f"color: {color}")
        ui.linear_progress(value/100, size="2px", color=color).classes("w-full mt-2 bg-white/5")


def _inspect_agent(agent_id):
    client_id = ui.context.client.id
    client_inspected_agent[client_id] = agent_id
    page.refresh()


def _mini_stat(label: str, value: int, color: str):
    with ui.column().classes("items-center flex-1"):
        ui.circular_progress(value / 100, size="32px", color=color)
        ui.label(label).classes("text-[9px] text-gray-500 mt-1")


def _start_possession(agent_id: str):
    """Inizia il possesso di un agente."""
    global current_agent_id, screen, engine, session_id

    if not current_human_id:
        ui.notify("Nessun umano registrato. Torna al menu e riprova.", type="warning")
        return
    result = swarm.possess_agent(current_human_id, agent_id)
    if result.get("success"):
        current_agent_id = agent_id
        agent = swarm.agents[agent_id]
        engine = agent.engine
        session_id = f"possession_{agent_id}_{uuid.uuid4().hex[:6]}"
        screen = "game"
        page.refresh()
    else:
        ui.notify(
            result.get("error", "Impossibile possedere l'agente"), type="negative"
        )


def _continue_possession(agent_id: str):
    global current_agent_id, screen, engine
    if agent_id not in swarm.agents:
        ui.notify("Agente non trovato", type="negative")
        return
    current_agent_id = agent_id
    engine = swarm.agents[agent_id].engine
    screen = "game"
    page.refresh()


def _go_to_laboratory():
    global current_human_id, current_agent_id, screen
    current_agent_id = None
    if not current_human_id:
        human = swarm.register_human(
            getattr(engine, "player", None) and engine.player.name or "Osservatore"
        )
        current_human_id = human.human_id
    screen = "laboratory"
    page.refresh()


def _mood_matches_agent(mood: str, agent: dict) -> bool:
    """
    Verifica se lo stato psicofisico di un agente corrisponde al mood selezionato.
    Utilizzato per filtrare gli agenti nel Jump System.
    """
    stats = agent.get("current_stats") or {}
    if not stats:
        return True

    if mood == "Stressato":
        return stats.get("stress", 0) > 50
    elif mood == "Arrabbiato":
        return stats.get("self_esteem", 50) < 40 or stats.get("stress", 0) > 60
    elif mood == "Stanco":
        return stats.get("energy", 100) < 40
    elif mood == "Motivato":
        return stats.get("energy", 0) > 60 and stats.get("stress", 100) < 50
    elif mood == "Cinico":
        return stats.get("integrity", 50) < 40 or stats.get("team_rep", 50) < 40
    elif mood == "Speranzoso":
        return stats.get("self_esteem", 0) > 60 and stats.get("employability", 0) > 60
    elif mood == "Confuso":
        # Confuso è un mood transizionale, quasi tutti possono esserlo se hanno stats medie
        s = stats.get("stress", 50)
        return 30 <= s <= 70
    return True


def _render_jump_dialog():
    """
    Dialog che appare quando l'umano vuole saltare a un altro agente.
    Mostra gli agenti disponibili filtrati per mood selezionato.
    """
    if not current_human_id:
        ui.notify(
            "Registrati prima nel Laboratorio per usare il salto.", type="warning"
        )
        return
    with ui.dialog().props("maximized") as dialog:
        with (
            ui.card()
            .classes("w-full h-full bg-gray-900 text-white overflow-y-auto")
            .props("flat")
        ):
            with ui.column().classes("w-full max-w-3xl mx-auto p-8 gap-6"):
                ui.label("🔄 SALTA A UN ALTRO AGENTE").classes(
                    "text-2xl font-black text-white mb-4"
                )
                ui.label(
                    "Scegli un agente che rispecchia il tuo stato d'animo attuale."
                ).classes("text-gray-400 mb-6")

                # Mood selector (filtra la lista agenti)
                mood = ui.select(
                    [
                        "Stressato",
                        "Arrabbiato",
                        "Stanco",
                        "Motivato",
                        "Cinico",
                        "Speranzoso",
                        "Confuso",
                    ],
                    label="Come ti senti in questo momento?",
                ).classes("w-full max-w-md mb-6")

                # Contenitore agenti (ricaricato al cambio mood)
                agents_container = ui.column().classes("w-full gap-3")

                def render_agents():
                    agents_container.clear()
                    available = swarm.get_available_agents(current_human_id)
                    selected_mood = mood.value
                    rendered_any = False
                    for agent in available:
                        if agent["agent_id"] == current_agent_id:
                            continue
                        if selected_mood and not _mood_matches_agent(
                            selected_mood, agent
                        ):
                            continue
                        rendered_any = True
                        with agents_container:
                            with (
                                ui.card()
                                .classes("w-full p-4 mb-3 vn-card")
                                .props("flat")
                            ):
                                with ui.row().classes(
                                    "w-full items-center justify-between"
                                ):
                                    with ui.column():
                                        ui.label(agent["name"]).classes("font-bold")
                                        ui.label(
                                            f"Giorno {agent['current_day']} · {agent['company_type']}"
                                        ).classes("text-xs text-gray-500")
                                    with ui.column().classes("items-end"):
                                        ui.label(
                                            f"Affinità: {agent['match_score']}%"
                                        ).classes(
                                            "text-sm font-bold text-green-400"
                                            if agent["match_score"] > 60
                                            else "text-sm text-gray-400"
                                        )
                                        ui.button(
                                            "SALTA QUI",
                                            on_click=lambda aid=agent["agent_id"], m=mood: (
                                                _execute_jump(aid, m.value, dialog)
                                            ),
                                        ).props("color=purple size=sm")
                    if not rendered_any:
                        with agents_container:
                            ui.label(
                                "Nessun agente corrisponde al tuo stato d'animo attuale."
                            ).classes("text-gray-500 italic")

                render_agents()
                mood.on_change = lambda: render_agents()

                ui.button("Annulla", on_click=dialog.close).props("flat").classes(
                    "mt-4"
                )

    dialog.open()


def _execute_jump(to_agent_id: str, mood: Optional[str], dialog):
    """Esegue il salto da un agente all'altro."""
    global current_agent_id, engine, session_id

    if not current_human_id:
        ui.notify("Nessun umano registrato.", type="warning")
        return

    result = swarm.possess_agent(
        current_human_id, to_agent_id, reason=f"Salto emotivo: {mood}" if mood else None
    )

    if result.get("success"):
        current_agent_id = to_agent_id
        agent = swarm.agents[to_agent_id]
        engine = agent.engine
        session_id = f"possession_{to_agent_id}_{uuid.uuid4().hex[:6]}"
        dialog.close()
        page.refresh()


def _show_agent_details(agent_id: str):
    """Mostra dettagli completi di un agente per aiutare la scelta."""
    details = swarm.get_agent_detailed_view(agent_id)

    with ui.dialog().props("maximized") as dialog:
        with (
            ui.card()
            .classes("w-full h-full bg-gray-900 text-white overflow-y-auto")
            .props("flat")
        ):
            with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-6"):
                with ui.row().classes("w-full items-center justify-between"):
                    with ui.row().classes("items-center gap-4"):
                        ui.icon("psychology", size="48px").classes("text-blue-400")
                        with ui.column().classes("gap-0"):
                            ui.label(details["agent"]["name"]).classes(
                                "text-3xl font-black"
                            )
                            ui.label(details["agent"]["profile_name"]).classes(
                                "text-xl text-blue-400"
                            )
                    ui.button(icon="close", on_click=dialog.close).props(
                        "flat round color=white size=lg"
                    )

                with ui.grid(columns=2).classes("w-full gap-6"):
                    # Colonna 1: Profilo e Stats
                    with ui.column().classes("gap-4"):
                        ui.label("PROFILO PSICOLOGICO").classes(
                            "text-xs font-black tracking-widest text-gray-500"
                        )
                        ui.label(details["agent"]["company_type"]).classes(
                            "text-sm text-gray-300 italic"
                        )

                        # Radar Stats attuali
                        state = details["agent"]["current_state"]
                        stats = (
                            state["stats"]["stats"]
                            if state and state["stats"]
                            else None
                        )
                        if stats:
                            radar_data = [
                                {"name": "Stress", "value": stats.get("stress", 0)},
                                {"name": "Energia", "value": stats.get("energy", 0)},
                                {"name": "Salute", "value": stats.get("health", 0)},
                                {
                                    "name": "Integrità",
                                    "value": stats.get("integrity", 0),
                                },
                                {
                                    "name": "Autostima",
                                    "value": stats.get("self_esteem", 0),
                                },
                                {
                                    "name": "Occupabilità",
                                    "value": stats.get("employability", 0),
                                },
                            ]
                            radar_option = {
                                "radar": {
                                    "indicator": [
                                        {"name": r["name"], "max": 100}
                                        for r in radar_data
                                    ],
                                    "shape": "circle",
                                },
                                "series": [
                                    {
                                        "type": "radar",
                                        "data": [
                                            {
                                                "value": [
                                                    s["value"] for s in radar_data
                                                ],
                                                "name": "Stato Attuale",
                                            }
                                        ],
                                        "areaStyle": {"color": "rgba(59,130,246,0.2)"},
                                        "lineStyle": {"color": "#3b82f6", "width": 2},
                                    }
                                ],
                                "backgroundColor": "transparent",
                            }
                            ui.echart(radar_option).classes("w-full h-64")

                    # Colonna 2: Memoria e Analisi
                    with ui.column().classes("gap-4"):
                        ui.label("ANALISI COMPORTAMENTALE").classes(
                            "text-xs font-black tracking-widest text-gray-500"
                        )
                        summary = details["memory_summary"]

                        # Heatmap/Bar chart categorie
                        cat_data = summary["category_distribution"]
                        bar_option = {
                            "xAxis": {
                                "type": "category",
                                "data": list(cat_data.keys()),
                                "axisLabel": {"color": "#999"},
                            },
                            "yAxis": {"type": "value", "axisLabel": {"color": "#999"}},
                            "series": [
                                {
                                    "data": list(cat_data.values()),
                                    "type": "bar",
                                    "itemStyle": {"color": "#a855f7"},
                                }
                            ],
                            "backgroundColor": "transparent",
                            "grid": {"top": 20, "bottom": 40, "left": 40, "right": 20},
                        }
                        ui.echart(bar_option).classes("w-full h-48")

                        with ui.row().classes("w-full justify-around mt-2"):
                            with ui.column().classes("items-center"):
                                ui.label(str(summary["total_decisions"])).classes(
                                    "text-2xl font-black text-white"
                                )
                                ui.label("DECISIONI").classes(
                                    "text-[10px] text-gray-500"
                                )
                            with ui.column().classes("items-center"):
                                ui.label(str(summary["unique_events"])).classes(
                                    "text-2xl font-black text-white"
                                )
                                ui.label("EVENTI").classes("text-[10px] text-gray-500")
                            with ui.column().classes("items-center"):
                                hv_auto = summary["human_vs_auto"]
                                ui.label(
                                    f"{hv_auto['human_decisions']}/{hv_auto['auto_decisions']}"
                                ).classes("text-2xl font-black text-purple-400")
                                ui.label("UMANO/IA").classes(
                                    "text-[10px] text-gray-500"
                                )

                ui.separator().classes("bg-white/10 my-4")

                # Storia
                ui.label("STORIA DEL SOGGETTO").classes(
                    "text-xs font-black tracking-widest text-gray-500"
                )
                with ui.column().classes("w-full gap-2 max-h-48 overflow-y-auto pr-2"):
                    for p in reversed(details["possession_history"]):
                        status = "CONCLUSA" if p["ended"] else "IN CORSO"
                        color = "text-gray-400" if p["ended"] else "text-green-400"
                        with ui.row().classes(
                            "w-full justify-between items-center p-2 bg-white/5 rounded"
                        ):
                            ui.label(f"Possessione {status}").classes(
                                f"text-xs font-bold {color}"
                            )
                            ui.label(f"Decisioni: {p['decisions']}").classes(
                                "text-xs text-gray-500"
                            )
                            ui.label(
                                f"Inizio: {p['started'][:16].replace('T', ' ')}"
                            ).classes("text-[10px] text-gray-600")

                if not details["agent"]["is_possessed"]:
                    ui.button(
                        "POSSIEDI QUESTO AGENTE",
                        on_click=lambda: [_start_possession(agent_id), dialog.close()],
                    ).classes("w-full py-4 mt-4 bg-blue-600 font-bold")

        dialog.open()


def _step_simulation(steps=1):
    for _ in range(steps):
        swarm.run_simulation_step()
    page.refresh()


def _render_start():
    with ui.column().classes("w-full items-center justify-center min-h-[80vh] fade-in"):
        with (
            ui.card()
            .classes("w-full max-w-xl p-12 text-center vn-card vn-card-highlight mt-10")
            .props("flat")
        ):
            theme = ARCHETYPE_THEMES["Corporate Tossica"]
            ui.label("BURNOUT SIMULATOR").classes(
                "text-5xl font-black tracking-tighter mb-2"
            ).style(
                f"color: {theme['header']}; text-shadow: 0 0 30px {theme['accent']}60"
            )
            ui.label("Simulatore di Antropologia delle Organizzazioni").classes(
                "text-lg text-gray-400 mb-10 italic"
            )

            with ui.column().classes("w-full gap-6 items-center"):
                with ui.column().classes("w-full items-start"):
                    ui.label("ARCHETIPO AZIENDALE").classes(
                        "text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-1 ml-1"
                    )
                    arch_options = {
                        k: f"{k} — {v['description']}"
                        for k, v in GameEngine.COMPANY_ARCHETYPES.items()
                    }
                    arch_select = (
                        ui.select(
                            arch_options,
                            value="Corporate Tossica",
                        )
                        .classes("w-full")
                        .props("outlined standout dark color=blue")
                    )

                def on_arch_change():
                    t = ARCHETYPE_THEMES.get(
                        arch_select.value, ARCHETYPE_THEMES["Corporate Tossica"]
                    )
                    ui.run_javascript(f"""
                        document.documentElement.style.setProperty('--theme-accent', '{t["accent"]}');
                        document.documentElement.style.setProperty('--theme-header', '{t["header"]}');
                        document.documentElement.style.setProperty('--theme-glow', '{t["glow"]}');
                    """)

                arch_select.on("change", on_arch_change)

                with ui.column().classes("w-full items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10"):
                    ui.label("PARAMETRI HR (DSS)").classes(
                        "text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-1 ml-1"
                    )

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Tossicità Ambientale").classes("text-xs text-gray-300")
                        tox_slider = ui.slider(min=0, max=100, value=30).props("color=red-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Pressione Risorse").classes("text-xs text-gray-300")
                        res_slider = ui.slider(min=0, max=100, value=50).props("color=orange-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Coesione Sociale").classes("text-xs text-gray-300")
                        coh_slider = ui.slider(min=0, max=100, value=40).props("color=green-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Competizione Interna").classes("text-xs text-gray-300")
                        comp_slider = ui.slider(min=0, max=100, value=60).props("color=purple-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Supporto Sociale").classes("text-xs text-gray-300")
                        supp_slider = ui.slider(min=0, max=100, value=50).props("color=blue-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Trasparenza Decisionale").classes("text-xs text-gray-300")
                        trans_slider = ui.slider(min=0, max=100, value=30).props("color=cyan-5").classes("w-32")

                with ui.row().classes(
                    "w-full items-center justify-between bg-white/5 p-4 rounded-xl border border-white/10 mt-2"
                ):
                    with ui.column().classes("gap-0"):
                        ui.label('Modalità "Casi Reali"').classes(
                            "text-sm font-bold text-gray-200"
                        )
                        ui.label("Eventi ispirati a storie vere").classes(
                            "text-[10px] text-gray-400"
                        )
                    real_cases_toggle = ui.switch().props("color=blue-4")

                with ui.row().classes(
                    "w-full items-center justify-between bg-white/5 p-3 rounded-xl border border-white/10 mt-2"
                ):
                    with ui.column().classes("gap-0"):
                        ui.label("Salta tutorial").classes(
                            "text-sm font-bold text-gray-200"
                        )
                        ui.label("Non mostrare le istruzioni iniziali").classes(
                            "text-[10px] text-gray-400"
                        )
                    skip_tutorial_toggle = ui.switch().props("color=purple-4")

            def start_lab_cb():
                global current_human_id, screen

                hr_params = {
                    "toxicity": tox_slider.value,
                    "pressure": res_slider.value,
                    "cohesion": coh_slider.value,
                    "competition": comp_slider.value,
                    "social_support": supp_slider.value,
                    "transparency": trans_slider.value,
                    "real_cases": real_cases_toggle.value
                }

                # Allinea tutti gli agenti all'archetipo e ai parametri HR
                swarm.set_hr_parameters(arch_select.value, hr_params)

                if not current_human_id:
                    human = swarm.register_human("HR_Manager")
                    current_human_id = human.human_id
                screen = "laboratory"
                page.refresh()

            with ui.button(on_click=start_lab_cb).classes(
                "w-full mt-10 py-6 text-xl font-bold rounded-xl shadow-xl hover:scale-102 transition-transform bg-purple-600 text-white"
            ):
                with ui.row().classes("items-center gap-3 no-wrap"):
                    ui.icon("psychology", size="md")
                    ui.label("ENTRA NEL LABORATORIO")

            with ui.row().classes(
                "w-full justify-center mt-6 pt-6 border-t border-white/5 gap-3"
            ):
                ui.button(
                    "Analytics", on_click=lambda: _go_analytics(), icon="insights"
                ).props("flat color=grey-5").classes("text-xs")
                ui.button("Help", on_click=_show_help, icon="help").props(
                    "flat color=grey-5"
                ).classes("text-xs")
                ui.button(
                    "Config",
                    on_click=_show_config,
                    icon="settings",
                ).props("flat color=grey-5").classes("text-xs")


def _show_help():
    d = ui.dialog().props("maximized")
    with d:
        with (
            ui.card()
            .classes("w-full h-full bg-gray-900 text-white overflow-y-auto")
            .props("flat")
        ):
            with ui.column().classes("w-full max-w-3xl mx-auto p-8 gap-6"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("STRATEGIC LABORATORY & DSS HELP").classes(
                        "text-2xl font-black tracking-tighter text-blue-400"
                    )
                    ui.button(icon="close", on_click=d.close).props(
                        "flat round color=white"
                    )

                sections = [
                    (
                        "🧪 LABORATORIO HR (DSS)",
                        [
                            "Questa modalità permette di lanciare simulazioni su uno sciame di 6 agenti autonomi.",
                            "Puoi definire i parametri HR (Tossicità, Pressione, Coesione, Competizione, Supporto, Trasparenza) per vedere come influenzano lo stress collettivo.",
                            "Il grafico 'Evoluzione Dinamica' mostra come la biodiversità psicologica cambia nel tempo: alcuni profili 'conquistano' spazio a danno di altri in base all'ambiente.",
                            "Usa il selettore 'SIM' per lanciare N passi di simulazione contemporaneamente.",
                            "🔍 **Modalità Casi Reali**: Disattiva le euristiche di allineamento sociale ('Peer Influence') per testare gli agenti contro scenari deterministici basati su pattern di dati reali, senza il supporto sociale del gruppo.",
                        ],
                    ),
                    (
                        "📊 REPORT E TOP PERFORMERS",
                        [
                            "Al termine di ogni sessione (o ispezionando un agente), viene generato un report DSS.",
                            "Vengono identificati i 'Top Performers': agenti che hanno superato del 20% la sopravvivenza media del loro profilo o mantenuto stress bassissimo.",
                            "Le decisioni sono raggruppate per tipologia (Compliance, Resistance, etc.) per analizzare i pattern comportamentali dello sciame.",
                        ],
                    ),
                    (
                        "🔄 JUMP SYSTEM (POSSESSO)",
                        [
                            "Puoi 'possedere' un agente cliccando su POSSIEDI. Da quel momento farai tu le sue scelte.",
                            "Puoi saltare tra agenti usando il tasto SALTA. Il sistema ti proporrà agenti che corrispondono al tuo mood dichiarato.",
                            "L'antropologia organizzativa suggerisce che l'immersione (possesso) sia fondamentale per capire i motivi qualitativi dietro i dati quantitativi.",
                        ],
                    ),
                    (
                        "🎯 COSA DEVI FARE (MODALITÀ CLASSICA)",
                        [
                            "Sei un impiegato in un'azienda tossica. Ogni giorno riceverai un evento con una descrizione della situazione.",
                            "Devi scegliere tra 2-4 opzioni di reazione. Ogni scelta ha effetti sulle tue statistiche e sulle relazioni con colleghi e fazioni.",
                            "L'obiettivo: sopravvivere più giorni possibile senza cadere in burnout, licenziamento o depressione professionale.",
                        ],
                    ),
                    (
                        "📊 STATISTICHE",
                        [
                            "Energia: cala con gli straordinari, si ricarica con scelte di autoconservazione.",
                            "Stress: aumenta con pressioni e conflitti. Se arriva a 100, burnout mentale.",
                            "Salute: cala con stress prolungato e mancanza di cure. Se arriva a 0, burnout fisico.",
                            "Autostima: si erode con umiliazioni e compromessi. A 0, depressione professionale.",
                            "Integrità: sale quando difendi i tuoi valori, cala quando tradisci te stesso.",
                            "Occupabilità: la tua attrattiva sul mercato. Tienila alta per poter scappare.",
                            "Rep. Manager: la tua reputazione col capo. Se cala a 0, sei licenziato.",
                            "Rep. Team: la tua reputazione tra colleghi. utile per alleanze.",
                        ],
                    ),
                    (
                        "🏛️ FAZIONI",
                        [
                            "Fedelissimi: seguono il manager. Guadagni punti facendo COMPLIANCE.",
                            "Gruppo Silenzioso: sopravvissuti neutrali. Cresce con scelte di ESCAPE.",
                            "Ribelli: si oppongono al sistema. Cresce con scelte RESISTANCE.",
                            "Le fazioni influenzano il finale di gioco e il supporto che riceverai dagli NPC.",
                        ],
                    ),
                    (
                        "👥 NPC (COLLEGHI)",
                        [
                            "Marco: il manager tossico. La sua fiducia sale con COMPLIANCE.",
                            "Giulia: collega opportunista. Osserva le tue mosse e si allea con chi vince.",
                            "Roberto: mentor disilluso. Apprezza l'integrità e la resistenza silenziosa.",
                            "Elena: HR passiva. Può aiutarti se ha fiducia in te, ma teme ritorsioni.",
                        ],
                    ),
                    (
                        "🔄 TIPI DI SCELTA",
                        [
                            "COMPLIANCE (blu): accontenti il sistema. Aumenta rep. manager ma spesso aumenta stress.",
                            "RESISTANCE (rossa): ti opponi. Alza autostima e integrità ma rischia ritorsioni.",
                            "NEGOTIATION (gialla): cerchi compromesso. Effetti bilanciati ma a volte nessuno è soddisfatto.",
                            "ESCAPE (verde): eviti il conflitto. Preserva energia ma non risolve i problemi.",
                        ],
                    ),
                    (
                        "🏆 FINALI E ACHIEVEMENT",
                        [
                            "Ogni partita termina con un finale basato sulle tue statistiche, fazioni e tag comportamentali.",
                            "I tag (yes_man, boundary_setter, truth_teller, survivor, burnout_risk) si accumulano con le scelte ripetute.",
                            "Sblocca achievement come 'Sempre Disponibile' (10 scelte yes_man) o 'Indistruttibile' (20 survivor).",
                            "Esistono oltre 15 finali diversi: da 'IL WHISTLEBLOWER' a 'IL CADUTO'.",
                        ],
                    ),
                    (
                        "💡 CONSIGLI",
                        [
                            "Non puoi sempre compiacere tutti. Scegli le tue battaglie.",
                            "Tieni d'occhio la salute mentale: stress > 80 è zona pericolo.",
                            "Le scelte NEGOTIATION a volte aprono percorsi nascosti.",
                            "I tag comportamentali sbloccano finali speciali. Sperimenta!",
                            "La fase di carriera cambia gli eventi disponibili.",
                        ],
                    ),
                ]

                for title, items in sections:
                    with ui.column().classes(
                        "w-full gap-2 p-4 rounded-xl bg-white/5 border border-white/10"
                    ):
                        ui.label(title).classes(
                            "text-sm font-black text-blue-300 tracking-tighter"
                        )
                        for item in items:
                            ui.label(f"• {item}").classes(
                                "text-sm text-gray-300 leading-relaxed ml-2"
                            )

                ui.label(
                    "Burnout Simulator v2.0 — Un gioco di antropologia organizzativa"
                ).classes(
                    "text-xs text-gray-500 text-center w-full mt-6 pt-4 border-t border-white/10"
                )
    d.open()


def _show_config():
    d = ui.dialog().props("maximized")
    with d:
        with (
            ui.card()
            .classes("w-full h-full bg-gray-900 text-white overflow-y-auto")
            .props("flat")
        ):
            with ui.column().classes("w-full max-w-xl mx-auto p-8 gap-6"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("IMPOSTAZIONI").classes(
                        "text-2xl font-black tracking-tighter text-blue-400"
                    )
                    ui.button(icon="close", on_click=d.close).props(
                        "flat round color=white"
                    )

                with ui.column().classes(
                    "w-full gap-4 p-6 rounded-xl bg-white/5 border border-white/10"
                ):
                    ui.label("LAYOUT").classes(
                        "text-sm font-black text-blue-300 tracking-tighter"
                    )
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Modalità schermo").classes("text-sm text-gray-300")
                        ui.toggle(
                            ["desktop", "mobile"],
                            value=_layout_mode,
                            on_change=lambda e: globals().update(_layout_mode=e.value),
                        ).props("color=blue-4 outline")

                with ui.column().classes(
                    "w-full gap-4 p-6 rounded-xl bg-white/5 border border-white/10"
                ):
                    ui.label("TUTORIAL").classes(
                        "text-sm font-black text-blue-300 tracking-tighter"
                    )
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Salta tutorial all'avvio").classes(
                            "text-sm text-gray-300"
                        )
                        ui.switch(
                            value=_skip_tutorial,
                            on_change=lambda e: globals().update(
                                _skip_tutorial=e.value
                            ),
                        ).props("color=purple-4")

                ui.label("Le modifiche al layout si applicano immediatamente.").classes(
                    "text-xs text-gray-500 text-center w-full"
                )
    d.open()


def _render_game():
    player = engine.player
    pdata = player.to_dict()
    event = engine.current_event
    theme = ARCHETYPE_THEMES.get(
        player.company_type, ARCHETYPE_THEMES["Corporate Tossica"]
    )

    if current_agent_id:
        with ui.row().classes(
            "w-full bg-purple-900/30 p-2 items-center justify-between border-b border-purple-500/50 mb-4"
        ):
            ui.label(f"POSSESSO AGENTE: {player.name}").classes(
                "text-xs font-black text-purple-300"
            )
            with ui.row().classes("gap-2"):
                ui.button(
                    "SALTA", icon="swap_horiz", on_click=_render_jump_dialog
                ).props("flat size=sm").classes("text-white")
                ui.button(
                    "LABORATORIO",
                    icon="biotech",
                    on_click=_go_to_laboratory,
                ).props("flat size=sm").classes("text-white")

    mobile_cls = " pb-20" if _layout_mode == "mobile" else ""
    with ui.column().classes(f"w-full gap-0{mobile_cls}"):
        # Top bar
        total_events = len(engine.event_manager.events)
        unique_seen = len(set(engine.history))
        is_repeat = event and event.id in engine.history[:-1]

        with ui.row().classes(
            "w-full items-center justify-between mb-6 pb-4 border-b border-white/5"
        ):
            with ui.row().classes("items-center gap-4 flex-wrap"):
                with ui.column().classes("gap-0"):
                    ui.label("GIORNO").classes(
                        "text-[10px] font-bold text-gray-500 uppercase tracking-widest"
                    )
                    ui.label(str(player.days_survived)).classes(
                        "text-3xl font-black text-white leading-none"
                    )

                ui.separator().props("vertical").classes("bg-white/10 h-8")

                with ui.column().classes("gap-1"):
                    ui.badge(player.company_type.upper(), color=theme["badge"]).classes(
                        "px-3 py-1 font-bold tracking-tighter"
                    )
                    ui.label(f"Evento {unique_seen}/{total_events}").classes(
                        "text-[10px] text-gray-400 font-mono"
                    )

            with ui.row().classes("items-center gap-2"):
                ui.button(
                    icon="menu",
                    on_click=lambda: ui.run_javascript(
                        'document.querySelector(".stats-sidebar").classList.toggle("open")'
                    ),
                ).props("flat round color=white").classes("lg:hidden")
                ui.button(icon="help", on_click=_show_help).props(
                    "flat round color=white"
                ).classes("hover:bg-white/10")
                ui.button(icon="hub", on_click=_show_decision_graph).props(
                    "flat round color=blue"
                ).classes("hover:bg-blue-500/10")
                ui.button(icon="biotech", on_click=_go_to_laboratory).props(
                    "flat round color=purple"
                ).classes("hover:bg-purple-500/10").tooltip("Laboratorio agenti")
                ui.button(icon="logout", on_click=_exit_game).props(
                    "flat round color=red"
                ).classes("hover:bg-red-500/10")

        # Main area
        with ui.row().classes("w-full gap-6 items-start"):
            # Stats sidebar
            with (
                ui.card()
                .classes(
                    "w-full lg:w-80 p-6 gap-4 stats-sidebar-card stats-sidebar vn-card"
                )
                .props("flat")
            ):
                ui.label("STATISTICHE").classes(
                    "text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                )
                stats = pdata["stats"]

                # Radar chart
                radar_data = [
                    {"name": "Energia", "value": stats["energy"]},
                    {"name": "Stress", "value": stats["stress"]},
                    {"name": "Salute", "value": stats["health"]},
                    {"name": "Integrità", "value": stats["integrity"]},
                    {"name": "Autostima", "value": stats["self_esteem"]},
                    {"name": "Occupabilità", "value": stats["employability"]},
                ]
                radar_option = {
                    "radar": {
                        "indicator": [
                            {"name": r["name"], "max": 100} for r in radar_data
                        ],
                        "shape": "circle",
                        "splitArea": {
                            "areaStyle": {
                                "color": [
                                    "rgba(255,255,255,0.02)",
                                    "rgba(255,255,255,0.05)",
                                ]
                            }
                        },
                        "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.1)"}},
                        "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.1)"}},
                    },
                    "series": [
                        {
                            "type": "radar",
                            "data": [
                                {
                                    "value": [s["value"] for s in radar_data],
                                    "name": "Profilo",
                                }
                            ],
                            "areaStyle": {"color": theme["accent"] + "40"},
                            "lineStyle": {"color": theme["accent"], "width": 2},
                            "itemStyle": {"color": theme["accent"]},
                        }
                    ],
                    "backgroundColor": "transparent",
                }
                ui.echart(radar_option).classes("w-full h-44")

                # Stat bars with pulse on critical
                _render_stats_section(stats)

                # FAZIONI
                _render_factions_section(pdata["factions"])

                # RELAZIONI con avatar
                _render_relationships_section(pdata["npcs"])

                # ULTIME SCELTE
                if choice_history:
                    ui.separator().classes("my-3 bg-gray-700")
                    ui.label("ULTIME SCELTE").classes(
                        "text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                    )
                    for h in choice_history[-5:]:
                        cat_color = cat_colors.get(h["category"], "#6b7280")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("circle", size="6px").style(f"color: {cat_color}")
                            ui.label(
                                h["text"][:40] + ("…" if len(h["text"]) > 40 else "")
                            ).classes("text-xs text-gray-400 truncate")

                # Personalità Manager
                mp = getattr(engine, "manager_personality", {})
                if mp:
                    ui.separator().classes("my-3 bg-gray-700")
                    ui.label("MANAGER").classes("text-sm font-bold text-gray-400 mb-1")
                    with ui.row().classes("items-center gap-1"):
                        ui.icon("person", size="14px").classes("text-gray-500")
                        ui.label(mp.get("type", "")).classes("text-xs text-gray-300")
                    ui.label(mp.get("description", "")).classes(
                        "text-[10px] text-gray-500 italic"
                    )

                # Fase Carriera
                phase = engine.get_career_phase()
                ui.separator().classes("my-3 bg-gray-700")
                ui.label("FASE").classes(
                    "text-xs font-bold text-gray-500 uppercase tracking-wider mb-1"
                )
                with ui.row().classes("items-center gap-1"):
                    ui.icon("timeline", size="14px").classes("text-gray-500")
                    ui.label(phase[1]).classes("text-xs text-gray-300")
                ui.label(phase[2]).classes("text-[10px] text-gray-500 italic")

                # STATO
                ui.separator().classes("my-3 bg-gray-700")
                ui.label("STATO").classes(
                    "text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                )

                risk_critical = sum(1 for s in stats.values() if s <= 20) + (
                    1 if stats["stress"] >= 80 else 0
                )
                risk_warning = sum(
                    1 for s in stats.values() if 20 < s <= 35 or 65 <= s < 80
                )

                if not engine.player.is_alive:
                    risk_label = "Terminato"
                    risk_color = "text-gray-500"
                elif (
                    risk_critical >= 3 or stats["stress"] >= 85 or stats["health"] <= 15
                ):
                    risk_label = "Pericolo Imminente"
                    risk_color = "text-red-400 font-bold"
                elif risk_critical >= 1 or risk_warning >= 3:
                    risk_label = "Critico"
                    risk_color = "text-orange-400 font-bold"
                elif risk_warning >= 1:
                    risk_label = "Moderato"
                    risk_color = "text-yellow-400"
                else:
                    risk_label = "Stabile"
                    risk_color = "text-green-400"

                with ui.row().classes("items-center gap-2"):
                    state_img = _state_icon(risk_label)
                    if not state_img:
                        state_img = _state_icon(engine.player.status)
                    if state_img:
                        ui.image(state_img).style(
                            "width: 36px; height: 36px; border-radius: 6px"
                        )
                    ui.label(risk_label).classes(f"{risk_color} text-base")
                ui.linear_progress(
                    value=min(stats["stress"] / 100, 1.0),
                    size="sm",
                    show_value=False,
                    color="red"
                    if stats["stress"] > 65
                    else "orange"
                    if stats["stress"] > 40
                    else "green",
                ).classes("w-full mt-1")
                ui.label("Stress").classes("text-xs text-gray-500")

                danger_stats = []
                if stats["stress"] >= 75:
                    danger_stats.append("Stress: rischio burnout")
                if stats["health"] <= 25:
                    danger_stats.append("Salute: critica")
                if stats["energy"] <= 20:
                    danger_stats.append("Energia: esaurita")
                if stats["self_esteem"] <= 20:
                    danger_stats.append("Autostima: a terra")
                if stats["manager_rep"] <= 20:
                    danger_stats.append("Rep. Manager: rischio licenziamento")
                for msg in danger_stats[:2]:
                    ui.label(f"⚠ {msg}").classes("text-xs text-red-400 mt-1")

            # Event + Choices
            with ui.column().classes("flex-1 gap-6 min-w-0 fade-in"):
                # Mini-evento giornaliero
                if engine.current_mini_event:
                    mini_text, mini_effects = engine.current_mini_event
                    with (
                        ui.card()
                        .classes("w-full p-4 border-l-4 border-blue-500/50 vn-card")
                        .props("flat")
                    ):
                        with ui.row().classes("items-center justify-between"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("coffee", size="18px").classes("text-blue-400")
                                ui.label("DAILY ROUTINE").classes(
                                    "text-xs font-black text-blue-400 tracking-tighter"
                                )
                            with ui.row().classes("gap-1"):
                                for k, v in mini_effects.items():
                                    color = (
                                        "text-green-400" if v > 0 else "text-red-400"
                                    )
                                    sign = "+" if v > 0 else ""
                                    label = _effect_label(k)[:6]
                                    ui.label(f"{label} {sign}{v}").classes(
                                        f"text-[10px] font-bold {color} px-1.5 py-0.5 rounded bg-black/20"
                                    )

                        ui.label(mini_text).classes(
                            "text-sm text-gray-300 italic mt-2 leading-relaxed"
                        )

                if event:
                    with ui.column().classes("w-full gap-2"):
                        with ui.row().classes("items-center justify-between"):
                            ui.badge(
                                event.category.replace("_", " ").upper(),
                                color="amber-9",
                            ).classes("px-3 py-1 text-[10px] font-bold tracking-widest")

                            with ui.row().classes("gap-2"):
                                if engine.real_cases_mode:
                                    ui.badge("CASO REALE", color="orange-10").classes(
                                        "px-2 py-0.5 text-[9px] font-black"
                                    )
                                if is_repeat:
                                    ui.label("🔄 DÉJÀ VU").classes(
                                        "text-[9px] text-gray-500 font-bold"
                                    )

                        # NPC portrait + narrative card (Visual Novel style)
                        npc_names = list(pdata["npcs"].keys())
                        npc_idx = (
                            (len(engine.history)) % max(len(npc_names), 1)
                            if npc_names
                            else 0
                        )
                        npc_trigger = npc_names[npc_idx] if npc_names else ""

                        with ui.row().classes("w-full gap-4 items-end"):
                            # NPC portrait
                            with ui.column().classes("items-center gap-1 shrink-0"):
                                nd = pdata["npcs"].get(npc_trigger, {})
                                nf = NPC_FACTION_MAP.get(npc_trigger, "")
                                nc = NPC_FACTION_COLORS.get(nf, "#6b7280")
                                portrait_url = _npc_portrait(npc_trigger, nd)
                                with ui.element("div").classes("relative inline-block"):
                                    ui.image(portrait_url).style(
                                        f"border-color: {nc}; width: 80px; height: 80px; border-radius: 20px; border: 2px solid; object-fit: cover"
                                    ).classes("npc-portrait")
                                    # Emote bubble overlay
                                    if event.choices:
                                        emote_icon = EMOTE_ICONS.get(
                                            event.choices[0].category
                                        )
                                        if emote_icon:
                                            emote_url = (
                                                f"{GFX_PATH}/personaggi/{emote_icon}"
                                            )
                                            ui.image(emote_url).style(
                                                "width: 28px; height: 28px; position: absolute; top: -8px; right: -8px; border-radius: 50%; border: 2px solid rgba(0,0,0,0.5); background: rgba(0,0,0,0.6)"
                                            )
                                ui.label(npc_trigger.upper()).classes(
                                    "text-[9px] font-black text-gray-500 tracking-tighter"
                                )

                            # Narrative Card
                            with (
                                ui.card()
                                .classes(
                                    "flex-1 p-6 event-card vn-card-highlight min-h-[140px]"
                                )
                                .props("flat")
                            ):
                                with ui.row().classes("items-start gap-3"):
                                    ev_icon = _event_icon(event)
                                    if ev_icon:
                                        ui.image(ev_icon).style(
                                            "width: 48px; height: 48px; border-radius: 8px; flex-shrink: 0"
                                        )
                                    ui.markdown(event.text).classes(
                                        "narrative-text prose prose-invert max-w-none flex-1"
                                        " [&_strong]:text-blue-300 [&_strong]:font-bold"
                                    )

                    n_choices = len(event.choices)
                    with ui.column().classes("w-full gap-3 mt-2"):
                        if n_choices > 1:
                            ui.label("PRENDI UNA DECISIONE").classes(
                                "text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1"
                            )

                    # Timer per scelte critiche (M12)
                    _timer_choice_idx = -1
                    if n_choices > 1:
                        _timer_choice_idx = random.randint(0, n_choices - 1)

                    # Track decision time (start counting from event render)
                    global _decision_start
                    _decision_start = __import__("time").time()

                    for i, choice in enumerate(event.choices):

                        def handle_choice_cb(idx=0, evt=None, ch=None):
                            return lambda: _make_choice(idx, evt, ch)

                        timer_class = ""
                        if i == _timer_choice_idx and n_choices > 1:
                            timer_class = " timer-choice"

                        label = f"{chr(65 + i)}. {choice.text}"
                        if n_choices == 1:
                            label = "Continua →"

                        with (
                            ui.button(
                                on_click=handle_choice_cb(i, event, choice),
                            )
                            .classes(f"w-full choice-btn {timer_class} fade-in")
                            .props("flat no-caps")
                        ):
                            with ui.column().classes("w-full items-start gap-1"):
                                ui.label(label).classes("text-left")

                                # Effetti sempre visibili (chip)
                                if choice.effects:
                                    with ui.row().classes("gap-1 mt-1 flex-wrap"):
                                        for ek, ev in list(choice.effects.items())[:4]:
                                            cls = "pos" if ev > 0 else "neg"
                                            sign = "+" if ev > 0 else ""
                                            ui.label(
                                                f"{_effect_label(ek)}: {sign}{ev}"
                                            ).classes(f"effect-chip {cls}")

                            # Timer su scelta critica
                            if i == _timer_choice_idx and n_choices > 1:
                                timer_id = f"timer_{uuid.uuid4().hex[:6]}"
                                ui.label().classes("timer-ring").props(f"id={timer_id}")
                                ui.run_javascript(f"""
                                    (function() {{
                                        let sec = 15;
                                        const el = document.getElementById('{timer_id}');
                                        if (!el) return;
                                        el.innerHTML = '⏱ ' + sec + 's';
                                        const iv = setInterval(() => {{
                                            sec--;
                                            if (el) el.innerHTML = '⏱ ' + sec + 's';
                                            if (sec <= 0) {{
                                                clearInterval(iv);
                                                el.closest('button')?.click();
                                            }}
                                        }}, 1000);
                                    }})();
                                """)

                            # Tooltip (M3)
                            with ui.tooltip().classes(
                                "p-2 bg-gray-800 border border-gray-600 rounded"
                            ):
                                for effect_key, effect_val in choice.effects.items():
                                    sign = "+" if effect_val > 0 else ""
                                    ui.label(
                                        f"{_effect_label(effect_key)}: {sign}{effect_val}"
                                    ).classes("text-xs font-mono")

    # Mobile bottom bar
    if _layout_mode == "mobile":
        with ui.row().classes("w-full items-center justify-between mobile-bottom-bar"):
            with ui.row().classes("items-center gap-2"):
                ui.label("Giorno").classes(
                    "text-[9px] font-bold text-gray-500 uppercase tracking-widest"
                )
                ui.label(str(player.days_survived)).classes(
                    "text-lg font-black text-white"
                )
            with ui.row().classes("items-center gap-2"):
                ui.icon("speed", size="16px").classes(
                    "text-red-400"
                    if stats["stress"] > 65
                    else "text-yellow-400"
                    if stats["stress"] > 40
                    else "text-green-400"
                )
                ui.label(f"{stats['stress']}%").classes(
                    "text-xs font-bold font-mono text-gray-300"
                )
            with ui.row().classes("items-center gap-1"):
                ui.button(
                    icon="menu",
                    on_click=lambda: ui.run_javascript(
                        'document.querySelector(".stats-sidebar").classList.toggle("open")'
                    ),
                ).props("flat round color=white dense")
                ui.button(icon="help", on_click=_show_help).props(
                    "flat round color=white dense"
                )
                ui.button(icon="hub", on_click=_show_decision_graph).props(
                    "flat round color=blue dense"
                )
                ui.button(icon="logout", on_click=_exit_game).props(
                    "flat round color=red dense"
                )


def _render_game_over():
    player = engine.player
    ending = determine_ending(player)

    # Identifica se l'agente si è comportato bene rispetto al suo profilo
    is_top_performer = False
    if current_agent_id and current_agent_id in swarm.agents:
        agent = swarm.agents[current_agent_id]
        # Un top performer è chi sopravvive più della media del suo profilo o ha stress basso
        analytics = swarm.get_swarm_analytics()
        profile_stats = analytics.get("profile_impact", {}).get(agent.profile.name, {})
        avg_days = profile_stats.get("avg_days", 0)
        if player.days_survived > avg_days * 1.2 or (player.is_alive and player.stress < 40):
            is_top_performer = True

    end_session(session_id, player.days_survived, player.status, ending)
    record_tags(session_id, player.tags)
    stats = get_stats_dict(engine)

    with ui.column().classes("w-full max-w-4xl mx-auto py-12 fade-in report-card"):
        with (
            ui.card()
            .classes(
                "w-full p-12 text-center vn-card vn-card-highlight overflow-hidden relative"
            )
            .props("flat")
        ):
            # Background effect for game over
            ui.html(
                f'<div style="position:absolute; top:-50px; right:-50px; width:200px; height:200px; background:var(--theme-accent); opacity:0.1; border-radius:50%; filter:blur(60px);"></div>'
            )

            ui.label("VALUTAZIONE CARRIERA CONCLUSO").classes(
                "text-[10px] font-black text-gray-500 tracking-[0.3em] mb-2"
            )
            ui.label(ending).classes(
                "text-5xl font-black text-white mt-2 mb-2 tracking-tighter"
            )
            with ui.row().classes("items-center justify-center gap-3 mt-2"):
                state_img = _state_icon(player.status)
                if state_img:
                    ui.image(state_img).style(
                        "width: 48px; height: 48px; border-radius: 8px"
                    )
                ui.badge(
                    player.status.upper(),
                    color="red-10"
                    if "Burnout" in player.status or "Licenziato" in player.status
                    else "blue-10",
                ).classes("px-4 py-1 text-xs font-bold")

            ui.label(
                f"Hai resistito {player.days_survived} giorni operativi presso {player.company_type}."
            ).classes("text-gray-400 mt-6 text-lg italic")

            # Grafico storico stress/tempo
            hist = getattr(engine, "stats_history", [])
            if len(hist) >= 3:
                stress_series = [s.get("stress", 0) for s in hist]
                energy_series = [s.get("energy", 0) for s in hist]
                days_labels = list(range(len(hist)))
                stress_chart = {
                    "tooltip": {"trigger": "axis"},
                    "legend": {
                        "data": ["Stress", "Energia"],
                        "textStyle": {"color": "#999"},
                    },
                    "xAxis": {
                        "type": "category",
                        "data": days_labels,
                        "axisLabel": {"color": "#666", "fontSize": 9},
                    },
                    "yAxis": {
                        "type": "value",
                        "max": 100,
                        "axisLabel": {"color": "#666"},
                        "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}},
                    },
                    "series": [
                        {
                            "name": "Stress",
                            "type": "line",
                            "data": stress_series,
                            "smooth": True,
                            "lineStyle": {"color": "#f87171", "width": 2},
                            "areaStyle": {"color": "rgba(248,113,113,0.1)"},
                            "symbol": "none",
                        },
                        {
                            "name": "Energia",
                            "type": "line",
                            "data": energy_series,
                            "smooth": True,
                            "lineStyle": {"color": "#4ade80", "width": 2},
                            "areaStyle": {"color": "rgba(74,222,128,0.1)"},
                            "symbol": "none",
                        },
                    ],
                    "backgroundColor": "transparent",
                    "grid": {
                        "left": "10%",
                        "right": "5%",
                        "top": "15%",
                        "bottom": "10%",
                    },
                }
                ui.echart(stress_chart).classes("w-full h-36 mt-4")

            # Radar finale
            radar_data = [
                {"name": "Energia", "value": stats["energy"]},
                {"name": "Stress", "value": stats["stress"]},
                {"name": "Salute", "value": stats["health"]},
                {"name": "Integrità", "value": stats["integrity"]},
                {"name": "Autostima", "value": stats["self_esteem"]},
                {"name": "Occupabilità", "value": stats["employability"]},
            ]
            radar_option = {
                "radar": {
                    "indicator": [{"name": r["name"], "max": 100} for r in radar_data],
                    "shape": "circle",
                    "splitArea": {
                        "areaStyle": {
                            "color": [
                                "rgba(255,255,255,0.02)",
                                "rgba(255,255,255,0.05)",
                            ]
                        }
                    },
                    "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.1)"}},
                    "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.1)"}},
                },
                "series": [
                    {
                        "type": "radar",
                        "data": [
                            {
                                "value": [s["value"] for s in radar_data],
                                "name": "Profilo",
                            }
                        ],
                        "areaStyle": {"color": "rgba(168,85,247,0.3)"},
                        "lineStyle": {"color": "#a855f7", "width": 2},
                        "itemStyle": {"color": "#a855f7"},
                    }
                ],
                "backgroundColor": "transparent",
            }
            ui.echart(radar_option).classes("w-full h-48 mt-4")

            # Tempi di decisione
            dt = getattr(player, "decision_times", [])
            if dt:
                avg_dt = sum(dt) / len(dt) / 1000
                fast = sum(1 for t in dt if t < 5000)
                slow = sum(1 for t in dt if t >= 15000)
                ui.label(
                    f"Tempo medio decisione: {avg_dt:.1f}s · Rapide: {fast} · Lente (>15s): {slow}"
                ).classes("text-xs text-gray-500 mt-2")

            with ui.row().classes("w-full justify-center gap-6 mt-6"):
                for key, label, color in [
                    ("energy", "Energia", "#4ade80"),
                    ("stress", "Stress", "#f87171"),
                    ("health", "Salute", "#22d3ee"),
                    ("integrity", "Integrità", "#a78bfa"),
                ]:
                    with ui.column().classes("items-center"):
                        ui.linear_progress(
                            value=stats[key] / 100,
                            size="md",
                            color=color,
                            show_value=False,
                        ).classes("w-20")
                        ui.label(f"{label}: {stats[key]}%").classes(
                            "text-xs text-gray-400"
                        )

        tags = player.tags
        total_tags = sum(tags.values())
        if total_tags > 0:
            with ui.card().classes("w-full p-6 mt-4 vn-card").props("flat"):
                ui.label("PROFILO COMPORTAMENTALE").classes(
                    "text-lg font-bold text-gray-300 mb-4"
                )
                for tag, count in sorted(
                    tags.items(), key=lambda x: x[1], reverse=True
                ):
                    if count > 0:
                        perc = (count / total_tags) * 100
                        with ui.row().classes("items-center gap-3"):
                            ui.linear_progress(
                                value=perc / 100,
                                size="sm",
                                color="amber",
                                show_value=False,
                            ).classes("w-40")
                            ui.label(
                                f"{tag.replace('_', ' ').title()}: {perc:.1f}%"
                            ).classes("text-sm text-gray-400")

        if player.achievements:
            with ui.card().classes("w-full p-6 mt-4").props("flat"):
                ui.label("ACHIEVEMENT").classes("text-lg font-bold text-gray-300 mb-3")
                for ach in player.achievements:
                    ui.badge(f"\U0001f3c6 {ach}", color="positive").classes("mr-2 mb-2")

        # Report dettagliato domande/risposte (per HR DSS)
        if current_agent_id and current_agent_id in swarm.agents:
            agent = swarm.agents[current_agent_id]

            # Nuova Sezione: Commento Discorsivo Strategico (v3.2)
            report = StrategicAnalyzer.analyze_agent(agent)
            if "discursive_comment" in report:
                with ui.card().classes("w-full p-6 mt-4 vn-card border-l-4 border-purple-500").props("flat"):
                    ui.label("ANALISI STRATEGICA POSTERIORI").classes("text-[10px] font-black text-purple-400 tracking-[0.3em] mb-2")
                    ui.label(report["strategy_name"].upper()).classes("text-2xl font-black text-white mb-4")
                    ui.markdown(report["discursive_comment"]).classes("text-base text-gray-300 italic leading-relaxed")

            with ui.card().classes("w-full p-6 mt-4 vn-card").props("flat"):
                ui.label("REPORT DETTAGLIATO DECISIONI (DSS)").classes("text-lg font-bold text-gray-300 mb-4")

                # Raggruppa per categoria
                decisions_by_cat = {}
                for dec in agent.memory.decisions:
                    cat = dec.category
                    if cat not in decisions_by_cat: decisions_by_cat[cat] = []
                    decisions_by_cat[cat].append(dec)

                with ui.tabs().classes('w-full') as tabs:
                    for cat in decisions_by_cat:
                        ui.tab(cat)

                with ui.tab_panels(tabs, value=next(iter(decisions_by_cat)) if decisions_by_cat else None).classes('w-full bg-transparent'):
                    for cat, decs in decisions_by_cat.items():
                        with ui.tab_panel(cat):
                            with ui.column().classes('w-full gap-2'):
                                for d in decs:
                                    with ui.row().classes('w-full p-2 bg-white/5 rounded border-l-2 items-start').style(f"border-color: {cat_colors.get(cat, '#666')}"):
                                        with ui.column().classes('flex-1 gap-1'):
                                            ui.label(f"GIORNO {d.day}").classes('text-[9px] font-black text-gray-500')
                                            # Cerchiamo il testo dell'evento
                                            ev = engine.event_manager.get_event(d.event_id)
                                            if ev:
                                                ui.label(ev.text[:100] + "...").classes('text-xs italic text-gray-400')
                                            ui.label(d.choice_text).classes('text-sm text-white font-bold')

        if is_top_performer:
            with ui.card().classes("w-full p-6 mt-4 vn-card border-2 border-green-500/50 bg-green-500/5").props("flat"):
                with ui.row().classes("items-center gap-4"):
                    ui.icon("emoji_events", size="48px").classes("text-yellow-400")
                    with ui.column().classes("gap-0"):
                        ui.label("TOP PERFORMER RILEVATO").classes("text-xs font-black text-green-400 tracking-widest")
                        ui.label("Efficienza Adattiva Superiore").classes("text-xl font-bold text-white")
                ui.label(f"L'agente ha superato del {((player.days_survived/avg_days)-1)*100:.0f}% la sopravvivenza media del profilo {agent.profile.name}." if avg_days > 0 else "L'agente ha mostrato una resilienza eccezionale.").classes("text-sm text-gray-300 mt-2")

        with ui.card().classes("w-full p-6 mt-4").props("flat"):
            ui.label("ANALISI ANTROPOLOGICA").classes(
                "text-lg font-bold text-gray-300 mb-3"
            )
            if player.factions["Ribelli"] > 30:
                ui.label(
                    "- Hai mostrato una forte tendenza alla resistenza attiva, "
                    "prioritizzando l'integrità individuale."
                ).classes("text-sm text-gray-400")
            if player.factions["Fedelissimi"] > 30:
                ui.label(
                    "- Il tuo adattamento è stato di tipo opportunistico, "
                    "integrando i valori dominanti dell'organizzazione."
                ).classes("text-sm text-gray-400")
            if player.stress > 70:
                ui.label(
                    "- L'esposizione prolungata a dinamiche tossiche ha eroso "
                    "le tue barriere psicologiche (Burnout Alert)."
                ).classes("text-sm text-gray-400")

        with ui.row().classes("w-full justify-center mt-6 mb-12 gap-3"):
            ui.button("Gioca Ancora", icon="replay", on_click=_play_again).props(
                "color=positive size=lg"
            )
            ui.button(
                "📷 Esporta Report", icon="download", on_click=_export_report
            ).props("flat size=lg").classes("text-gray-400")
            ui.button(
                "🕸 Grafo Decisionale", icon="hub", on_click=_show_decision_graph
            ).props("flat size=lg").classes("text-gray-400")


# ── Actions ──


def _make_choice(idx: int, event, choice):
    global stats_before, choice_history, _decision_start, current_agent_id
    decision_time = (
        int((__import__("time").time() - _decision_start) * 1000)
        if _decision_start > 0
        else 0
    )

    stats_before = get_stats_dict(engine)

    if current_agent_id and current_human_id:
        # Modalità laboratorio/possesso
        res = swarm.human_make_choice(current_human_id, idx)
        if "error" in res:
            ui.notify(res["error"], type="negative")
            return
    else:
        # Modalità classica
        engine.handle_choice(idx)

    stats_after = get_stats_dict(engine)

    if decision_time > 0:
        engine.player.decision_times.append(decision_time)

    record_choice(
        session_id,
        engine.player.days_survived,
        event.id,
        choice.id,
        choice.text,
        choice.category,
        stats_before,
        stats_after,
        decision_time=decision_time,
    )

    choice_history.append(
        {
            "text": choice.text,
            "category": choice.category,
        }
    )

    # Update career phase
    phase = engine.get_career_phase()
    engine.player.career_phase = phase[1]

    deltas = {}
    for key in stats_before:
        d = stats_after[key] - stats_before[key]
        if d != 0:
            deltas[key] = d

    _show_choice_feedback(deltas, choice.category)


def _show_choice_feedback(deltas: dict, category: str):
    stat_labels = {
        "energy": "Energia",
        "stress": "Stress",
        "health": "Salute",
        "integrity": "Integrità",
        "self_esteem": "Autostima",
        "employability": "Occupabilità",
        "manager_rep": "Rep. Manager",
        "team_rep": "Rep. Team",
    }
    stat_colors = {
        "energy": "#4ade80",
        "stress": "#f87171",
        "health": "#22d3ee",
        "integrity": "#a78bfa",
        "self_esteem": "#fbbf24",
        "employability": "#34d399",
        "manager_rep": "#fb923c",
        "team_rep": "#60a5fa",
    }

    with (
        ui.dialog().props(
            "persistent transition-show=scale transition-hide=scale"
        ) as dialog,
        ui.card().classes("p-8 min-w-[320px] vn-card border-t-4 border-blue-500"),
    ):
        ui.label("CONSEGUENZE").classes(
            "text-[10px] font-black text-blue-400 tracking-[0.3em] mb-1"
        )
        ui.label(category.upper()).classes(
            "text-xl font-bold text-white mb-6 tracking-tight"
        )

        has_effects = False
        with ui.column().classes("w-full gap-2"):
            for key in deltas:
                has_effects = True
                delta = deltas[key]
                sign = "+" if delta > 0 else ""
                color = stat_colors.get(key, "#9ca3af")
                label = stat_labels.get(key, key)

                is_pos = (delta > 0 and key != "stress") or (
                    delta < 0 and key == "stress"
                )
                bg_color = (
                    "rgba(74, 222, 128, 0.1)" if is_pos else "rgba(248, 113, 113, 0.1)"
                )
                text_color = "#4ade80" if is_pos else "#f87171"
                arrow = "▲" if delta > 0 else "▼"

                with (
                    ui.row()
                    .classes(
                        "w-full items-center justify-between px-4 py-3 rounded-xl border border-white/5"
                    )
                    .style(f"background: {bg_color}")
                ):
                    ui.label(label.upper()).classes(
                        "text-[10px] font-extrabold text-gray-300 tracking-tighter"
                    )
                    ui.label(f"{arrow} {sign}{delta}").style(
                        f"color: {text_color}"
                    ).classes("text-sm font-black font-mono")

        if not has_effects:
            ui.label("Nessun impatto sistemico rilevato.").classes(
                "text-sm text-gray-500 italic text-center w-full my-4"
            )

        def advance():
            global screen
            dialog.close()
            if engine and engine.is_game_over():
                screen = "game_over"
            else:
                if engine:
                    engine.next_turn()
                screen = "game_over" if engine and engine.is_game_over() else "game"
                if current_agent_id:
                    save_agent(swarm.agents[current_agent_id].to_dict())
            page.refresh()

        ui.button("PROSEGUI", on_click=advance).props("color=blue size=lg").classes(
            "mt-8 w-full font-bold rounded-xl shadow-lg shadow-blue-500/20"
        )
    dialog.open()


def _render_tutorial():
    steps = [
        {
            "title": "Benvenuto in Burnout Simulator",
            "icon": "auto_awesome",
            "text": "Questa è una simulazione di antropologia organizzativa. <b>Ogni scelta conta:</b> le tue decisioni influenzeranno le tue statistiche, i rapporti con i colleghi e il finale della partita.",
        },
        {
            "title": "Le Statistiche",
            "icon": "query_stats",
            "text": "A sinistra trovi il <b>radar psicologico</b> e le barre numeriche. Tienile d'occhio: stress alto e salute bassa possono portare al burnout. Le barre pulsano quando sono in zona critica.",
        },
        {
            "title": "Fazioni e NPC",
            "icon": "groups",
            "text": "I tuoi colleghi appartengono a fazioni (Fedelissimi, Gruppo Silenzioso, Ribelli). Guadagnare o perdere fiducia con loro cambia il gioco. Ogni NPC ha un avatar colorato in base alla fazione.",
        },
        {
            "title": "Le Scelte",
            "icon": "ads_click",
            "text": "Le scelte mostrano gli effetti direttamente nel bottone (+/-). Su alcune scelte critiche parte un <b>timer di 15 secondi</b> per simulare la pressione lavorativa. Non farti prendere dal panico!",
        },
        {
            "title": "Pronto?",
            "icon": "rocket_launch",
            "text": "Ricorda: non esiste la scelta giusta. Esiste la scelta <b>coerente</b> con il tuo stile. Buona fortuna.",
        },
    ]
    if _tutorial_step >= len(steps):
        return
    step = steps[_tutorial_step]
    with ui.column().classes("tutorial-overlay fade-in"):
        with (
            ui.card()
            .classes("tutorial-card vn-card border-t-4 border-purple-500")
            .props("flat")
        ):
            ui.icon(step["icon"], size="48px").classes("text-purple-400 mb-4")
            ui.label(step["title"]).classes(
                "text-2xl font-black text-white mb-4 tracking-tight"
            )
            ui.html(step["text"]).classes(
                "text-base text-gray-300 leading-relaxed text-center"
            )

            with ui.row().classes("w-full items-center justify-center mt-8 gap-1"):
                for i in range(len(steps)):
                    color = "bg-purple-500" if i == _tutorial_step else "bg-gray-700"
                    ui.html(f'<div class="w-2 h-2 rounded-full {color}"></div>')

            with ui.row().classes("justify-center gap-4 mt-8 w-full"):
                if _tutorial_step > 0:
                    ui.button("INDIETRO", on_click=lambda: _tutorial_prev()).props(
                        "flat"
                    ).classes("text-gray-500 font-bold")
                btn_label = (
                    "INIZIA ORA" if _tutorial_step == len(steps) - 1 else "AVANTI"
                )
                ui.button(btn_label, on_click=_tutorial_next).props(
                    "color=purple-10 elevation=0"
                ).classes("px-8 font-black rounded-xl")


def _tutorial_next():
    global _tutorial_step, _tutorial_active
    if _tutorial_step >= 4:
        _tutorial_active = False
    else:
        _tutorial_step += 1
    page.refresh()


def _tutorial_prev():
    global _tutorial_step
    if _tutorial_step > 0:
        _tutorial_step -= 1
    page.refresh()


def _exit_game():
    global screen
    screen = "game_over"
    page.refresh()


def _play_again():
    global \
        screen, \
        engine, \
        session_id, \
        choice_history, \
        current_human_id, \
        current_agent_id
    engine = None
    session_id = None
    choice_history = []
    current_human_id = None
    current_agent_id = None
    screen = "start"
    page.refresh()


def _show_stats_dialog():
    stats = get_stats_dict(engine)
    pdata = engine.player.to_dict()
    with ui.dialog() as dialog, ui.card().classes("p-6 vn-card"):
        ui.label("Statistiche Dettagliate").classes("text-lg font-bold mb-4")
        for label, key, color in bars_def:
            with ui.row().classes("w-full items-center justify-between"):
                ui.label(label).classes("text-sm")
                val = stats[key]
                val_color = (
                    "#ef4444"
                    if (val <= 20 or (key == "stress" and val >= 80))
                    else color
                )
                ui.label(f"{val}%").style(f"color: {val_color}")
            ui.linear_progress(
                value=stats[key] / 100, size="sm", color=color, show_value=False
            )
        ui.label("FAZIONI").classes("text-sm font-bold mt-4 mb-2")
        for fname, fscore in pdata["factions"].items():
            fcol = NPC_FACTION_COLORS.get(fname, "#6b7280")
            with ui.row().classes("items-center gap-2"):
                ui.icon("circle", size="8px").style(f"color: {fcol}")
                ui.label(f"{fname}: {fscore}%").classes("text-sm")
        ui.button("Chiudi", on_click=dialog.close).props("flat")
    dialog.open()


def _export_report():
    player = engine.player
    stats = get_stats_dict(engine)
    ending = determine_ending(player)
    pdata = player.to_dict()

    tags_rows = "".join(
        f"<tr><td>{tag.replace('_', ' ').title()}</td><td>{count}</td></tr>\n"
        for tag, count in sorted(player.tags.items(), key=lambda x: x[1], reverse=True)
        if count
    )
    archs_rows = "".join(
        f"<tr><td>{fname}</td><td>{fscore}%</td></tr>\n"
        for fname, fscore in pdata["factions"].items()
    )
    npcs_rows = "".join(
        f"<tr><td>{nname}</td><td>{ndata['trust']}%</td><td>{ndata['respect']}%</td><td>{ndata['fear']}%</td></tr>\n"
        for nname, ndata in pdata["npcs"].items()
    )
    status_badge = (
        "badge-red"
        if "Burnout" in player.status or "Licenziato" in player.status
        else "badge-blue"
    )

    html = f"""<!DOCTYPE html>
<html lang="it">
<head><meta charset="utf-8"><title>Burnout Report</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a1a; color: #e2e8f0; padding: 40px; max-width: 800px; margin: auto; }}
h1 {{ color: #3b82f6; font-size: 28px; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
h2 {{ color: #94a3b8; font-size: 18px; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0 20px; }}
th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
th {{ color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; }}
td {{ color: #cbd5e1; }}
.badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
.badge-red {{ background: rgba(239,68,68,0.2); color: #f87171; }}
.badge-blue {{ background: rgba(59,130,246,0.2); color: #60a5fa; }}
.footer {{ margin-top: 40px; font-size: 11px; color: #475569; text-align: center; }}
</style></head>
<body>
<h1>Burnout Simulator — Report Carriera</h1>
<p style="color:#94a3b8;font-size:14px;">{player.name} · {player.company_type} · {player.days_survived} giorni</p>
<h2>Finale: {ending}</h2>
<p>Stato: <span class="badge {status_badge}">{player.status}</span></p>
<h2>Statistiche Finali</h2>
<table>
<tr><th>Statistica</th><th>Valore</th></tr>
<tr><td>Energia</td><td>{stats["energy"]}%</td></tr>
<tr><td>Stress</td><td>{stats["stress"]}%</td></tr>
<tr><td>Salute</td><td>{stats["health"]}%</td></tr>
<tr><td>Integrità</td><td>{stats["integrity"]}%</td></tr>
<tr><td>Autostima</td><td>{stats["self_esteem"]}%</td></tr>
<tr><td>Occupabilità</td><td>{stats["employability"]}%</td></tr>
<tr><td>Rep. Manager</td><td>{stats["manager_rep"]}%</td></tr>
<tr><td>Rep. Team</td><td>{stats["team_rep"]}%</td></tr>
</table>
<h2>Fazioni</h2>
<table><tr><th>Fazione</th><th>Allineamento</th></tr>
{archs_rows}</table>
<h2>Relazioni</h2>
<table><tr><th>NPC</th><th>Fiducia</th><th>Rispetto</th><th>Paura</th></tr>
{npcs_rows}</table>
<h2>Profilo Comportamentale</h2>
<table><tr><th>Tratto</th><th>Conteggio</th></tr>
{tags_rows}</table>
<p class="footer">Generato da Burnout Simulator v2.0</p>
</body></html>"""

    b64 = base64.b64encode(html.encode()).decode()
    safe_name = player.name.replace(" ", "_")
    ui.run_javascript(f"""
        var a = document.createElement('a');
        a.download = 'burnout-report-{safe_name}.html';
        a.href = 'data:text/html;base64,{b64}';
        a.click();
    """)


def _show_decision_graph():
    if not engine or not engine.graph.history:
        ui.notify("Nessun dato disponibile per il grafo", type="warning")
        return

    graph = engine.graph
    event_mgr = engine.event_manager
    history = graph.history

    nodes_map = {}
    edges = []

    for entry in history:
        ev_id = entry["event_id"]
        ch_id = entry["choice_id"]
        nxt = entry.get("next_event_id")

        if ev_id not in nodes_map:
            ev = event_mgr.get_event(ev_id)
            cat = ev.category if ev else "unknown"
            cat_colors_map = {
                "micromanagement": "#3b82f6",
                "mobbing": "#ef4444",
                "favoritismo": "#eab308",
                "burnout": "#f97316",
                "scapegoating": "#a855f7",
            }
            nodes_map[ev_id] = {
                "id": ev_id,
                "name": ev_id.replace("_", " ")[:25],
                "symbolSize": 20,
                "itemStyle": {"color": cat_colors_map.get(cat, "#6b7280")},
                "category": cat,
            }

        if nxt and nxt not in nodes_map:
            ev = event_mgr.get_event(nxt)
            if ev:
                cat = ev.category if ev else "unknown"
                cat_colors_map = {
                    "micromanagement": "#3b82f6",
                    "mobbing": "#ef4444",
                    "favoritismo": "#eab308",
                    "burnout": "#f97316",
                    "scapegoating": "#a855f7",
                }
                nodes_map[nxt] = {
                    "id": nxt,
                    "name": nxt.replace("_", " ")[:25],
                    "symbolSize": 16,
                    "itemStyle": {"color": cat_colors_map.get(cat, "#6b7280")},
                    "category": "consequence",
                }

        ev = event_mgr.get_event(ev_id)
        choice_text = ""
        if ev:
            for c in ev.choices:
                if c.id == ch_id:
                    choice_text = c.category
                    break

        edge_color = {
            "COMPLIANCE": "#3b82f6",
            "RESISTANCE": "#ef4444",
            "NEGOTIATION": "#eab308",
            "ESCAPE": "#22c55e",
        }.get(choice_text, "#6b7280")

        target = nxt if nxt else ""
        if target:
            edges.append(
                {
                    "source": ev_id,
                    "target": target,
                    "label": {
                        "formatter": choice_text,
                        "fontSize": 9,
                        "color": edge_color,
                    },
                    "lineStyle": {"color": edge_color, "width": 1.5, "curveness": 0.2},
                }
            )

    option = {
        "tooltip": {"formatter": "{b}"},
        "series": [
            {
                "type": "graph",
                "layout": "force",
                "force": {"repulsion": 300, "edgeLength": 120},
                "draggable": True,
                "roam": True,
                "data": list(nodes_map.values()),
                "edges": edges,
                "categories": [
                    {"name": "micromanagement", "itemStyle": {"color": "#3b82f6"}},
                    {"name": "mobbing", "itemStyle": {"color": "#ef4444"}},
                    {"name": "favoritismo", "itemStyle": {"color": "#eab308"}},
                    {"name": "burnout", "itemStyle": {"color": "#f97316"}},
                    {"name": "scapegoating", "itemStyle": {"color": "#a855f7"}},
                    {"name": "consequence", "itemStyle": {"color": "#6b7280"}},
                ],
                "lineStyle": {"color": "source", "curveness": 0.3},
                "label": {
                    "show": True,
                    "position": "bottom",
                    "fontSize": 10,
                    "color": "#ccc",
                },
                "emphasis": {"focus": "adjacency", "lineStyle": {"width": 3}},
            }
        ],
        "backgroundColor": "transparent",
    }

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-4xl p-4 vn-card"):
        with ui.row().classes("w-full items-center justify-between mb-2"):
            ui.label("Grafo Decisionale").classes("text-lg font-bold text-gray-200")
            ui.button("", icon="close", on_click=dialog.close).props("flat").classes(
                "text-gray-400"
            )
        ui.echart(option).classes("w-full h-[500px]")
        ui.label(
            f"{len(nodes_map)} nodi · {len(edges)} connessioni · trascina per esplorare"
        ).classes("text-xs text-gray-500 text-center mt-1")
    dialog.open()


def _go_analytics():
    global screen
    screen = "analytics"
    page.refresh()


def _render_analytics():
    db_path = os.path.join(os.path.dirname(__file__), "database", "analytics.db")
    with ui.column().classes("w-full max-w-4xl mx-auto"):
        with ui.row().classes("w-full items-center justify-between mb-4 pb-3 top-bar"):
            ui.label("📊 Dashboard Analytics").classes("text-2xl font-bold text-white")
            ui.button("← Torna al Menu", on_click=lambda: _play_again()).props(
                "flat"
            ).classes("text-gray-400")

        if not os.path.exists(db_path):
            ui.label("Nessun dato analytics ancora disponibile.").classes(
                "text-gray-400"
            )
            return

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Finali più ottenuti
            cur.execute("""
                SELECT ending, COUNT(*) as cnt FROM sessions
                WHERE ending IS NOT NULL AND ending != ''
                GROUP BY ending ORDER BY cnt DESC LIMIT 10
            """)
            ending_data = cur.fetchall()

            # Scelte per categoria
            cur.execute("""
                SELECT category, COUNT(*) as cnt FROM choices
                GROUP BY category ORDER BY cnt DESC
            """)
            cat_data = cur.fetchall()

            # Sopravvivenza media per archetipo
            cur.execute("""
                SELECT company_type, ROUND(AVG(days_survived), 1) as avg_days,
                       COUNT(*) as sessions
                FROM sessions
                GROUP BY company_type ORDER BY avg_days DESC
            """)
            surv_data = cur.fetchall()

            # Totale sessioni
            cur.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cur.fetchone()[0]

            conn.close()
        except sqlite3.Error:
            ui.label("Errore lettura database.").classes("text-gray-400")
            return

        with ui.grid(columns=2).classes("w-full gap-4"):
            with ui.card().classes("p-4 vn-card").props("flat tight"):
                ui.label("Finali più ottenuti").classes(
                    "text-sm font-bold text-gray-300 mb-2"
                )
                total = sum(r[1] for r in ending_data) or 1
                for name, cnt in ending_data:
                    perc = cnt / total * 100
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.label(name).classes("text-xs text-gray-400 flex-1")
                        ui.label(f"{cnt}").classes("text-xs font-mono text-gray-300")
                        ui.linear_progress(
                            value=perc / 100, size="xs", color="amber", show_value=False
                        ).classes("w-16")

            with ui.card().classes("p-4 vn-card").props("flat tight"):
                ui.label("Scelte per categoria").classes(
                    "text-sm font-bold text-gray-300 mb-2"
                )
                total_cat = sum(r[1] for r in cat_data) or 1
                for name, cnt in cat_data:
                    perc = cnt / total_cat * 100
                    cat_color = cat_colors.get(name, "#6b7280")
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.icon("circle", size="6px").style(f"color: {cat_color}")
                        ui.label(name).classes("text-xs text-gray-400 flex-1")
                        ui.label(f"{cnt}").classes("text-xs font-mono text-gray-300")
                        ui.linear_progress(
                            value=perc / 100, size="xs", color="amber", show_value=False
                        ).classes("w-16")

        # Tabella sopravvivenza
        with ui.card().classes("w-full p-4 mt-4 vn-card").props("flat"):
            ui.label(
                f"Sopravvivenza media per archetipo (totale: {total_sessions} partite)"
            ).classes("text-sm font-bold text-gray-300 mb-2")
            for arch, avg, sessions in surv_data:
                with ui.row().classes("w-full items-center gap-2"):
                    color = ARCHETYPE_THEMES.get(arch, {}).get("accent", "#6b7280")
                    ui.icon("circle", size="6px").style(f"color: {color}")
                    ui.label(arch).classes("text-xs text-gray-400 w-36")
                    ui.label(f"{avg} giorni").classes(
                        "text-xs font-mono text-gray-300 w-20"
                    )
                    ui.linear_progress(
                        value=min(float(avg) / 50, 1.0),
                        size="xs",
                        color="primary",
                        show_value=False,
                    ).classes("flex-1")
                    ui.label(f"({sessions} partite)").classes("text-xs text-gray-500")

        # Ultime partite
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT name, company_type, days_survived, ending, status
                FROM sessions ORDER BY rowid DESC LIMIT 10
            """)
            recent = cur.fetchall()
            conn.close()
        except sqlite3.Error:
            recent = []

        if recent:
            with ui.card().classes("w-full p-4 mt-4 vn-card").props("flat"):
                ui.label("Ultime partite").classes(
                    "text-sm font-bold text-gray-300 mb-2"
                )
                for name, arch, days, ending, status in recent:
                    with ui.row().classes(
                        "w-full items-center gap-2 border-b border-gray-800 pb-1"
                    ):
                        ui.label(name).classes("text-xs text-gray-300 w-24 truncate")
                        ui.label(arch).classes("text-xs text-gray-500 w-32")
                        ui.label(f"{days} gg").classes(
                            "text-xs font-mono text-gray-400 w-16"
                        )
                        ui.label(ending or "-").classes(
                            "text-xs text-yellow-400 flex-1"
                        )
                        ui.label(status or "-").classes("text-xs text-gray-500")
            ui.html("<br>")

        with ui.row().classes("w-full justify-center mt-4 mb-12"):
            ui.button(
                "Gioca una partita", icon="play_arrow", on_click=_play_again
            ).props("color=positive")


# ── Startup ──

ui.add_head_html("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --theme-accent: #6366f1;
        --theme-header: #4f46e5;
        --theme-glow: 0 0 25px rgba(99,102,241,0.2);
    }

    * { font-family: 'Inter', system-ui, sans-serif; }
    .font-mono, code, pre { font-family: 'JetBrains Mono', monospace !important; }
    .q-icon, .material-icons { font-family: 'Material Icons' !important; }

    body {
        background: #0a0a0f;
        color: #e2e8f0;
        min-height: 100vh;
        overflow-x: hidden;
        position: relative;
    }

    body::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0.03;
        pointer-events: none;
        z-index: 1000;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    }

    .bg-animation {
        position: fixed; inset: 0; z-index: -1;
        background:
            linear-gradient(rgba(10, 10, 15, 0.9), rgba(10, 10, 15, 0.95)),
            radial-gradient(circle at 50% -20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 0% 100%, rgba(239, 68, 68, 0.05) 0%, transparent 40%);
    }

    /* Glassmorphism Cards */
    .vn-card {
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        background: #12121a;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .vn-card-highlight {
        border-top: 2px solid var(--theme-accent);
        box-shadow: var(--theme-glow);
    }

    .scan-lines {
        position: fixed;
        inset: 0;
        z-index: 1001;
        pointer-events: none;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        background-size: 100% 4px, 3px 100%;
        opacity: 0.1;
    }

    /* Event Card - Visual Novel Style */
    .event-card {
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        background: linear-gradient(165deg, rgba(20,20,45,0.9) 0%, rgba(10,10,25,0.95) 100%);
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
        position: relative;
        overflow: hidden;
    }

    .event-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    }

    .narrative-text {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #cbd5e1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    /* NPC Portraits */
    .npc-portrait {
        border-radius: 20px;
        border: 2px solid rgba(255,255,255,0.15);
        background: rgba(255,255,255,0.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    .npc-portrait:hover {
        transform: translateY(-2px);
        border-color: var(--theme-accent);
    }
    .npc-portrait img { width: 80px; height: 80px; object-fit: cover; }
    .npc-avatar img { width: 40px; height: 40px; object-fit: cover; border-radius: 10px; }

    /* Choice Buttons */
    .choice-btn {
        text-transform: none;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(30, 30, 60, 0.5) !important;
        backdrop-filter: blur(4px);
        border-radius: 12px !important;
        padding: 16px 20px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    .choice-btn:hover {
        background: rgba(59, 130, 246, 0.15) !important;
        border-color: var(--theme-accent) !important;
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(59,130,246,0.15);
    }

    .effect-chip {
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        background: rgba(0,0,0,0.3);
    }
    .effect-chip.pos { color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
    .effect-chip.neg { color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

    /* Sidebar Stats */
    .stats-sidebar-card {
        background: rgba(10, 10, 25, 0.5);
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeIn 0.5s ease forwards; }

    .pulse-danger {
        animation: pulse-red 2s infinite;
        border-color: rgba(239, 68, 68, 0.5) !important;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

    /* Mobile Bottom Bar */
    .mobile-bottom-bar {
        position: fixed; bottom: 0; left: 0; right: 0;
        z-index: 200;
        background: rgba(10, 10, 30, 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-top: 1px solid rgba(255,255,255,0.08);
        padding: 8px 16px;
        display: flex;
    }

    /* Mobile layout: extra bottom padding to avoid overlap with bottom bar */
    .mobile-layout main, .mobile-layout .q-page {
        padding-bottom: 60px;
    }

    /* Choice buttons stack full-width on mobile */
    @media (max-width: 640px) {
        .choice-btn { width: 100% !important; }
        .npc-portrait img { width: 56px !important; height: 56px !important; }
        .vn-card { padding: 1rem !important; }
    }

    /* Responsive fixes */
    @media (max-width: 1024px) {
        .stats-sidebar {
            position: fixed;
            left: -320px;
            top: 0; bottom: 0;
            width: 300px;
            z-index: 100;
            transition: left 0.3s ease;
            overflow-y: auto;
            background: #0f0f2d !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        .stats-sidebar.open { left: 0; }
    }

    /* Tutorial & Overlays */
    .tutorial-overlay {
        position: fixed; inset: 0; z-index: 9999;
        background: rgba(0,0,0,0.85);
        backdrop-filter: blur(8px);
        display: flex; align-items: center; justify-content: center;
    }
    .tutorial-card {
        max-width: 480px;
        width: 90%;
    }

    .timer-ring {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 12px; color: #fbbf24; font-weight: 800;
        background: rgba(0,0,0,0.3);
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(251,191,36,0.3);
    }
</style>
<div class="bg-animation"></div>
<div class="scan-lines"></div>
""")

init_db()
init_agent_db()

# Serve immagini dalla cartella graphics
if os.path.isdir(GRAPHICS_DIR):
    app.add_static_files(GFX_PATH, GRAPHICS_DIR)

ui.column().classes("w-full max-w-5xl mx-auto p-4 gap-4")
page()

ui.run(title="Burnout Simulator", dark=True, favicon="\U0001f3e2")
