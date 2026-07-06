from nicegui import ui
from ui.assets import GFX_PATH, NPC_SCARED, NPC_DEFAULT, NPC_ANGRY, NPC_STRESSED, NPC_WORRIED, NPC_HAPPY, EVENT_ICONS, STATE_ICONS, EFFECT_LABELS

def effect_label(key: str) -> str:
    return EFFECT_LABELS.get(key, key.replace("_", " ").title())


def npc_portrait(nname: str, ndata: dict) -> str:
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


def event_icon(event) -> str | None:
    if not hasattr(event, "id") or not event.id:
        return None
    path = EVENT_ICONS.get(event.id)
    if path:
        return f"{GFX_PATH}/eventi/{path}"
    return None


def state_icon(status: str) -> str | None:
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


def metric_card(label, value, color):
    with ui.card().classes("flex-1 p-3 vn-card items-center gap-0").props("flat"):
        ui.label(label).classes("text-[10px] font-black text-gray-500 tracking-tighter")
        ui.label(f"{value}%").classes("text-xl font-black").style(f"color: {color}")
        ui.linear_progress(value/100, size="2px", color=color).classes("w-full mt-2 bg-white/5")


def mini_stat(label: str, value: int, color: str):
    with ui.column().classes("items-center flex-1"):
        ui.circular_progress(value / 100, size="32px", color=color)
        ui.label(label).classes("text-[9px] text-gray-500 mt-1")


def show_agent_details(agent_id: str):
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
                        on_click=lambda: [start_possession(agent_id), dialog.close()],
                    ).classes("w-full py-4 mt-4 bg-blue-600 font-bold")

        dialog.open()
