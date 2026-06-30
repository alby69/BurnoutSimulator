import uuid
from nicegui import ui
from game.engine import GameEngine
from database.analytics import (
    init_db, create_session, end_session, record_choice, record_tags,
)

# ── State ──
screen: str = 'start'
engine: GameEngine | None = None
session_id: str | None = None
stats_before: dict = {}
choice_history: list = []

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
    elif screen == 'game_over':
        _render_game_over()


def _render_start():
    with ui.card().classes('w-full max-w-lg mx-auto p-8 text-center').props('flat'):
        ui.label('BURNOUT SIMULATOR').classes('text-4xl font-bold text-red-400')
        ui.label('Antropologia delle Organizzazioni').classes('text-lg text-gray-400 mb-6')

        ui.label('Scegli il tipo di azienda:').classes('text-gray-300')
        arch_options = {
            k: f"{k} — {v['description']}"
            for k, v in GameEngine.COMPANY_ARCHETYPES.items()
        }
        arch_select = ui.select(
            arch_options, value='Corporate Tossica',
        ).classes('w-full max-w-md')

        ui.label('Il tuo nome:').classes('text-gray-300 mt-4')
        name_input = ui.input(value='Impiegato Anonimo').classes('w-full max-w-md')

        def start_game_cb():
            global engine, session_id, stats_before, screen, choice_history
            session_id = uuid.uuid4().hex[:12]
            choice_history = []
            engine = GameEngine(
                name_input.value, 'game/data/events.json',
                company_type=arch_select.value,
            )
            stats_before = get_stats_dict(engine)
            create_session(session_id, engine.player.name, engine.player.company_type)
            engine.next_turn()
            screen = 'game_over' if engine.is_game_over() else 'game'
            page.refresh()

        ui.button('Inizia Avventura', on_click=start_game_cb, icon='play_arrow') \
            .classes('mt-6').props('color=positive')


def _render_game():
    player = engine.player
    pdata = player.to_dict()
    event = engine.current_event

    with ui.column().classes('w-full gap-0'):
        # Top bar
        total_events = len(engine.event_manager.events)
        unique_seen = len(set(engine.history))
        is_repeat = event and event.id in engine.history[:-1]

        with ui.row().classes('w-full items-center justify-between mb-4'):
            with ui.row().classes('items-center gap-2 flex-wrap'):
                ui.icon('calendar_month').classes('text-gray-400')
                ui.label(f'Giorno {player.days_survived}').classes('text-xl font-bold text-white')
                ui.badge(player.company_type, color='secondary')
                ui.badge(f'Evento {unique_seen}/{total_events}', color='dark') \
                    .props('outline').classes('text-gray-400')
            with ui.row().classes('items-center gap-1'):
                ui.button('', icon='bar_chart', on_click=_show_stats_dialog) \
                    .props('flat').classes('text-gray-400 lg:hidden')
                ui.button('', icon='exit_to_app', on_click=_exit_game) \
                    .props('flat').classes('text-gray-400')

        # Main area
        with ui.row().classes('w-full gap-0'):
            # Stats sidebar
            with ui.card().classes('w-full md:w-64 p-4 gap-2 md:mr-4 mb-4 md:mb-0 bg-gray-900 stats-sidebar') \
                    .props('flat'):
                ui.label('STATISTICHE').classes('text-sm font-bold text-gray-400 mb-2')
                stats = pdata['stats']
                for label, key, color in bars_def:
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(label).classes('text-xs text-gray-400')
                        ui.label(f'{stats[key]}%').classes('text-xs font-mono text-gray-300')
                    bar_color = color if stats[key] > 25 else '#ef4444'
                    ui.linear_progress(value=stats[key] / 100, size='xs', color=bar_color)

                ui.label('FAZIONI').classes('text-sm font-bold text-gray-400 mt-4 mb-1')
                for fname, fscore in pdata['factions'].items():
                    aligned = [n for n, f in engine.NPC_FACTION_MAP.items() if f == fname]
                    aligned_str = f' ({", ".join(aligned)})' if aligned else ''
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(f'{fname}{aligned_str}').classes('text-xs text-gray-400')
                        ui.label(f'{fscore}%').classes('text-xs text-gray-300')

                ui.label('RELAZIONI').classes('text-sm font-bold text-gray-400 mt-4 mb-1')
                for nname, ndata in pdata['npcs'].items():
                    ui.label(
                        f'{nname}:  T{ndata["trust"]}  R{ndata["respect"]}  F{ndata["fear"]}'
                    ).classes('text-xs text-gray-400')

                if choice_history:
                    ui.separator().classes('my-3 bg-gray-700')
                    ui.label('ULTIME SCELTE').classes('text-sm font-bold text-gray-400 mb-2')
                    cat_colors = {
                        'COMPLIANCE': '#3b82f6',
                        'RESISTANCE': '#ef4444',
                        'NEGOTIATION': '#eab308',
                        'ESCAPE': '#22c55e',
                    }
                    for h in choice_history[-5:]:
                        cat_color = cat_colors.get(h['category'], '#6b7280')
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('circle', size='6px').style(f'color: {cat_color}')
                            ui.label(h['text'][:40] + ('…' if len(h['text']) > 40 else '')).classes(
                                'text-xs text-gray-400 truncate'
                            )

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

                    for i, choice in enumerate(event.choices):
                        def handle_choice_cb(idx=0, evt=None, ch=None):
                            return lambda: _make_choice(idx, evt, ch)

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
                            with ui.tooltip().classes('p-2 bg-gray-800 border border-gray-600 rounded'):
                                for effect_key, effect_val in choice.effects.items():
                                    sign = '+' if effect_val > 0 else ''
                                    ui.label(f'{effect_key}: {sign}{effect_val}').classes(
                                        'text-xs font-mono',
                                    )


def _render_game_over():
    player = engine.player
    ending = determine_ending(player)

    end_session(session_id, player.days_survived, player.status, ending)
    record_tags(session_id, player.tags)

    with ui.column().classes('w-full max-w-2xl mx-auto'):
        with ui.card().classes('w-full p-8 text-center').props('flat'):
            ui.label('REPORT FINALE').classes('text-3xl font-bold text-red-400')
            ui.label(ending).classes('text-2xl font-bold text-yellow-400 mt-3')
            ui.badge(player.status, color='secondary').classes('mt-2')
            ui.label(
                f'Hai resistito {player.days_survived} giorni in {player.company_type}.'
            ).classes('text-gray-300 mt-4')

            stats = get_stats_dict(engine)
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

        with ui.row().classes('w-full justify-center mt-6 mb-12'):
            ui.button('Gioca Ancora', icon='replay', on_click=_play_again) \
                .props('color=positive size=lg')


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
    with ui.dialog() as dialog, ui.card().classes('p-6'):
        ui.label('Statistiche Dettagliate').classes('text-lg font-bold mb-4')
        for label, key, color in bars_def:
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(label).classes('text-sm')
                ui.label(f'{stats[key]}%')
            ui.linear_progress(value=stats[key] / 100, size='sm', color=color)
        ui.button('Chiudi', on_click=dialog.close).props('flat')
    dialog.open()


# ── Startup ──

ui.add_head_html("""
<style>
    body { background: #0a0a1a; }
    .choice-btn { text-transform: none; transition: all 0.15s ease; }
    .choice-btn:hover { transform: translateX(4px); }
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
