from nicegui import ui
import json
from ui.theme import AGENT_PROFILE_COLORS, CAT_COLORS
from database.agent_db import get_swarm_history
from ui.components.common import metric_card, mini_stat, state_icon
import game.state as state
from ui.pages.logic import (
    toggle_auto_simulation,
    step_simulation,
    inspect_agent,
    continue_possession,
    start_possession,
)


def render_laboratory():
    """Vista principale del laboratorio di agenti migliorata (v3.0)."""
    client_id = ui.context.client.id
    inspected_agent_id = state.client_inspected_agent.get(client_id)

    lab_view = state.swarm.get_laboratory_view(state.current_human_id)
    stats = lab_view["analytics"]

    # Dati per grafico dinamico profili
    history = get_swarm_history(state.swarm.session_id)

    # Se non c'è un agente ispezionato, scegliamo il primo della lista (spesso quello posseduto)
    if not inspected_agent_id and lab_view["agents"]:
        inspected_agent_id = lab_view["agents"][0]["agent_id"]
        state.client_inspected_agent[client_id] = inspected_agent_id

    # Cerchiamo i dati dell'agente ispezionato
    inspected_agent = next(
        (a for a in lab_view["agents"] if a["agent_id"] == inspected_agent_id), None
    )
    if not inspected_agent and lab_view["agents"]:
        inspected_agent = lab_view["agents"][0]
        inspected_agent_id = inspected_agent["agent_id"]

    with ui.column().classes("w-full max-w-[1600px] mx-auto p-4 gap-4 min-h-screen"):
        # --- HEADER: Emotional Weather + Swarm Stats ---
        with (
            ui.row()
            .classes(
                "w-full items-center justify-between p-4 vn-card vn-card-highlight"
            )
            .style("background: rgba(10,10,20,0.8)")
        ):
            with ui.row().classes("items-center gap-6"):
                # Emotional Weather
                avg_stress = stats.get("avg_stress", 0)
                if avg_stress < 40:
                    weather_icon, weather_label, weather_color = (
                        "sunny",
                        "SOLEGGIATO",
                        "text-green-400",
                    )
                elif avg_stress < 60:
                    weather_icon, weather_label, weather_color = (
                        "cloud",
                        "NUVOLOSO",
                        "text-gray-400",
                    )
                elif avg_stress < 75:
                    weather_icon, weather_label, weather_color = (
                        "thunderstorm",
                        "TEMPORALE",
                        "text-yellow-400",
                    )
                else:
                    weather_icon, weather_label, weather_color = (
                        "bolt",
                        "TEMPESTA",
                        "text-red-500",
                    )

                if stats.get("alive_count", 0) < stats.get("total_agents", 0):
                    weather_icon, weather_label, weather_color = (
                        "skull",
                        "COLLASSO",
                        "text-red-900",
                    )

                with ui.column().classes("items-center gap-0"):
                    ui.icon(weather_icon, size="32px").classes(weather_color)
                    ui.label(weather_label).classes(
                        f"text-[10px] font-black {weather_color} tracking-tighter"
                    )

                ui.separator().props("vertical").classes("bg-white/10 h-10")

                # Global Stats
                with ui.column().classes("gap-0"):
                    ui.label("STRESS MEDIO SCIAME").classes(
                        "text-[10px] text-gray-500 font-bold"
                    )
                    ui.label(f"{avg_stress}%").classes("text-2xl font-black text-white")

                with ui.column().classes("gap-0"):
                    ui.label("SOGGETTI ATTIVI").classes(
                        "text-[10px] text-gray-500 font-bold"
                    )
                    ui.label(
                        f"{stats.get('alive_count', 0)}/{len(state.swarm.agents)}"
                    ).classes("text-2xl font-black text-green-400")

            # Cultural drift indicator (v3.5)
            cultural_info = lab_view.get("cultural_drift", {})
            drift_culture = cultural_info.get("dominant_culture", "")
            if drift_culture:
                drift_colors = {
                    "Startup Caotica": "#f97316",
                    "Corporate Tossica": "#3b82f6",
                    "Azienda Familiare": "#22c55e",
                    "Consulting": "#a855f7",
                }
                drift_color = drift_colors.get(drift_culture, "#666")
                with ui.column().classes("items-center gap-0"):
                    ui.label("DERIVA CULTURALE").classes(
                        "text-[8px] text-gray-600 font-bold"
                    )
                    ui.label(drift_culture.upper()).classes(
                        "text-[10px] font-black tracking-wider"
                    ).style(f"color: {drift_color}")

            ui.label("LABORATORIO ANTROPOLOGICO v3.5").classes(
                "text-xl font-black tracking-[0.2em] text-white/20 absolute left-1/2 -translate-x-1/2"
            )

            with ui.row().classes("items-center gap-4"):
                # Auto-play Toggle
                from nicegui import app

                is_auto = getattr(app, "auto_sim_active", False)
                with ui.row().classes(
                    "items-center gap-2 bg-white/5 p-1 px-3 rounded-lg border border-white/10"
                ):
                    ui.label("AUTO").classes("text-[10px] font-bold text-gray-500")
                    ui.switch(value=is_auto, on_change=toggle_auto_simulation).props(
                        "color=green dense size=sm"
                    )

                # Input per numero simulazioni
                with ui.row().classes(
                    "items-center gap-2 bg-white/5 p-1 rounded-lg border border-white/10"
                ):
                    ui.label("SIM:").classes("text-[10px] font-bold text-gray-500 ml-2")
                    sim_count = (
                        ui.number(value=1, min=1, max=100, step=1)
                        .props("dense borderless dark")
                        .classes("w-12 text-xs")
                    )
                    ui.button(
                        icon="play_arrow",
                        on_click=lambda: step_simulation(int(sim_count.value)),
                    ).props("color=green size=sm round").classes("shadow-lg")

                ui.button("10x", on_click=lambda: step_simulation(10)).props(
                    "color=green size=md flat"
                ).classes("font-bold")
                ui.button(
                    "← MENU",
                    on_click=lambda: (
                        setattr(state, "screen", "start") or ui.navigate.to("/")
                    ),
                ).props("flat color=gray").classes("text-xs")

        # --- DYNAMIC PROFILE EVOLUTION (NEW) ---
        if len(history) > 1:
            with ui.card().classes("w-full p-4 vn-card").props("flat"):
                ui.label(
                    "EVOLUZIONE DINAMICA TRATTI PSICOLOGICI (VALORI MEDI SCIAME)"
                ).classes("text-[10px] font-black text-purple-400 tracking-widest mb-4")

                trait_names = [
                    "openness",
                    "conscientiousness",
                    "extraversion",
                    "agreeableness",
                    "neuroticism",
                    "narcissism",
                    "machiavellianism",
                    "psychopathy",
                ]
                trait_labels = [
                    "Apertura",
                    "Coscienziosità",
                    "Estroversione",
                    "Gradevolezza",
                    "Nevroticismo",
                    "Narcisismo",
                    "Machiavellismo",
                    "Psicopatia",
                ]
                series = []

                for i, t_name in enumerate(trait_names):
                    data = []
                    for h in history:
                        avg_stats = json.loads(h["avg_stats_json"])
                        avg_traits = avg_stats.get("avg_traits", {})
                        data.append(round(avg_traits.get(t_name, 50), 1))

                    series.append(
                        {
                            "name": trait_labels[i],
                            "type": "line",
                            "smooth": True,
                            "data": data,
                        }
                    )

                evolution_option = {
                    "tooltip": {"trigger": "axis"},
                    "legend": {
                        "data": trait_labels,
                        "textStyle": {"color": "#999", "fontSize": 10},
                        "top": 0,
                    },
                    "grid": {
                        "left": "3%",
                        "right": "4%",
                        "bottom": "3%",
                        "containLabel": True,
                    },
                    "xAxis": [
                        {
                            "type": "category",
                            "boundaryGap": False,
                            "data": [h["turn_number"] for h in history],
                        }
                    ],
                    "yAxis": [{"type": "value", "min": 0, "max": 100}],
                    "series": series,
                    "backgroundColor": "transparent",
                }
                ui.echart(evolution_option).classes("w-full h-80")

        # --- COLLINS CUBE 3D: Visualizzazione Sciame (v3.5) ---
        if lab_view["agents"]:
            with ui.card().classes("w-full p-4 vn-card").props("flat"):
                ui.label("CUBO DI COLLINS 3D (STRESS · ENERGIA · INTEGRITÀ)").classes(
                    "text-[10px] font-black text-cyan-400 tracking-widest mb-4"
                )
                cube_data = []
                for a in lab_view["agents"]:
                    cube_data.append(
                        {
                            "name": a["name"][:12],
                            "value": [a["stress"], a["energy"], a["integrity"]],
                            "profile": a["profile_name"],
                            "alive": a["alive"],
                            "possessed": a["is_possessed"],
                        }
                    )

                # Mappa profili a colori
                profile_color_map = {
                    "Il Performante": "#f97316",
                    "Il Protettore": "#ef4444",
                    "Il Sopravvissuto": "#22c55e",
                    "Il Negoziatore": "#eab308",
                    "Il Cinico": "#64748b",
                    "Il Manipolatore": "#ec4899",
                    "L'Idealista": "#3b82f6",
                }

                series_data = []
                for pt in cube_data:
                    series_data.append(
                        {
                            "name": pt["name"],
                            "value": pt["value"],
                            "itemStyle": {
                                "color": profile_color_map.get(
                                    pt["profile"], "#ffffff"
                                ),
                                "opacity": 0.7 if pt["alive"] else 0.2,
                            },
                            "symbolSize": 16 if pt["possessed"] else 12,
                            "symbol": "diamond" if pt["possessed"] else "circle",
                        }
                    )

                cube_option = {
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{b}<br/>Stress: {c0}<br/>Energia: {c1}<br/>Integrità: {c2}",
                    },
                    "grid3D": {
                        "boxWidth": 120,
                        "boxHeight": 120,
                        "boxDepth": 120,
                        "viewControl": {
                            "distance": 280,
                            "autoRotate": True,
                            "autoRotateSpeed": 5,
                        },
                        "axisPointer": {"show": False},
                    },
                    "xAxis3D": {
                        "type": "value",
                        "name": "STRESS",
                        "nameTextStyle": {"color": "#ef4444", "fontSize": 10},
                        "axisLabel": {"color": "#666", "fontSize": 8},
                        "min": 0,
                        "max": 100,
                    },
                    "yAxis3D": {
                        "type": "value",
                        "name": "ENERGIA",
                        "nameTextStyle": {"color": "#22c55e", "fontSize": 10},
                        "axisLabel": {"color": "#666", "fontSize": 8},
                        "min": 0,
                        "max": 100,
                    },
                    "zAxis3D": {
                        "type": "value",
                        "name": "INTEGRITÀ",
                        "nameTextStyle": {"color": "#a78bfa", "fontSize": 10},
                        "axisLabel": {"color": "#666", "fontSize": 8},
                        "min": 0,
                        "max": 100,
                    },
                    "series": [
                        {
                            "type": "scatter3D",
                            "data": [p["value"] for p in cube_data],
                            "itemStyle": {
                                "opacity": 0.8,
                            },
                            "symbolSize": 14,
                            "encode": {"x": 0, "y": 1, "z": 2},
                        }
                    ],
                    "backgroundColor": "transparent",
                }
                ui.echart(cube_option).classes("w-full h-96")

        # --- HR DSS INSIGHTS (NEW) ---
        if stats.get("profile_impact"):
            with ui.row().classes("w-full gap-4 items-stretch"):
                with ui.card().classes("flex-1 p-4 vn-card").props("flat"):
                    ui.label("IMPATTO CULTURALE PER PROFILO (DSS)").classes(
                        "text-[10px] font-black text-blue-400 tracking-widest mb-4"
                    )
                    with ui.row().classes("w-full gap-4"):
                        for p_name, p_data in stats["profile_impact"].items():
                            with ui.column().classes(
                                "flex-1 p-3 bg-white/5 rounded-lg border border-white/10"
                            ):
                                ui.label(p_name.upper()).classes(
                                    "text-[10px] font-black text-gray-300 truncate"
                                )
                                with ui.row().classes(
                                    "w-full justify-between items-end mt-2"
                                ):
                                    with ui.column().classes("gap-0"):
                                        ui.label("Stress").classes(
                                            "text-[8px] text-gray-500"
                                        )
                                        ui.label(f"{p_data['avg_stress']}%").classes(
                                            "text-sm font-bold text-red-400"
                                        )
                                    with ui.column().classes("gap-0"):
                                        ui.label("Sopravvivenza").classes(
                                            "text-[8px] text-gray-500"
                                        )
                                        ui.label(f"{p_data['avg_days']}gg").classes(
                                            "text-sm font-bold text-green-400"
                                        )
                                    with ui.column().classes("gap-0"):
                                        ui.label("Tasso").classes(
                                            "text-[8px] text-gray-500"
                                        )
                                        ui.label(f"{p_data['survival_rate']}%").classes(
                                            "text-sm font-bold text-blue-400"
                                        )

        # --- MAIN 3-ZONE LAYOUT ---
        with ui.row().classes("w-full gap-4 items-start no-wrap"):
            # COLONNA SX: Agent Compact List
            with ui.column().classes("w-80 shrink-0 gap-3"):
                ui.label("SOGGETTI").classes(
                    "text-xs font-black text-gray-500 tracking-widest ml-1"
                )
                for agent_data in lab_view["agents"]:
                    is_selected = agent_data["agent_id"] == inspected_agent_id
                    render_agent_compact_card(agent_data, is_selected)

            # AREA CENTRALE: Agent Focus
            with ui.column().classes("flex-1 gap-4"):
                if inspected_agent:
                    # Focus Header
                    with (
                        ui.card()
                        .classes("w-full p-6 vn-card vn-card-highlight")
                        .props("flat")
                    ):
                        with ui.row().classes("w-full items-start justify-between"):
                            with ui.column().classes("gap-0"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label(inspected_agent["name"]).classes(
                                        "text-3xl font-black text-white tracking-tighter"
                                    )
                                    if inspected_agent["is_possessed"]:
                                        ui.badge("POSSEDUTO", color="purple").classes(
                                            "px-2 font-black text-[10px]"
                                        )
                                ui.label(
                                    f"{inspected_agent['profile_name']} · {inspected_agent['company_type']} · GIORNO {inspected_agent['day']}"
                                ).classes("text-sm text-blue-400 font-bold")

                            with ui.row().classes("gap-2"):
                                if inspected_agent["is_possessed"]:
                                    ui.button(
                                        "CONTINUA",
                                        on_click=lambda aid=inspected_agent[
                                            "agent_id"
                                        ]: continue_possession(aid),
                                    ).props("color=purple icon=bolt").classes(
                                        "font-bold"
                                    )
                                else:
                                    ui.button(
                                        "POSSIEDI",
                                        on_click=lambda aid=inspected_agent[
                                            "agent_id"
                                        ]: start_possession(aid),
                                    ).props("color=blue icon=psychology").classes(
                                        "font-bold"
                                    )

                        # Aura Radar Area
                        with ui.row().classes("w-full gap-6 mt-6"):
                            # Radar chart
                            with ui.column().classes("flex-1 items-center"):
                                ui.label("AURA COMPORTAMENTALE").classes(
                                    "text-[10px] font-black text-gray-500 tracking-widest mb-4"
                                )
                                render_aura_radar(inspected_agent)

                            # Event Showcase
                            with ui.column().classes("w-96 gap-4"):
                                # Report Strategico (NEW)
                                if (
                                    "strategic_report" in inspected_agent
                                    and "discursive_comment"
                                    in inspected_agent["strategic_report"]
                                ):
                                    ui.label("ANALISI STRATEGICA POSTERIORI").classes(
                                        "text-[10px] font-black text-purple-400 tracking-widest mb-0"
                                    )
                                    with (
                                        ui.card()
                                        .classes(
                                            "w-full p-4 vn-card border-l-4 border-purple-500"
                                        )
                                        .style("background: rgba(120,50,255,0.05)")
                                    ):
                                        rep = inspected_agent["strategic_report"]
                                        ui.label(rep["strategy_name"].upper()).classes(
                                            "text-xs font-black text-purple-300 mb-2"
                                        )
                                        ui.markdown(rep["discursive_comment"]).classes(
                                            "text-xs text-gray-300 leading-relaxed italic"
                                        )

                                ui.label("EVENTO CORRENTE").classes(
                                    "text-[10px] font-black text-gray-500 tracking-widest mb-0"
                                )
                                with (
                                    ui.card()
                                    .classes("w-full p-4 vn-card")
                                    .style("background: rgba(0,0,0,0.3)")
                                ):
                                    ui.label(
                                        inspected_agent["current_event"]
                                        .replace("_", " ")
                                        .upper()
                                        if inspected_agent["current_event"]
                                        else "NESSUN EVENTO"
                                    ).classes("text-xs font-black text-orange-400 mb-2")
                                    ui.markdown(
                                        inspected_agent["current_event_text"]
                                    ).classes(
                                        "text-sm text-gray-300 italic line-clamp-3"
                                    )

                                ui.label("SCELTE & PROBABILITÀ").classes(
                                    "text-[10px] font-black text-gray-500 tracking-widest mt-2"
                                )
                                with ui.column().classes("w-full gap-2"):
                                    for choice in inspected_agent["current_choices"]:
                                        prob = choice.get("probability", 0)
                                        with ui.row().classes(
                                            "w-full items-center justify-between p-2 bg-white/5 rounded border border-white/10"
                                        ):
                                            ui.label(
                                                choice["text"][:40] + "..."
                                            ).classes(
                                                "text-[11px] text-gray-400 truncate flex-1"
                                            )
                                            with ui.row().classes("items-center gap-2"):
                                                ui.label(f"{prob}%").classes(
                                                    "text-[10px] font-black text-gray-500"
                                                )
                                                ui.label(choice["category"]).classes(
                                                    "text-[9px] font-bold px-1 rounded"
                                                ).style(
                                                    f"background: {CAT_COLORS.get(choice['category'], '#666')}40; color: {CAT_COLORS.get(choice['category'], '#666')}"
                                                )

                    # Global Metrics of Inspected Agent
                    with ui.row().classes("w-full gap-4"):
                        metric_card("STRESS", inspected_agent["stress"], "#ef4444")
                        metric_card("ENERGIA", inspected_agent["energy"], "#22c55e")
                        metric_card("SALUTE", inspected_agent["health"], "#22d3ee")
                        metric_card(
                            "AUTOSTIMA", inspected_agent["self_esteem"], "#eab308"
                        )

            # COLONNA DX: Decision Timeline
            with ui.column().classes("w-80 shrink-0 gap-3"):
                ui.label("CRONOLOGIA SCELTE").classes(
                    "text-xs font-black text-gray-500 tracking-widest ml-1"
                )
                with ui.column().classes(
                    "w-full gap-1 overflow-y-auto max-h-[80vh] pr-2"
                ):
                    if inspected_agent and inspected_agent["recent_decisions"]:
                        for dec in inspected_agent["recent_decisions"]:
                            render_timeline_item(dec)
                    else:
                        ui.label("Nessuna decisione registrata").classes(
                            "text-xs text-gray-600 italic mt-4 text-center w-full"
                        )


def render_agent_compact_card(agent, is_selected):
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

    card_bg = (
        "background: rgba(30,30,50,0.6)"
        if is_selected
        else "background: rgba(15,15,30,0.4)"
    )

    with (
        ui.card()
        .classes(f"w-full p-3 vn-card cursor-pointer {border_class}")
        .style(card_bg)
        .on("click", lambda _, aid=agent["agent_id"]: inspect_agent(aid))
    ):
        with ui.row().classes("w-full items-center justify-between no-wrap"):
            with ui.row().classes("items-center gap-2 flex-1 min-w-0"):
                ui.icon(status_icon, size="14px").classes(status_color)
                ui.label(agent["name"]).classes("text-sm font-bold text-white truncate")
            ui.label(f"G{agent['day']}").classes("text-[10px] font-mono text-gray-500")

        # Stress bar
        with ui.row().classes("w-full items-center gap-2 mt-1"):
            ui.linear_progress(
                agent["stress"] / 100,
                size="2px",
                color="red"
                if agent["stress"] > 75
                else "orange"
                if agent["stress"] > 50
                else "blue",
            ).classes("flex-1 bg-white/5")
            ui.label(f"{agent['stress']}%").classes(
                "text-[9px] font-mono text-gray-500"
            )

        with ui.row().classes("w-full items-center justify-between mt-1"):
            ui.label(agent["profile_name"].upper()).classes(
                "text-[9px] font-black text-gray-600"
            )
            ui.label(agent["dominant_faction"]).classes(
                "text-[9px] font-bold text-gray-500"
            )


def render_aura_radar(agent):
    # Cerchiamo l'agente reale nello sciame per accedere al profilo psicometrico
    real_agent = state.swarm.agents.get(agent["agent_id"])
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
            "title": {
                "text": "BIG FIVE",
                "left": "center",
                "textStyle": {"color": "#555", "fontSize": 10},
            },
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
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}},
            },
            "series": [
                {
                    "type": "radar",
                    "data": [
                        {
                            "value": [a["value"] for a in ocean_axes],
                            "areaStyle": {"color": profile_color, "opacity": 0.4},
                        }
                    ],
                    "symbol": "none",
                    "lineStyle": {"width": 2, "color": profile_color},
                }
            ],
            "backgroundColor": "transparent",
        }
        ui.echart(ocean_option).classes("w-1/2 h-64")

        # DARK TRIAD Radar
        dark_option = {
            "title": {
                "text": "TRIADE OSCURA",
                "left": "center",
                "textStyle": {"color": "#555", "fontSize": 10},
            },
            "radar": {
                "indicator": [
                    {"name": "Narcissism", "max": 100},
                    {"name": "Machiavellianism", "max": 100},
                    {"name": "Psychopathy", "max": 100},
                ],
                "shape": "polygon",
                "axisName": {"color": "#777", "fontSize": 8},
                "splitArea": {"show": False},
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}},
            },
            "series": [
                {
                    "type": "radar",
                    "data": [
                        {
                            "value": [a["value"] for a in dark_axes],
                            "areaStyle": {"color": "#ef4444", "opacity": 0.4},
                        }
                    ],
                    "symbol": "none",
                    "lineStyle": {"width": 2, "color": "#ef4444"},
                }
            ],
            "backgroundColor": "transparent",
        }
        ui.echart(dark_option).classes("w-1/2 h-64")


def render_timeline_item(dec):
    cat_col = CAT_COLORS.get(dec["category"], "#666")
    is_auto = dec["was_auto"]

    with (
        ui.row()
        .classes("w-full items-start gap-3 p-2 bg-white/5 rounded border-l-2 mb-1")
        .style(f"border-color: {cat_col}")
    ):
        with ui.column().classes("gap-0 flex-1"):
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(dec["category"]).classes("text-[9px] font-black").style(
                    f"color: {cat_col}"
                )
                ui.label(f"G{dec['day']}").classes("text-[9px] text-gray-600 font-mono")

            ui.label(dec["choice_text"]).classes(
                "text-xs text-gray-300 leading-tight mt-1"
            )

            with ui.row().classes("w-full justify-between items-center mt-2"):
                # Impact indicator
                delta = dec.get("stress_delta", 0)
                if delta != 0:
                    delta_col = "text-red-400" if delta > 0 else "text-green-400"
                    delta_sign = "+" if delta > 0 else ""
                    ui.label(f"STRESS {delta_sign}{delta}").classes(
                        f"text-[9px] font-bold {delta_col}"
                    )
                else:
                    ui.element("div")  # spacer

                ui.icon("smart_toy" if is_auto else "person", size="12px").classes(
                    "text-gray-600"
                )
