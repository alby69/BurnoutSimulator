import uuid, random, json, sqlite3, os
from io import BytesIO
from nicegui import ui
from game.engine import GameEngine, NPC_FACTION_MAP
from database.analytics import (
    init_db, create_session, end_session, record_choice, record_tags,
)
from game.events import Choice

# ── State ──
screen: str = 'start'
engine: GameEngine | None = None
session_id: str | None = None
stats_before: dict = {}
choice_history: list = []
_tutorial_active: bool = False
_tutorial_step: int = 0
_timer_active: bool = False

bars_def = [
    ('Energia', 'energy', '#4ade80'),
    ('Stress', 'stress', '#f87171'),
    ('Salute', 'health', '#22d3ee'),
    ('Integrità', 'integrity', '#a78bfa'),
    ('Autostima', 'self_esteem', '#fbbf24'),
    ('Occupabilità', 'employability', '#34d399'),
    ('Rep. Manager', 'manager_rep', '#fb923c'),
    ('Rep. Team', 'team_rep', '#60a5fa'),
]

NPC_FACTION_COLORS = {
    'Fedelissimi': '#7c3aed',
    'Gruppo Silenzioso': '#64748b',
    'Ribelli': '#f87171',
}

ARCHETYPE_THEMES = {
    "Startup Caotica": {
        "accent": "#f97316", "header": "#ea580c", "badge": "warning",
        "glow": "0 0 20px rgba(249,115,22,0.2)",
    },
    "Corporate Tossica": {
        "accent": "#3b82f6", "header": "#2563eb", "badge": "primary",
        "glow": "0 0 20px rgba(59,130,246,0.2)",
    },
    "Azienda Familiare": {
        "accent": "#22c55e", "header": "#16a34a", "badge": "positive",
        "glow": "0 0 20px rgba(34,197,94,0.2)",
    },
    "Consulting": {
        "accent": "#a855f7", "header": "#9333ea", "badge": "secondary",
        "glow": "0 0 20px rgba(168,85,247,0.2)",
    },
}

cat_colors = {
    'COMPLIANCE': '#3b82f6',
    'RESISTANCE': '#ef4444',
    'NEGOTIATION': '#eab308',
    'ESCAPE': '#22c55e',
}


def get_stats_dict(eng: GameEngine) -> dict:
    return eng.player.to_dict()['stats']


def determine_ending(player) -> str:
    endings = []

    # Finali basati sulle fazioni (priorità alta)
    if player.factions['Ribelli'] >= 70 and player.integrity >= 60:
        endings.append(("IL WHISTLEBLOWER", 7))
    if player.factions['Fedelissimi'] >= 70 and player.manager_rep >= 80:
        endings.append(("IL BRACCIO DESTRO", 7))
    if player.factions['Gruppo Silenzioso'] >= 70:
        endings.append(("LO SPETTATORE", 6))
    if all(v >= 50 for v in player.factions.values()):
        endings.append(("IL CAMALEONTE", 5))

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

@ui.refreshable
def page():
    if screen == 'start':
        _render_start()
    elif screen == 'game':
        _render_game()
        if _tutorial_active:
            _render_tutorial()
    elif screen == 'game_over':
        _render_game_over()
    elif screen == 'analytics':
        _render_analytics()


def _render_start():
    with ui.card().classes('w-full max-w-lg mx-auto p-8 text-center').props('flat'):
        theme = ARCHETYPE_THEMES['Corporate Tossica']
        ui.label('BURNOUT SIMULATOR').style(f'color: {theme["header"]}').classes('text-4xl font-bold')
        ui.label('Antropologia delle Organizzazioni').classes('text-lg text-gray-400 mb-6')

        ui.label('Scegli il tipo di azienda:').classes('text-gray-300')
        arch_options = {
            k: f"{k} — {v['description']}"
            for k, v in GameEngine.COMPANY_ARCHETYPES.items()
        }
        arch_select = ui.select(
            arch_options, value='Corporate Tossica',
        ).classes('w-full max-w-md')

        def on_arch_change():
            t = ARCHETYPE_THEMES.get(arch_select.value, ARCHETYPE_THEMES['Corporate Tossica'])
            ui.run_javascript(f'''
                document.documentElement.style.setProperty('--theme-accent', '{t["accent"]}');
                document.querySelector("h1").style.color = '{t["header"]}';
            ''')

        arch_select.on('change', on_arch_change)

        ui.label('Il tuo nome:').classes('text-gray-300 mt-4')
        name_input = ui.input(value='Impiegato Anonimo').classes('w-full max-w-md')

        def start_game_cb():
            global engine, session_id, stats_before, screen, choice_history, _tutorial_active, _tutorial_step
            session_id = uuid.uuid4().hex[:12]
            choice_history = []
            engine = GameEngine(
                name_input.value, 'game/data/events.json',
                company_type=arch_select.value,
            )
            stats_before = get_stats_dict(engine)
            create_session(session_id, engine.player.name, engine.player.company_type)
            engine.next_turn()

            t = ARCHETYPE_THEMES.get(arch_select.value, ARCHETYPE_THEMES['Corporate Tossica'])
            ui.run_javascript(f'''
                document.documentElement.style.setProperty('--theme-accent', '{t["accent"]}');
                document.documentElement.style.setProperty('--theme-header', '{t["header"]}');
                document.documentElement.style.setProperty('--theme-glow', '{t["glow"]}');
            ''')

            _tutorial_active = True
            _tutorial_step = 0
            screen = 'game_over' if engine.is_game_over() else 'game'
            page.refresh()

        ui.button('Inizia Avventura', on_click=start_game_cb, icon='play_arrow') \
            .classes('mt-6').props('color=positive')

        with ui.row().classes('w-full justify-center mt-6 gap-2'):
            ui.button('📊 Analytics', on_click=lambda: _go_analytics()).props('flat').classes('text-gray-400')


def _render_game():
    player = engine.player
    pdata = player.to_dict()
    event = engine.current_event
    theme = ARCHETYPE_THEMES.get(player.company_type, ARCHETYPE_THEMES['Corporate Tossica'])

    with ui.column().classes('w-full gap-0'):
        # Top bar
        total_events = len(engine.event_manager.events)
        unique_seen = len(set(engine.history))
        is_repeat = event and event.id in engine.history[:-1]

        with ui.row().classes('w-full items-center justify-between mb-4'):
            with ui.row().classes('items-center gap-2 flex-wrap'):
                ui.icon('calendar_month').classes('text-gray-400')
                ui.label(f'Giorno {player.days_survived}').style(f'color: {theme["header"]}').classes('text-xl font-bold')
                ui.badge(player.company_type, color=theme['badge'])
                ui.badge(f'Evento {unique_seen}/{total_events}', color='dark') \
                    .props('outline').classes('text-gray-400')
            with ui.row().classes('items-center gap-1'):
                ui.button('', icon='bar_chart', on_click=_show_stats_dialog) \
                    .props('flat').classes('text-gray-400 lg:hidden')
                ui.button('', icon='hub', on_click=_show_decision_graph) \
                    .props('flat').classes('text-gray-400')
                ui.button('', icon='exit_to_app', on_click=_exit_game) \
                    .props('flat').classes('text-gray-400')

        # Main area
        with ui.row().classes('w-full gap-0'):
            # Stats sidebar
            with ui.card().classes('w-full md:w-72 p-4 gap-2 md:mr-4 mb-4 md:mb-0 bg-gray-900 stats-sidebar') \
                    .props('flat'):
                ui.label('STATISTICHE').classes('text-sm font-bold text-gray-400 mb-2')
                stats = pdata['stats']

                # Radar chart
                radar_data = [
                    {'name': 'Energia', 'value': stats['energy']},
                    {'name': 'Stress', 'value': stats['stress']},
                    {'name': 'Salute', 'value': stats['health']},
                    {'name': 'Integrità', 'value': stats['integrity']},
                    {'name': 'Autostima', 'value': stats['self_esteem']},
                    {'name': 'Occupabilità', 'value': stats['employability']},
                ]
                radar_option = {
                    'radar': {
                        'indicator': [{'name': r['name'], 'max': 100} for r in radar_data],
                        'shape': 'circle',
                        'splitArea': {'areaStyle': {'color': ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.05)']}},
                        'axisLine': {'lineStyle': {'color': 'rgba(255,255,255,0.1)'}},
                        'splitLine': {'lineStyle': {'color': 'rgba(255,255,255,0.1)'}},
                    },
                    'series': [{
                        'type': 'radar',
                        'data': [{'value': [s['value'] for s in radar_data], 'name': 'Profilo'}],
                        'areaStyle': {'color': theme['accent'] + '40'},
                        'lineStyle': {'color': theme['accent'], 'width': 2},
                        'itemStyle': {'color': theme['accent']},
                    }],
                    'backgroundColor': 'transparent',
                }
                ui.echart(radar_option).classes('w-full h-44')

                # Stat bars with pulse on critical
                for label, key, color in bars_def:
                    is_critical = stats[key] <= 20 or (key == 'stress' and stats[key] >= 80)
                    pulse_class = ' pulse-danger' if is_critical else ''
                    with ui.row().classes(f'w-full items-center justify-between{pulse_class}'):
                        ui.label(label).classes('text-xs text-gray-400')
                        val = stats[key]
                        val_color = '#ef4444' if (val <= 20 or (key == 'stress' and val >= 80)) else color
                        ui.label(f'{val}%').style(f'color: {val_color}').classes('text-xs font-mono')
                    bar_color = '#ef4444' if is_critical else color
                    ui.linear_progress(value=stats[key] / 100, size='xs', color=bar_color)

                # FAZIONI
                ui.label('FAZIONI').classes('text-sm font-bold text-gray-400 mt-4 mb-1')
                for fname, fscore in pdata['factions'].items():
                    fcol = NPC_FACTION_COLORS.get(fname, '#6b7280')
                    aligned = [n for n, f in NPC_FACTION_MAP.items() if f == fname]
                    aligned_str = f' ({", ".join(aligned)})' if aligned else ''
                    with ui.row().classes('w-full items-center justify-between'):
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('circle', size='8px').style(f'color: {fcol}')
                            ui.label(f'{fname}{aligned_str}').classes('text-xs text-gray-400')
                        ui.label(f'{fscore}%').classes('text-xs text-gray-300')

                # RELAZIONI con avatar
                ui.label('RELAZIONI').classes('text-sm font-bold text-gray-400 mt-4 mb-1')
                for nname, ndata in pdata['npcs'].items():
                    nfaction = NPC_FACTION_MAP.get(nname, '')
                    avi_color = NPC_FACTION_COLORS.get(nfaction, '#6b7280')
                    initial = nname[0]
                    trust = ndata['trust']
                    trust_color = '#4ade80' if trust >= 60 else '#f87171' if trust < 35 else '#eab308'
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.label(initial).style(f'background: {avi_color}').classes('npc-avatar')
                        with ui.column().classes('gap-0 flex-1'):
                            ui.label(nname).classes('text-xs text-gray-300')
                            ui.label(
                                f'Fiducia {trust}%  Rispetto {ndata["respect"]}%  Paura {ndata["fear"]}%'
                            ).style(f'color: {trust_color}').classes('text-[10px]')

                # ULTIME SCELTE
                if choice_history:
                    ui.separator().classes('my-3 bg-gray-700')
                    ui.label('ULTIME SCELTE').classes('text-sm font-bold text-gray-400 mb-2')
                    for h in choice_history[-5:]:
                        cat_color = cat_colors.get(h['category'], '#6b7280')
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('circle', size='6px').style(f'color: {cat_color}')
                            ui.label(h['text'][:40] + ('…' if len(h['text']) > 40 else '')).classes(
                                'text-xs text-gray-400 truncate'
                            )

                # STATO
                ui.separator().classes('my-3 bg-gray-700')
                ui.label('STATO').classes('text-sm font-bold text-gray-400 mb-2')

                risk_critical = sum(1 for s in stats.values() if s <= 20) + (1 if stats['stress'] >= 80 else 0)
                risk_warning = sum(1 for s in stats.values() if 20 < s <= 35 or 65 <= s < 80)

                if not engine.player.is_alive:
                    risk_label = 'Terminato'
                    risk_color = 'text-gray-500'
                elif risk_critical >= 3 or stats['stress'] >= 85 or stats['health'] <= 15:
                    risk_label = 'Pericolo Imminente'
                    risk_color = 'text-red-400 font-bold'
                elif risk_critical >= 1 or risk_warning >= 3:
                    risk_label = 'Critico'
                    risk_color = 'text-orange-400 font-bold'
                elif risk_warning >= 1:
                    risk_label = 'Moderato'
                    risk_color = 'text-yellow-400'
                else:
                    risk_label = 'Stabile'
                    risk_color = 'text-green-400'

                ui.label(risk_label).classes(f'{risk_color} text-base')
                ui.linear_progress(
                    value=min(stats['stress'] / 100, 1.0),
                    size='sm',
                    color='red' if stats['stress'] > 65 else 'orange' if stats['stress'] > 40 else 'green',
                ).classes('w-full mt-1')
                ui.label('Stress').classes('text-xs text-gray-500')

                danger_stats = []
                if stats['stress'] >= 75:
                    danger_stats.append('Stress: rischio burnout')
                if stats['health'] <= 25:
                    danger_stats.append('Salute: critica')
                if stats['energy'] <= 20:
                    danger_stats.append('Energia: esaurita')
                if stats['self_esteem'] <= 20:
                    danger_stats.append('Autostima: a terra')
                if stats['manager_rep'] <= 20:
                    danger_stats.append('Rep. Manager: rischio licenziamento')
                for msg in danger_stats[:2]:
                    ui.label(f'⚠ {msg}').classes('text-xs text-red-400 mt-1')

            # Event + Choices
            with ui.column().classes('flex-1 gap-4 min-w-0'):
                # Mini-evento giornaliero
                if engine.current_mini_event:
                    mini_text, mini_effects = engine.current_mini_event
                    with ui.card().classes('w-full p-3 bg-gray-800/50 border-l-4 border-gray-600').props('flat'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('wb_sunny', size='16px').classes('text-gray-500')
                            ui.label('Routine').classes('text-xs font-bold text-gray-500 uppercase tracking-wide')
                        ui.label(mini_text).classes('text-sm text-gray-400 italic')
                        with ui.row().classes('gap-2 mt-1 flex-wrap'):
                            for k, v in mini_effects.items():
                                if v > 0:
                                    ui.badge(f'{k}: +{v}', color='dark').props('outline')
                                else:
                                    ui.badge(f'{k}: {v}', color='dark').props('outline')

                if event:
                    with ui.row().classes('items-center gap-2 flex-wrap'):
                        ui.badge(
                            event.category.replace('_', ' ').upper(),
                            color='warning',
                        )
                        if is_repeat:
                            ui.badge('Già visto', color='dark').props('outline')
                        if engine.deferred_events:
                            ui.badge(f'{len(engine.deferred_events)} in sospeso', color='dark').props('outline')

                    with ui.card().classes('w-full p-6 bg-gray-900').props('flat'):
                        ui.markdown(event.text).classes(
                            'text-base leading-relaxed text-gray-200 '
                            'prose prose-invert max-w-none'
                        )

                    n_choices = len(event.choices)
                    if n_choices == 1:
                        ui.label('Conseguenza — proseguì automaticamente').classes(
                            'text-sm text-gray-500 italic mt-2'
                        )
                    else:
                        ui.label('Cosa fai?').classes(
                            'text-sm font-semibold text-gray-400 mt-2'
                        )

                    # Timer per scelte critiche (M12)
                    _timer_choice_idx = -1
                    if n_choices > 1:
                        _timer_choice_idx = random.randint(0, n_choices - 1)

                    for i, choice in enumerate(event.choices):
                        def handle_choice_cb(idx=0, evt=None, ch=None):
                            return lambda: _make_choice(idx, evt, ch)

                        timer_class = ''
                        if i == _timer_choice_idx and n_choices > 1:
                            timer_class = ' timer-choice'

                        label = f'{chr(65 + i)}. {choice.text}'
                        if n_choices == 1:
                            label = 'Continua →'

                        with ui.button(
                            label,
                            on_click=handle_choice_cb(i, event, choice),
                        ).classes(
                            'w-full text-left choice-btn rounded-lg border '
                            f'{"border-blue-700 hover:border-blue-500" if n_choices == 1 else "border-gray-700 hover:border-gray-500"} '
                            'hover:bg-gray-800 transition-all'
                        ).props('flat no-caps'):

                            # Effetti sempre visibili (chip)
                            if choice.effects:
                                with ui.row().classes('gap-1 mt-1 flex-wrap'):
                                    for ek, ev in list(choice.effects.items())[:4]:
                                        cls = 'pos' if ev > 0 else 'neg'
                                        sign = '+' if ev > 0 else ''
                                        ui.label(f'{ek}: {sign}{ev}').classes(f'effect-chip {cls}')

                            # Timer su scelta critica
                            if i == _timer_choice_idx and n_choices > 1:
                                timer_id = f'timer_{uuid.uuid4().hex[:6]}'
                                ui.label().classes('timer-ring').props(f'id={timer_id}')
                                ui.run_javascript(f'''
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
                                ''')

                            # Tooltip (M3)
                            with ui.tooltip().classes('p-2 bg-gray-800 border border-gray-600 rounded'):
                                for effect_key, effect_val in choice.effects.items():
                                    sign = '+' if effect_val > 0 else ''
                                    ui.label(f'{effect_key}: {sign}{effect_val}').classes('text-xs font-mono')


def _render_game_over():
    player = engine.player
    ending = determine_ending(player)

    end_session(session_id, player.days_survived, player.status, ending)
    record_tags(session_id, player.tags)
    stats = get_stats_dict(engine)

    with ui.column().classes('w-full max-w-2xl mx-auto'):
        with ui.card().classes('w-full p-8 text-center report-card').props('flat'):

            ui.label('REPORT FINALE').classes('text-3xl font-bold text-red-400')
            ui.label(ending).classes('text-2xl font-bold text-yellow-400 mt-3')
            ui.badge(player.status, color='secondary').classes('mt-2')
            ui.label(
                f'Hai resistito {player.days_survived} giorni in {player.company_type}.'
            ).classes('text-gray-300 mt-4')

            # Radar finale
            radar_data = [
                {'name': 'Energia', 'value': stats['energy']},
                {'name': 'Stress', 'value': stats['stress']},
                {'name': 'Salute', 'value': stats['health']},
                {'name': 'Integrità', 'value': stats['integrity']},
                {'name': 'Autostima', 'value': stats['self_esteem']},
                {'name': 'Occupabilità', 'value': stats['employability']},
            ]
            radar_option = {
                'radar': {
                    'indicator': [{'name': r['name'], 'max': 100} for r in radar_data],
                    'shape': 'circle',
                    'splitArea': {'areaStyle': {'color': ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.05)']}},
                    'axisLine': {'lineStyle': {'color': 'rgba(255,255,255,0.1)'}},
                    'splitLine': {'lineStyle': {'color': 'rgba(255,255,255,0.1)'}},
                },
                'series': [{
                    'type': 'radar',
                    'data': [{'value': [s['value'] for s in radar_data], 'name': 'Profilo'}],
                    'areaStyle': {'color': 'rgba(168,85,247,0.3)'},
                    'lineStyle': {'color': '#a855f7', 'width': 2},
                    'itemStyle': {'color': '#a855f7'},
                }],
                'backgroundColor': 'transparent',
            }
            ui.echart(radar_option).classes('w-full h-48 mt-4')

            with ui.row().classes('w-full justify-center gap-6 mt-6'):
                for key, label, color in [
                    ('energy', 'Energia', '#4ade80'),
                    ('stress', 'Stress', '#f87171'),
                    ('health', 'Salute', '#22d3ee'),
                    ('integrity', 'Integrità', '#a78bfa'),
                ]:
                    with ui.column().classes('items-center'):
                        ui.linear_progress(
                            value=stats[key] / 100, size='md', color=color,
                        ).classes('w-20')
                        ui.label(f'{label}: {stats[key]}%').classes('text-xs text-gray-400')

        tags = player.tags
        total_tags = sum(tags.values())
        if total_tags > 0:
            with ui.card().classes('w-full p-6 mt-4').props('flat'):
                ui.label('PROFILO COMPORTAMENTALE').classes(
                    'text-lg font-bold text-gray-300 mb-4'
                )
                for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        perc = (count / total_tags) * 100
                        with ui.row().classes('items-center gap-3'):
                            ui.linear_progress(
                                value=perc / 100, size='sm', color='amber',
                            ).classes('w-40')
                            ui.label(
                                f'{tag.replace("_", " ").title()}: {perc:.1f}%'
                            ).classes('text-sm text-gray-400')

        if player.achievements:
            with ui.card().classes('w-full p-6 mt-4').props('flat'):
                ui.label('ACHIEVEMENT').classes('text-lg font-bold text-gray-300 mb-3')
                for ach in player.achievements:
                    ui.badge(f'\U0001f3c6 {ach}', color='positive').classes('mr-2 mb-2')

        with ui.card().classes('w-full p-6 mt-4').props('flat'):
            ui.label('ANALISI ANTROPOLOGICA').classes(
                'text-lg font-bold text-gray-300 mb-3'
            )
            if player.factions['Ribelli'] > 30:
                ui.label(
                    '- Hai mostrato una forte tendenza alla resistenza attiva, '
                    'prioritizzando l\'integrità individuale.'
                ).classes('text-sm text-gray-400')
            if player.factions['Fedelissimi'] > 30:
                ui.label(
                    '- Il tuo adattamento è stato di tipo opportunistico, '
                    'integrando i valori dominanti dell\'organizzazione.'
                ).classes('text-sm text-gray-400')
            if player.stress > 70:
                ui.label(
                    '- L\'esposizione prolungata a dinamiche tossiche ha eroso '
                    'le tue barriere psicologiche (Burnout Alert).'
                ).classes('text-sm text-gray-400')

        with ui.row().classes('w-full justify-center mt-6 mb-12 gap-3'):
            ui.button('Gioca Ancora', icon='replay', on_click=_play_again) \
                .props('color=positive size=lg')
            ui.button('📷 Esporta Report', icon='download', on_click=_export_report) \
                .props('flat size=lg').classes('text-gray-400')
            ui.button('🕸 Grafo Decisionale', icon='hub', on_click=_show_decision_graph) \
                .props('flat size=lg').classes('text-gray-400')


# ── Actions ──

def _make_choice(idx: int, event, choice):
    global stats_before, choice_history
    stats_before = get_stats_dict(engine)
    engine.handle_choice(idx)
    stats_after = get_stats_dict(engine)

    record_choice(
        session_id, engine.player.days_survived,
        event.id, choice.id, choice.text, choice.category,
        stats_before, stats_after,
    )

    choice_history.append({
        'text': choice.text,
        'category': choice.category,
    })

    deltas = {}
    for key in stats_before:
        d = stats_after[key] - stats_before[key]
        if d != 0:
            deltas[key] = d

    _show_choice_feedback(deltas, choice.category)


def _show_choice_feedback(deltas: dict, category: str):
    stat_labels = {
        'energy': 'Energia', 'stress': 'Stress', 'health': 'Salute',
        'integrity': 'Integrità', 'self_esteem': 'Autostima',
        'employability': 'Occupabilità', 'manager_rep': 'Rep. Manager',
        'team_rep': 'Rep. Team',
    }
    stat_colors = {
        'energy': '#4ade80', 'stress': '#f87171', 'health': '#22d3ee',
        'integrity': '#a78bfa', 'self_esteem': '#fbbf24',
        'employability': '#34d399', 'manager_rep': '#fb923c', 'team_rep': '#60a5fa',
    }

    with ui.dialog() as dialog, ui.card().classes('p-6 min-w-[280px] bg-gray-900'):
        ui.label('Esito della scelta').classes('text-lg font-bold text-gray-200 mb-1')
        ui.badge(category, color='dark').classes('mb-4')

        has_effects = False
        for key in deltas:
            has_effects = True
            delta = deltas[key]
            sign = '+' if delta > 0 else ''
            color = stat_colors.get(key, '#9ca3af')
            label = stat_labels.get(key, key)
            bg = 'bg-green-900/30' if delta > 0 else 'bg-red-900/30'
            text_color = 'text-green-400' if delta > 0 else 'text-red-400'
            arrow = '▲' if delta > 0 else '▼'
            with ui.row().classes(f'w-full items-center justify-between px-3 py-1 rounded {bg}'):
                ui.label(label).classes('text-sm text-gray-300')
                ui.label(f'{arrow} {sign}{delta}').classes(f'text-sm font-bold {text_color}')

        if not has_effects:
            ui.label('Nessun effetto rilevante sulle statistiche').classes('text-sm text-gray-500 italic')

        def advance():
            dialog.close()
            if engine.is_game_over():
                screen = 'game_over'
            else:
                engine.next_turn()
                screen = 'game_over' if engine.is_game_over() else 'game'
            page.refresh()

        ui.button('Continua', on_click=advance).props('color=positive').classes('mt-4 w-full')
    dialog.open()


def _render_tutorial():
    steps = [
        {
            'title': 'Benvenuto in Burnout Simulator',
            'text': 'Questa è una simulazione di antropologia organizzativa. <b>Ogni scelta conta:</b> le tue decisioni influenzeranno le tue statistiche, i rapporti con i colleghi e il finale della partita.',
        },
        {
            'title': 'Le Statistiche',
            'text': 'A sinistra trovi il <b>radar psicologico</b> e le barre numeriche. Tienile d\'occhio: stress alto e salute bassa possono portare al burnout. Le barre pulsano quando sono in zona critica.',
        },
        {
            'title': 'Fazioni e NPC',
            'text': 'I tuoi colleghi appartengono a fazioni (Fedelissimi, Gruppo Silenzioso, Ribelli). Guadagnare o perdere fiducia con loro cambia il gioco. Ogni NPC ha un avatar colorato in base alla fazione.',
        },
        {
            'title': 'Le Scelte',
            'text': 'Le scelte mostrano gli effetti direttamente nel bottone (+/-). Su alcune scelte critiche parte un <b>timer di 15 secondi</b> per simulare la pressione lavorativa. Non farti prendere dal panico!',
        },
        {
            'title': 'Pronto?',
            'text': 'Ricorda: non esiste la scelta giusta. Esiste la scelta <b>coerente</b> con il tuo stile. Buona fortuna.',
        },
    ]
    if _tutorial_step >= len(steps):
        return
    step = steps[_tutorial_step]
    with ui.column().classes('tutorial-overlay'):
        with ui.card().classes('tutorial-card').props('flat'):
            ui.label(step['title']).classes('text-lg font-bold text-white mb-3')
            ui.html(step['text']).classes('text-sm text-gray-300 leading-relaxed')
            ui.html('<br>')
            with ui.row().classes('justify-center gap-2'):
                if _tutorial_step > 0:
                    ui.button('← Indietro', on_click=lambda: _tutorial_prev()).props('flat').classes('text-gray-400')
                btn_label = 'Inizia a giocare →' if _tutorial_step == len(steps) - 1 else 'Avanti →'
                ui.button(btn_label, on_click=_tutorial_next).props('color=positive')


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
    screen = 'game_over'
    page.refresh()


def _play_again():
    global screen, engine, session_id, choice_history
    engine = None
    session_id = None
    choice_history = []
    screen = 'start'
    page.refresh()


def _show_stats_dialog():
    stats = get_stats_dict(engine)
    pdata = engine.player.to_dict()
    with ui.dialog() as dialog, ui.card().classes('p-6'):
        ui.label('Statistiche Dettagliate').classes('text-lg font-bold mb-4')
        for label, key, color in bars_def:
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(label).classes('text-sm')
                val = stats[key]
                val_color = '#ef4444' if (val <= 20 or (key == 'stress' and val >= 80)) else color
                ui.label(f'{val}%').style(f'color: {val_color}')
            ui.linear_progress(value=stats[key] / 100, size='sm', color=color)
        ui.label('FAZIONI').classes('text-sm font-bold mt-4 mb-2')
        for fname, fscore in pdata['factions'].items():
            fcol = NPC_FACTION_COLORS.get(fname, '#6b7280')
            with ui.row().classes('items-center gap-2'):
                ui.icon('circle', size='8px').style(f'color: {fcol}')
                ui.label(f'{fname}: {fscore}%').classes('text-sm')
        ui.button('Chiudi', on_click=dialog.close).props('flat')
    dialog.open()


def _export_report():
    ui.run_javascript('''
        (function() {
            const el = document.querySelector('.report-card');
            if (!el) return;
            import('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js')
            .then(() => {
                html2canvas(el, { backgroundColor: '#0a0a1a', scale: 2 })
                .then(canvas => {
                    const link = document.createElement('a');
                    link.download = 'burnout-report.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                });
            })
            .catch(() => alert('Esportazione non disponibile (nessuna connessione)'));
        })();
    ''')


def _show_decision_graph():
    if not engine or not engine.graph.history:
        ui.notify('Nessun dato disponibile per il grafo', type='warning')
        return

    graph = engine.graph
    event_mgr = engine.event_manager
    history = graph.history

    nodes_map = {}
    edges = []

    for entry in history:
        ev_id = entry['event_id']
        ch_id = entry['choice_id']
        nxt = entry.get('next_event_id')

        if ev_id not in nodes_map:
            ev = event_mgr.get_event(ev_id)
            cat = ev.category if ev else 'unknown'
            cat_colors_map = {
                'micromanagement': '#3b82f6', 'mobbing': '#ef4444',
                'favoritismo': '#eab308', 'burnout': '#f97316',
                'scapegoating': '#a855f7',
            }
            nodes_map[ev_id] = {
                'id': ev_id,
                'name': ev_id.replace('_', ' ')[:25],
                'symbolSize': 20,
                'itemStyle': {'color': cat_colors_map.get(cat, '#6b7280')},
                'category': cat,
            }

        if nxt and nxt not in nodes_map:
            ev = event_mgr.get_event(nxt)
            if ev:
                cat = ev.category if ev else 'unknown'
                cat_colors_map = {
                    'micromanagement': '#3b82f6', 'mobbing': '#ef4444',
                    'favoritismo': '#eab308', 'burnout': '#f97316',
                    'scapegoating': '#a855f7',
                }
                nodes_map[nxt] = {
                    'id': nxt,
                    'name': nxt.replace('_', ' ')[:25],
                    'symbolSize': 16,
                    'itemStyle': {'color': cat_colors_map.get(cat, '#6b7280')},
                    'category': 'consequence',
                }

        ev = event_mgr.get_event(ev_id)
        choice_text = ''
        if ev:
            for c in ev.choices:
                if c.id == ch_id:
                    choice_text = c.category
                    break

        edge_color = {
            'COMPLIANCE': '#3b82f6', 'RESISTANCE': '#ef4444',
            'NEGOTIATION': '#eab308', 'ESCAPE': '#22c55e',
        }.get(choice_text, '#6b7280')

        target = nxt if nxt else ''
        if target:
            edges.append({
                'source': ev_id,
                'target': target,
                'label': {'formatter': choice_text, 'fontSize': 9, 'color': edge_color},
                'lineStyle': {'color': edge_color, 'width': 1.5, 'curveness': 0.2},
            })

    option = {
        'tooltip': {'formatter': '{b}'},
        'series': [{
            'type': 'graph',
            'layout': 'force',
            'force': {'repulsion': 300, 'edgeLength': 120},
            'draggable': True,
            'roam': True,
            'data': list(nodes_map.values()),
            'edges': edges,
            'categories': [
                {'name': 'micromanagement', 'itemStyle': {'color': '#3b82f6'}},
                {'name': 'mobbing', 'itemStyle': {'color': '#ef4444'}},
                {'name': 'favoritismo', 'itemStyle': {'color': '#eab308'}},
                {'name': 'burnout', 'itemStyle': {'color': '#f97316'}},
                {'name': 'scapegoating', 'itemStyle': {'color': '#a855f7'}},
                {'name': 'consequence', 'itemStyle': {'color': '#6b7280'}},
            ],
            'lineStyle': {'color': 'source', 'curveness': 0.3},
            'label': {'show': True, 'position': 'bottom', 'fontSize': 10, 'color': '#ccc'},
            'emphasis': {'focus': 'adjacency', 'lineStyle': {'width': 3}},
        }],
        'backgroundColor': 'transparent',
    }

    with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl p-4 bg-gray-900'):
        with ui.row().classes('w-full items-center justify-between mb-2'):
            ui.label('Grafo Decisionale').classes('text-lg font-bold text-gray-200')
            ui.button('', icon='close', on_click=dialog.close).props('flat').classes('text-gray-400')
        ui.echart(option).classes('w-full h-[500px]')
        ui.label(f'{len(nodes_map)} nodi · {len(edges)} connessioni · trascina per esplorare').classes(
            'text-xs text-gray-500 text-center mt-1'
        )
    dialog.open()


def _go_analytics():
    global screen
    screen = 'analytics'
    page.refresh()


def _render_analytics():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'analytics.db')
    with ui.column().classes('w-full max-w-4xl mx-auto'):
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('📊 Dashboard Analytics').classes('text-2xl font-bold text-white')
            ui.button('← Torna al Menu', on_click=lambda: _play_again()).props('flat').classes('text-gray-400')

        if not os.path.exists(db_path):
            ui.label('Nessun dato analytics ancora disponibile.').classes('text-gray-400')
            return

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Finali più ottenuti
            cur.execute('''
                SELECT ending, COUNT(*) as cnt FROM sessions
                WHERE ending IS NOT NULL AND ending != ''
                GROUP BY ending ORDER BY cnt DESC LIMIT 10
            ''')
            ending_data = cur.fetchall()

            # Scelte per categoria
            cur.execute('''
                SELECT category, COUNT(*) as cnt FROM choices
                GROUP BY category ORDER BY cnt DESC
            ''')
            cat_data = cur.fetchall()

            # Sopravvivenza media per archetipo
            cur.execute('''
                SELECT company_type, ROUND(AVG(days_survived), 1) as avg_days,
                       COUNT(*) as sessions
                FROM sessions
                GROUP BY company_type ORDER BY avg_days DESC
            ''')
            surv_data = cur.fetchall()

            # Totale sessioni
            cur.execute('SELECT COUNT(*) FROM sessions')
            total_sessions = cur.fetchone()[0]

            conn.close()
        except sqlite3.Error:
            ui.label('Errore lettura database.').classes('text-gray-400')
            return

        with ui.grid(columns=2).classes('w-full gap-4'):
            with ui.card().classes('p-4').props('flat tight'):
                ui.label('Finali più ottenuti').classes('text-sm font-bold text-gray-300 mb-2')
                total = sum(r[1] for r in ending_data) or 1
                for name, cnt in ending_data:
                    perc = cnt / total * 100
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.label(name).classes('text-xs text-gray-400 flex-1')
                        ui.label(f'{cnt}').classes('text-xs font-mono text-gray-300')
                        ui.linear_progress(value=perc / 100, size='xs', color='amber').classes('w-16')

            with ui.card().classes('p-4').props('flat tight'):
                ui.label('Scelte per categoria').classes('text-sm font-bold text-gray-300 mb-2')
                total_cat = sum(r[1] for r in cat_data) or 1
                for name, cnt in cat_data:
                    perc = cnt / total_cat * 100
                    cat_color = cat_colors.get(name, '#6b7280')
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.icon('circle', size='6px').style(f'color: {cat_color}')
                        ui.label(name).classes('text-xs text-gray-400 flex-1')
                        ui.label(f'{cnt}').classes('text-xs font-mono text-gray-300')
                        ui.linear_progress(value=perc / 100, size='xs', color='amber').classes('w-16')

        # Tabella sopravvivenza
        with ui.card().classes('w-full p-4 mt-4').props('flat'):
            ui.label(f'Sopravvivenza media per archetipo (totale: {total_sessions} partite)').classes(
                'text-sm font-bold text-gray-300 mb-2'
            )
            for arch, avg, sessions in surv_data:
                with ui.row().classes('w-full items-center gap-2'):
                    color = ARCHETYPE_THEMES.get(arch, {}).get('accent', '#6b7280')
                    ui.icon('circle', size='6px').style(f'color: {color}')
                    ui.label(arch).classes('text-xs text-gray-400 w-36')
                    ui.label(f'{avg} giorni').classes('text-xs font-mono text-gray-300 w-20')
                    ui.linear_progress(value=min(float(avg) / 50, 1.0), size='xs', color='primary').classes('flex-1')
                    ui.label(f'({sessions} partite)').classes('text-xs text-gray-500')

        # Ultime partite
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('''
                SELECT name, company_type, days_survived, ending, status
                FROM sessions ORDER BY rowid DESC LIMIT 10
            ''')
            recent = cur.fetchall()
            conn.close()
        except sqlite3.Error:
            recent = []

        if recent:
            with ui.card().classes('w-full p-4 mt-4').props('flat'):
                ui.label('Ultime partite').classes('text-sm font-bold text-gray-300 mb-2')
                for name, arch, days, ending, status in recent:
                    with ui.row().classes('w-full items-center gap-2 border-b border-gray-800 pb-1'):
                        ui.label(name).classes('text-xs text-gray-300 w-24 truncate')
                        ui.label(arch).classes('text-xs text-gray-500 w-32')
                        ui.label(f'{days} gg').classes('text-xs font-mono text-gray-400 w-16')
                        ui.label(ending or '-').classes('text-xs text-yellow-400 flex-1')
                        ui.label(status or '-').classes('text-xs text-gray-500')
            ui.html('<br>')

        with ui.row().classes('w-full justify-center mt-4 mb-12'):
            ui.button('Gioca una partita', icon='play_arrow', on_click=_play_again) \
                .props('color=positive')


# ── Startup ──

ui.add_head_html("""
<style>
    body { background: #0a0a1a; }
    .choice-btn { text-transform: none; transition: all 0.15s ease; position: relative; }
    .choice-btn:hover { transform: translateX(4px); }
    .choice-btn .effect-chip {
        font-size: 10px; padding: 1px 6px; border-radius: 8px;
        background: rgba(255,255,255,0.08);
    }
    .choice-btn .effect-chip.pos { color: #4ade80; }
    .choice-btn .effect-chip.neg { color: #f87171; }

    .pulse-danger {
        animation: pulse-danger 1.2s ease-in-out infinite;
    }
    @keyframes pulse-danger {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.45; }
    }

    .npc-avatar {
        width: 26px; height: 26px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 700; color: #fff;
        flex-shrink: 0;
    }

    .tutorial-overlay {
        position: fixed; inset: 0; z-index: 9999;
        background: rgba(0,0,0,0.7);
        display: flex; align-items: center; justify-content: center;
    }
    .tutorial-card {
        max-width: 420px; background: #1a1a2e; border: 1px solid #7c3aed;
        border-radius: 16px; padding: 28px; text-align: center;
    }

    .timer-ring {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 12px; color: #fbbf24; font-weight: 600;
    }

    @media (max-width: 767px) {
        .stats-sidebar { display: none; }
    }
    @media (min-width: 768px) {
        .mobile-stats-btn { display: none !important; }
    }
</style>
""")

init_db()

ui.column().classes('w-full max-w-5xl mx-auto p-4 gap-4')
page()

ui.run(title='Burnout Simulator', dark=True, favicon='\U0001f3e2')
