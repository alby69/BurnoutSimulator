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

def global_style():
    ui.add_head_html("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --theme-accent: #6366f1;
        --theme-header: #4f46e5;
        --theme-glow: 0 0 25px rgba(99,102,241,0.2); }

    * { font-family: 'Inter', system-ui, sans-serif; }
    .font-mono, code, pre { font-family: 'JetBrains Mono', monospace !important; }
    .q-icon, .material-icons { font-family: 'Material Icons' !important; }

    body {
        background: #0a0a0f;
        color: #e2e8f0;
        min-height: 100vh;
        overflow-x: hidden;
        position: relative; }

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
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E"); }

    .bg-animation {
        position: fixed; inset: 0; z-index: -1;
        background:
            linear-gradient(rgba(10, 10, 15, 0.9), rgba(10, 10, 15, 0.95)),
            radial-gradient(circle at 50% -20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 0% 100%, rgba(239, 68, 68, 0.05) 0%, transparent 40%); }

    /* Glassmorphism Cards */
    .vn-card {
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        background: #12121a;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }

    .vn-card-highlight {
        border-top: 2px solid var(--theme-accent);
        box-shadow: var(--theme-glow); }

    .scan-lines {
        position: fixed;
        inset: 0;
        z-index: 1001;
        pointer-events: none;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        background-size: 100% 4px, 3px 100%;
        opacity: 0.1; }

    /* Event Card - Visual Novel Style */
    .event-card {
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        background: linear-gradient(165deg, rgba(20,20,45,0.9) 0%, rgba(10,10,25,0.95) 100%);
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
        position: relative;
        overflow: hidden; }

    .event-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); }

    .narrative-text {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #cbd5e1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3); }

    /* NPC Portraits */
    .npc-portrait {
        border-radius: 20px;
        border: 2px solid rgba(255,255,255,0.15);
        background: rgba(255,255,255,0.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        overflow: hidden; }
    .npc-portrait:hover {
        transform: translateY(-2px);
        border-color: var(--theme-accent); }
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
        justify-content: flex-start !important; }

    .choice-btn:hover {
        background: rgba(59, 130, 246, 0.15) !important;
        border-color: var(--theme-accent) !important;
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(59,130,246,0.15); }

    .effect-chip {
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        background: rgba(0,0,0,0.3); }
    .effect-chip.pos { color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
    .effect-chip.neg { color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

    /* Sidebar Stats */
    .stats-sidebar-card {
        background: rgba(10, 10, 25, 0.5);
        border: 1px solid rgba(255,255,255,0.05); }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); } }
    .fade-in { animation: fadeIn 0.5s ease forwards; }

    .pulse-danger {
        animation: pulse-red 2s infinite;
        border-color: rgba(239, 68, 68, 0.5) !important; }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 4px; }
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
        display: flex; }

    /* Mobile layout: extra bottom padding to avoid overlap with bottom bar */
    .mobile-layout main, .mobile-layout .q-page {
        padding-bottom: 60px; }

    /* Choice buttons stack full-width on mobile */
    @media (max-width: 640px) {
        .choice-btn { width: 100% !important; }
        .npc-portrait img { width: 56px !important; height: 56px !important; }
        .vn-card { padding: 1rem !important; } }

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
            border-right: 1px solid rgba(255,255,255,0.1); }
        .stats-sidebar.open { left: 0; } }

    /* Tutorial & Overlays */
    .tutorial-overlay {
        position: fixed; inset: 0; z-index: 9999;
        background: rgba(0,0,0,0.85);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center; justify-content: center; }
    .tutorial-card {
        max-width: 480px;
        width: 90%; }

    .timer-ring {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 12px; color: #fbbf24; font-weight: 800;
        background: rgba(0,0,0,0.3);
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(251,191,36,0.3); }
</style>
<div class="bg-animation"></div>
<div class="scan-lines"></div>
""", shared=True)

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
