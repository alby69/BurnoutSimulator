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
from ui.theme import NPC_FACTION_COLORS, ARCHETYPE_THEMES, AGENT_PROFILE_COLORS, CAT_COLORS, BARS_DEF
from ui.components.common import effect_label, npc_portrait, event_icon, state_icon, metric_card, mini_stat, show_agent_details
from ui.components.sidebar import render_stats_section, render_factions_section, render_relationships_section
from ui.pages.start_page import render_start
from ui.pages.laboratory_page import render_laboratory
from ui.pages.game_page import render_game, render_tutorial
from ui.pages.game_over_page import render_game_over
from ui.pages.analytics_page import render_analytics
from ui.pages.logic import *
from ui.pages.main_page import page
from ui.assets import GFX_PATH, EMOTE_ICONS
from game.logic import determine_ending
from game.events import Choice
from agents.swarm import AgentSwarm
from engine.analysis import StrategicAnalyzer
import game.state as state

# ── Startup ──

init_db()
init_agent_db()

# Serve immagini dalla cartella graphics
GRAPHICS_DIR = "static/images"
if os.path.isdir(GRAPHICS_DIR):
    app.add_static_files(GFX_PATH, GRAPHICS_DIR)

from ui.theme import global_style

@ui.page("/")
def main_page_route():
    global_style()
    ui.column().classes("w-full max-w-5xl mx-auto p-4 gap-4")
    page(state.screen, render_start, render_laboratory, render_game, render_tutorial, render_game_over, render_analytics, on_start_cb, show_help, show_config, go_analytics, state._tutorial_active)

from ui.pages.editor_page import render_editor
@ui.page("/editor")
def editor_page_route():
    global_style()
    render_editor()

ui.run(title="Burnout Simulator", dark=True, favicon="\U0001f3e2", port=8080)
