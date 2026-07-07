from nicegui import ui
import base64, io, json
from ui.theme import CAT_COLORS, ARCHETYPE_THEMES
from engine.analysis import StrategicAnalyzer
from ui.components.common import state_icon
from game.logic import determine_ending
import game.state as state
from ui.pages.logic import (
    get_stats_dict,
    end_session_logic,
    record_tags_logic,
    play_again,
    export_report,
    show_decision_graph,
    go_analytics
)

def render_game_over():
    engine = state.engine
    swarm = state.swarm
    session_id = state.session_id
    current_agent_id = state.current_agent_id

    player = engine.player
    ending = determine_ending(player)

    # Meta-progression: record ending
    try:
        from database.analytics import get_meta_value, set_meta_value
        unlocked_json = get_meta_value("unlocked_endings", "[]")
        unlocked = json.loads(unlocked_json)
        if ending not in unlocked:
            unlocked.append(ending)
            set_meta_value("unlocked_endings", json.dumps(unlocked))
    except Exception as e:
        print(f"Error saving meta-progression: {e}")

    # Identifica se l'agente si è comportato bene rispetto al suo profilo
    is_top_performer = False
    avg_days = 0
    agent = None
    if current_agent_id and current_agent_id in swarm.agents:
        agent = swarm.agents[current_agent_id]
        # Un top performer è chi sopravvive più della media del suo profilo o ha stress basso
        analytics = swarm.get_swarm_analytics()
        profile_stats = analytics.get("profile_impact", {}).get(agent.profile.name, {})
        avg_days = profile_stats.get("avg_days", 0)
        if player.days_survived > avg_days * 1.2 or (player.is_alive and player.stress < 40):
            is_top_performer = True

    end_session_logic(session_id, player.days_survived, player.status, ending)
    record_tags_logic(session_id, player.tags)
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
                state_img = state_icon(player.status)
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

            with ui.row().classes("w-full justify-center mt-6 mb-12 gap-3 flex-wrap"):
                for key, label, color in [
                    ("energy", "Energia", "#4ade80"),
                    ("stress", "Stress", "#f87171"),
                    ("health", "Salute", "#22d3ee"),
                    ("integrity", "Integrità", "#a78bfa"),
                    ("self_esteem", "Autostima", "#fbbf24"),
                    ("employability", "Occupabilità", "#34d399"),
                ]:
                    with ui.column().classes("items-center p-2 bg-white/5 rounded-lg border border-white/5 min-w-[100px]"):
                        ui.circular_progress(
                            value=stats[key] / 100,
                            size="40px",
                            color=color,
                            show_value=False,
                        ).classes("mb-2")
                        ui.label(label).classes("text-[10px] text-gray-500 uppercase")
                        ui.label(f"{stats[key]}%").classes("text-sm font-bold")

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
                                    with ui.row().classes('w-full p-2 bg-white/5 rounded border-l-2 items-start').style(f"border-color: {CAT_COLORS.get(cat, '#666')}"):
                                        with ui.column().classes('flex-1 gap-1'):
                                            ui.label(f"GIORNO {d.day}").classes('text-[9px] font-black text-gray-500')
                                            # Cerchiamo il testo dell'evento
                                            ev = engine.event_manager.get_event(d.event_id)
                                            if ev:
                                                ui.label(ev.text[:100] + "...").classes('text-xs italic text-gray-400')
                                            ui.label(d.choice_text).classes('text-sm text-white font-bold')

        if is_top_performer and agent:
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
            ui.button("Gioca Ancora", icon="replay", on_click=play_again).props(
                "color=positive size=lg"
            )
            ui.button(
                "📷 Esporta Report", icon="download", on_click=export_report
            ).props("flat size=lg").classes("text-gray-400")
            ui.button(
                "🕸 Grafo Decisionale", icon="hub", on_click=show_decision_graph
            ).props("flat size=lg").classes("text-gray-400")
