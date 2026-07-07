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

CAT_COLORS = {
    "COMPLIANCE": "#3b82f6",
    "RESISTANCE": "#ef4444",
    "NEGOTIATION": "#eab308",
    "ESCAPE": "#22c55e",
}

BARS_DEF = [
    ("Energia", "energy", "#4ade80"),
    ("Stress", "stress", "#f87171"),
    ("Salute", "health", "#22d3ee"),
    ("Integrità", "integrity", "#a78bfa"),
    ("Autostima", "self_esteem", "#fbbf24"),
    ("Occupabilità", "employability", "#34d399"),
    ("Rep. Manager", "manager_rep", "#fb923c"),
    ("Rep. Team", "team_rep", "#60a5fa"),
]

from nicegui import ui

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

    body.light-mode {
        background: #f8fafc;
        color: #0f172a;
    }
    body.light-mode .vn-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.1);
        color: #1e293b;
    }
    body.light-mode .narrative-text {
        color: #334155;
        text-shadow: none;
    }
    body.light-mode .choice-btn {
        background: #f1f5f9 !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    body.light-mode .choice-btn:hover {
        background: #e2e8f0 !important;
    }

    /* High Contrast Mode */
    body.high-contrast {
        background: #000000 !important;
        color: #ffffff !important;
    }
    body.high-contrast .vn-card,
    body.high-contrast .event-card,
    body.high-contrast .choice-btn {
        background: #000000 !important;
        border: 2px solid #ffffff !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }
    body.high-contrast .text-gray-400,
    body.high-contrast .text-gray-500 {
        color: #ffffff !important;
    }
    body.high-contrast .narrative-text {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    body.high-contrast .choice-btn:hover {
        background: #ffffff !important;
        color: #000000 !important;
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
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 255, 0, 0.02));
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

    /* Screen Shake Animation */
    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        40% { transform: translate(1px, -1px) rotate(1deg); }
        50% { transform: translate(-1px, 2px) rotate(-1deg); }
        60% { transform: translate(-3px, 1px) rotate(0deg); }
        70% { transform: translate(3px, 1px) rotate(-1deg); }
        80% { transform: translate(-1px, -1px) rotate(1deg); }
        90% { transform: translate(1px, 2px) rotate(0deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    .shake { animation: shake 0.5s; animation-iteration-count: 1; }

    /* Reading speed classes */
    .typewriter-text {
        overflow: hidden;
        white-space: normal;
    }
</style>
<div class="bg-animation"></div>
<div class="scan-lines"></div>
""", shared=True)
