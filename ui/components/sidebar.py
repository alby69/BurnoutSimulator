from nicegui import ui
from ui.theme import BARS_DEF, NPC_FACTION_COLORS
from game.engine import NPC_FACTION_MAP
from ui.components.common import npc_portrait, effect_label, event_icon, state_icon

def render_stats_section(stats: dict):
    with ui.column().classes("w-full gap-3 mt-2"):
        for label, key, color in BARS_DEF:
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


def render_factions_section(factions: dict):
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


def render_relationships_section(npcs: dict):
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
            portrait_url = npc_portrait(nname, ndata)
            ui.image(portrait_url).style(
                f"border-color: {avi_color}; width: 40px; height: 40px; border-radius: 10px; border: 2px solid"
            ).classes("npc-avatar")
            with ui.column().classes("gap-0 flex-1"):
                ui.label(nname).classes("text-xs text-gray-300")
                ui.label(
                    f"Fiducia {trust}%  Rispetto {ndata['respect']}%  Paura {ndata['fear']}%"
                ).style(f"color: {trust_color}").classes("text-[10px]")
