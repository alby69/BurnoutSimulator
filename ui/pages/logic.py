from typing import Optional, Dict, List, Any
from nicegui import ui, app
import uuid
import random
import os
import sqlite3
import base64
import io
from database.analytics import record_choice, end_session, record_tags, create_session
from database.agent_db import save_agent
from game.logic import determine_ending
from game.engine import GameEngine, NPC_FACTION_MAP
from ui.theme import BARS_DEF, NPC_FACTION_COLORS, CAT_COLORS, ARCHETYPE_THEMES
import game.state as state


def on_start_cb(name, arch, hr_params, go_to_lab=False, skip_tutorial=False):
    if go_to_lab:
        state.swarm.set_hr_parameters(arch, hr_params)
        if not state.current_human_id:
            human = state.swarm.register_human("HR_Manager")
            state.current_human_id = human.human_id
        state.screen = "laboratory"
        ui.navigate.to("/")
    else:
        # Check if we need to show PRE questionnaire
        if state.screen == "start":
            state.temp_start_data = (name, arch, hr_params, skip_tutorial)
            state.screen = "questionnaire_pre"
            ui.navigate.to("/")
            return

        # If we are here, questionnaire is done or skipped
        if hasattr(state, "temp_start_data"):
            name, arch, hr_params, skip_tutorial = state.temp_start_data
            del state.temp_start_data

        state.engine = GameEngine(
            name, "game/data/events.json", company_type=arch, hr_params=hr_params
        )
        state.session_id = str(uuid.uuid4())
        create_session(state.session_id, name, arch)

        # Record variants for this session
        from database.analytics import record_variants
        record_variants(state.session_id, state.engine.session_variants)

        state.screen = "game"
        if not skip_tutorial:
            state._tutorial_active = True
        ui.navigate.to("/")


def get_stats_dict(eng) -> dict:
    return eng.player.to_dict()["stats"]


def inspect_agent(agent_id):
    client_id = ui.context.client.id
    state.client_inspected_agent[client_id] = agent_id
    ui.navigate.to("/")


def start_possession(agent_id: str):
    if not state.current_human_id:
        ui.notify("Nessun umano registrato.", type="warning")
        return
    result = state.swarm.possess_agent(state.current_human_id, agent_id)
    if result.get("success"):
        state.current_agent_id = agent_id
        agent = state.swarm.agents[agent_id]
        state.engine = agent.engine
        state.session_id = f"possession_{agent_id}_{uuid.uuid4().hex[:6]}"
        create_session(state.session_id, f"HR_Lab_{agent.name}", agent.company_type)
        state.screen = "game"
        ui.navigate.to("/")
    else:
        ui.notify(result.get("error", "Errore"), type="negative")


def continue_possession(agent_id: str):
    if agent_id not in state.swarm.agents:
        return
    state.current_agent_id = agent_id
    state.engine = state.swarm.agents[agent_id].engine
    state.session_id = f"possession_{agent_id}_{uuid.uuid4().hex[:6]}"
    agent = state.swarm.agents[agent_id]
    create_session(state.session_id, f"HR_Lab_{agent.name}", agent.company_type)
    state.screen = "game"
    ui.navigate.to("/")


def go_to_laboratory():
    state.current_agent_id = None
    if not state.current_human_id:
        human = state.swarm.register_human("Osservatore")
        state.current_human_id = human.human_id
    state.screen = "laboratory"
    ui.navigate.to("/")


def tutorial_next():
    if state._tutorial_step >= 4:
        state._tutorial_active = False
    else:
        state._tutorial_step += 1
    ui.navigate.to("/")


def tutorial_prev():
    if state._tutorial_step > 0:
        state._tutorial_step -= 1
    ui.navigate.to("/")


def make_choice(idx: int, event, choice):
    state.stats_before = get_stats_dict(state.engine)
    if state.current_agent_id and state.current_human_id:
        state.swarm.human_make_choice(state.current_human_id, idx)
    else:
        state.engine.handle_choice(idx)
    stats_after = get_stats_dict(state.engine)
    record_choice(
        state.session_id,
        state.engine.player.days_survived,
        event.id,
        choice.id,
        choice.text,
        choice.category,
        state.stats_before,
        stats_after,
    )
    state.choice_history.append({"text": choice.text, "category": choice.category})
    deltas = {
        k: stats_after[k] - state.stats_before[k]
        for k in state.stats_before
        if stats_after[k] != state.stats_before[k]
    }
    show_choice_feedback(deltas, choice.category, choice.text, getattr(choice, "reflection", None))


def show_choice_feedback(deltas, category, choice_text="", reflection_text=None):
    from ui.pages.game_page import render_reflection_dialog

    # Micro-animation for high stress
    if deltas.get("stress", 0) > 5:
        ui.run_javascript("document.body.classList.add('shake'); setTimeout(() => document.body.classList.remove('shake'), 500);")

    with (
        ui.dialog().props("persistent scale") as dialog,
        ui.card().classes("p-8 vn-card"),
    ):
        ui.label("CONSEGUENZE").classes(
            "text-[10px] font-black text-blue-400 tracking-[0.3em] mb-1"
        )
        ui.label(category.upper()).classes("text-xl font-bold mb-6")
        for key, delta in deltas.items():
            with ui.row().classes(
                "w-full items-center justify-between px-4 py-3 rounded-xl border border-white/5"
            ):
                ui.label(key.upper()).classes(
                    "text-[10px] font-extrabold text-gray-300"
                )
                ui.label(f"{'+' if delta > 0 else ''}{delta}").classes(
                    "text-sm font-black"
                )

        def advance():
            dialog.close()
            if state.engine and state.engine.is_game_over():
                state.screen = "game_over"
            else:
                if state.engine:
                    state.engine.next_turn()
                state.screen = (
                    "game_over"
                    if state.engine and state.engine.is_game_over()
                    else "game"
                )
                if state.current_agent_id:
                    save_agent(state.swarm.agents[state.current_agent_id].to_dict())
            ui.navigate.to("/")

        with ui.row().classes("w-full gap-2 mt-4"):
            ui.button("PROSEGUI", on_click=advance).classes("flex-1")
            ui.button(icon="lightbulb", on_click=lambda: render_reflection_dialog(deltas, category, choice_text, reflection_text)).props("flat color=amber").tooltip("Perché questo effetto? (Riflessione)")

    dialog.open()


def exit_game():
    state.screen = "game_over"
    ui.navigate.to("/")


def play_again():
    state.screen = "start"
    state.engine = None
    state.current_agent_id = None
    ui.navigate.to("/")


def go_analytics():
    state.screen = "analytics"
    ui.navigate.to("/")


def end_session_logic(sid, days, status, ending):
    end_session(sid, days, status, ending)


def record_tags_logic(sid, tags):
    record_tags(sid, tags)


def step_simulation(steps=1):
    for _ in range(steps):
        state.swarm.run_simulation_step()
    ui.navigate.to("/")


def toggle_auto_simulation():
    if not hasattr(app, "auto_sim_active"):
        app.auto_sim_active = False
    app.auto_sim_active = not app.auto_sim_active
    if app.auto_sim_active:
        if not hasattr(app, "auto_sim_timer"):
            app.auto_sim_timer = ui.timer(
                30.0, lambda: (state.swarm.run_simulation_step(), ui.navigate.to("/"))
            )
        else:
            app.auto_sim_timer.activate()
    else:
        if hasattr(app, "auto_sim_timer"):
            app.auto_sim_timer.deactivate()
    ui.navigate.to("/")


def mood_matches_agent(mood: str, agent: dict) -> bool:
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
        return 30 <= stats.get("stress", 50) <= 70
    return True


def render_jump_dialog():
    with ui.dialog().props("maximized") as dialog:
        with ui.card().classes("w-full h-full bg-gray-900 p-8"):
            ui.label("SALTA A UN ALTRO AGENTE").classes(
                "text-2xl font-bold text-white mb-4"
            )
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
                label="Come ti senti?",
            ).classes("w-full max-w-md mb-6")
            agents_container = ui.column().classes("w-full gap-3")

            def render_agents():
                agents_container.clear()
                available = state.swarm.get_available_agents(state.current_human_id)
                for agent in available:
                    if agent["agent_id"] == state.current_agent_id:
                        continue
                    if mood.value and not mood_matches_agent(mood.value, agent):
                        continue
                    with (
                        agents_container,
                        ui.card().classes(
                            "w-full p-4 mb-2 bg-white/5 border border-white/10"
                        ),
                    ):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label(agent["name"]).classes("font-bold")
                            ui.button(
                                "SALTA QUI",
                                on_click=lambda aid=agent["agent_id"],
                                m=mood: execute_jump(aid, m.value, dialog),
                            ).props("color=purple")

            mood.on_change = render_agents
            render_agents()
            ui.button("Annulla", on_click=dialog.close).props("flat").classes("mt-4")
    dialog.open()


def execute_jump(aid, mood_val, dialog):
    res = state.swarm.possess_agent(
        state.current_human_id,
        aid,
        reason=f"Salto emotivo: {mood_val}" if mood_val else None,
    )
    if res.get("success"):
        state.current_agent_id = aid
        state.engine = state.swarm.agents[aid].engine
        state.session_id = f"possession_{aid}_{uuid.uuid4().hex[:6]}"
        dialog.close()
        ui.navigate.to("/")


def show_help():
    with ui.dialog().props("maximized") as d:
        with ui.card().classes(
            "w-full h-full bg-gray-900 text-white p-8 overflow-y-auto"
        ):
            ui.label("STRATEGIC LABORATORY & DSS HELP").classes(
                "text-2xl font-black text-blue-400 mb-6"
            )
            ui.markdown("""
            - **Laboratorio**: Gestisce lo sciame di agenti autonomi.
            - **Parametri HR**: Influenzano lo stress e il comportamento collettivo.
            - **Jump System**: Permette di 'possedere' un agente per analisi qualitativa.
            - **Statistiche**: Energia, Stress, Salute, Integrità, Autostima, Occupabilità.
            - **Strategie**: Compliance (blu), Resistance (rossa), Negotiation (gialla), Escape (verde).
            """)
            ui.button("Chiudi", on_click=d.close).props("flat").classes("mt-4")
    d.open()


def show_config():
    with ui.dialog() as d, ui.card().classes("p-8 vn-card"):
        ui.label("IMPOSTAZIONI").classes("text-xl font-bold mb-4")

        ui.label("ACCESSIBILITÀ").classes("text-xs font-black text-blue-300 mb-2")
        with ui.column().classes("w-full gap-2 mb-4"):
            ui.label("Velocità Lettura:").classes("text-xs text-gray-400")
            rs = ui.slider(min=0, max=0.1, step=0.01, value=state._reading_speed).props("label-always")
            rs.on_change(lambda e: setattr(state, "_reading_speed", e.value))

        ui.label("SALVATAGGI MULTI-SLOT").classes(
            "text-xs font-black text-blue-300 mb-2"
        )
        with ui.row().classes("gap-4 mb-4"):
            for i in range(1, 4):
                with ui.column().classes("items-center"):
                    ui.label(f"Slot {i}").classes("text-xs")
                    ui.button(icon="save", on_click=lambda i=i: save_to_slot(i)).props(
                        "flat round color=blue"
                    )
                    ui.button(
                        icon="upload", on_click=lambda i=i: load_from_slot(i)
                    ).props("flat round color=gray")
        ui.button("Chiudi", on_click=d.close).props("flat")
    d.open()


def show_decision_graph():
    if not state.engine or not state.engine.graph.history:
        ui.notify("Nessun dato disponibile per il grafo", type="warning")
        return
    history = state.engine.graph.history
    nodes_map, edges = {}, []
    for entry in history:
        ev_id, ch_id, nxt = (
            entry["event_id"],
            entry["choice_id"],
            entry.get("next_event_id"),
        )
        if ev_id not in nodes_map:
            nodes_map[ev_id] = {
                "id": ev_id,
                "name": ev_id.replace("_", " ")[:15],
                "symbolSize": 20,
            }
        if nxt:
            if nxt not in nodes_map:
                nodes_map[nxt] = {
                    "id": nxt,
                    "name": nxt.replace("_", " ")[:15],
                    "symbolSize": 15,
                }
            edges.append(
                {"source": ev_id, "target": nxt, "lineStyle": {"curveness": 0.2}}
            )

    option = {
        "series": [
            {
                "type": "graph",
                "layout": "force",
                "data": list(nodes_map.values()),
                "edges": edges,
                "roam": True,
                "label": {"show": True, "position": "bottom", "fontSize": 10},
            }
        ],
        "backgroundColor": "transparent",
    }
    with ui.dialog() as d, ui.card().classes("w-full max-w-4xl p-4 vn-card"):
        ui.echart(option).classes("w-full h-[500px]")
    d.open()


def export_report():
    if not state.engine:
        return
    p = state.engine.player
    ending = determine_ending(p)
    report = "--- BURNOUT SIMULATOR REPORT ---\n"
    report += f"Soggetto: {p.name}\n"
    report += f"Azienda: {p.company_type.value}\n"
    report += f"Giorni Sopravvissuti: {p.days_survived}\n"
    report += f"Stato Finale: {p.status}\n"
    report += f"Finale: {ending}\n\n"
    report += "TAG COMPORTAMENTALI:\n"
    for tag, val in p.tags.items():
        report += f"- {tag}: {val}\n"
    ui.download(report.encode(), f"report_{p.name.replace(' ', '_')}.txt")


def save_to_slot(slot: int):
    if state.engine:
        state.engine.save_game_to_slot(slot)
        ui.notify(f"Salvataggio completato slot {slot}", type="positive")


def load_from_slot(slot: int):
    ui.notify(
        "Caricamento multi-slot non ancora integrato nella UI di ripresa", type="info"
    )
