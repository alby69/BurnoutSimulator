from nicegui import ui
import random, uuid
from ui.theme import ARCHETYPE_THEMES, CAT_COLORS, NPC_FACTION_COLORS
from ui.assets import GFX_PATH, EMOTE_ICONS
from game.engine import NPC_FACTION_MAP, CAREER_PHASES
from ui.components.sidebar import (
    render_stats_section,
    render_factions_section,
    render_relationships_section,
)
from ui.components.common import state_icon, event_icon, npc_portrait, effect_label
import game.state as state
from ui.pages.logic import (
    render_jump_dialog,
    go_to_laboratory,
    show_help,
    show_decision_graph,
    exit_game,
    make_choice,
    tutorial_next,
    tutorial_prev,
)


def render_game():
    engine = state.engine
    player = engine.player

    # Adaptive Audio (Placeholder logic)
    stress_level = player.stress
    audio_file = "ambient_low.mp3"
    if stress_level > 70:
        audio_file = "ambient_high.mp3"
    elif stress_level > 40:
        audio_file = "ambient_med.mp3"

    # Simple audio element that doesn't block (using a hidden ui.html or similar)
    # ui.html(f'<audio autoplay loop src="static/audio/{audio_file}" style="display:none"></audio>')
    pdata = player.to_dict()
    event = engine.current_event
    theme = ARCHETYPE_THEMES.get(
        player.company_type.value, ARCHETYPE_THEMES["Corporate Tossica"]
    )

    if state.current_agent_id:
        with ui.row().classes(
            "w-full bg-purple-900/30 p-2 items-center justify-between border-b border-purple-500/50 mb-4"
        ):
            ui.label(f"POSSESSO AGENTE: {player.name}").classes(
                "text-xs font-black text-purple-300"
            )
            with ui.row().classes("gap-2"):
                ui.button(
                    "SALTA", icon="swap_horiz", on_click=render_jump_dialog
                ).props("flat size=sm").classes("text-white")
                ui.button(
                    "LABORATORIO",
                    icon="biotech",
                    on_click=go_to_laboratory,
                ).props("flat size=sm").classes("text-white")

    mobile_cls = " pb-20" if state._layout_mode == "mobile" else ""
    with ui.column().classes(f"w-full gap-0{mobile_cls}"):
        # Top bar
        total_events = len(engine.event_manager.events)
        unique_seen = len(set(engine.history))
        is_repeat = event and event.id in engine.history[:-1]

        # Timeline Visiva (Proposta 2.3)
        with ui.row().classes("w-full h-2 gap-1 mb-4"):
            total_days_goal = 60
            for i in range(total_days_goal):
                color = "bg-blue-500" if i < player.days_survived else "bg-gray-800"
                # Milestone markers
                is_milestone = any(m[0] == i for m in CAREER_PHASES)
                if is_milestone:
                    color = "bg-amber-500" if i < player.days_survived else "bg-amber-900"
                ui.element("div").classes(f"flex-1 h-full {color} rounded-full transition-all")

        with ui.row().classes(
            "w-full items-center justify-between mb-6 pb-4 border-b border-white/5"
        ):
            with ui.row().classes("items-center gap-4 flex-wrap"):
                with ui.column().classes("gap-0"):
                    ui.label("GIORNO").classes(
                        "text-[10px] font-bold text-gray-500 uppercase tracking-widest"
                    )
                    ui.label(str(player.days_survived)).classes(
                        "text-3xl font-black text-white leading-none"
                    )

                ui.separator().props("vertical").classes("bg-white/10 h-8")

                with ui.column().classes("gap-1"):
                    ui.badge(
                        player.company_type.name.upper(), color=theme["badge"]
                    ).classes("px-3 py-1 font-bold tracking-tighter")
                    ui.label(f"Evento {unique_seen}/{total_events}").classes(
                        "text-[10px] text-gray-400 font-mono"
                    )

            with ui.row().classes("items-center gap-2"):
                ui.button(
                    icon="menu",
                    on_click=lambda: ui.run_javascript(
                        'document.querySelector(".stats-sidebar").classList.toggle("open")'
                    ),
                ).props("flat round color=white").classes("lg:hidden")
                ui.button(icon="contrast", on_click=lambda: ui.run_javascript('document.body.classList.toggle("light-mode")')).props(
                    "flat round color=white"
                ).classes("hover:bg-white/10").tooltip("Toggle Dark/Light Mode")
                ui.button(icon="visibility", on_click=lambda: ui.run_javascript('document.body.classList.toggle("high-contrast")')).props(
                    "flat round color=white"
                ).classes("hover:bg-white/10").tooltip("Toggle High Contrast")
                ui.button(icon="help", on_click=show_help).props(
                    "flat round color=white"
                ).classes("hover:bg-white/10")
                ui.button(icon="hub", on_click=show_decision_graph).props(
                    "flat round color=blue"
                ).classes("hover:bg-blue-500/10")
                ui.button(icon="biotech", on_click=go_to_laboratory).props(
                    "flat round color=purple"
                ).classes("hover:bg-purple-500/10").tooltip("Laboratorio agenti")
                ui.button(icon="logout", on_click=exit_game).props(
                    "flat round color=red"
                ).classes("hover:bg-red-500/10")

        # Main area
        with ui.row().classes("w-full gap-6 items-start"):
            # Stats sidebar
            with (
                ui.card()
                .classes(
                    "w-full lg:w-80 p-6 gap-4 stats-sidebar-card stats-sidebar vn-card"
                )
                .props("flat")
            ):
                ui.label("STATISTICHE").classes(
                    "text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                )
                stats = pdata["stats"]

                # Radar chart
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
                        "indicator": [
                            {"name": r["name"], "max": 100} for r in radar_data
                        ],
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
                            "areaStyle": {"color": theme["accent"] + "40"},
                            "lineStyle": {"color": theme["accent"], "width": 2},
                            "itemStyle": {"color": theme["accent"]},
                        }
                    ],
                    "backgroundColor": "transparent",
                }
                ui.echart(radar_option).classes("w-full h-44")

                # Stat bars with pulse on critical
                render_stats_section(stats)

                # FAZIONI
                render_factions_section(pdata["factions"])

                # RELAZIONI con avatar
                render_relationships_section(pdata["npcs"])

                # ULTIME SCELTE
                if state.choice_history:
                    ui.separator().classes("my-3 bg-gray-700")
                    ui.label("ULTIME SCELTE").classes(
                        "text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                    )
                    for h in state.choice_history[-5:]:
                        cat_color = CAT_COLORS.get(h["category"], "#6b7280")
                        with ui.row().classes("items-center gap-1"):
                            ui.icon("circle", size="6px").style(f"color: {cat_color}")
                            ui.label(
                                h["text"][:40] + ("…" if len(h["text"]) > 40 else "")
                            ).classes("text-xs text-gray-400 truncate")

                # Personalità Manager
                mp = getattr(engine, "manager_personality", {})
                if mp:
                    ui.separator().classes("my-3 bg-gray-700")
                    ui.label("MANAGER").classes("text-sm font-bold text-gray-400 mb-1")
                    with ui.row().classes("items-center gap-1"):
                        ui.icon("person", size="14px").classes("text-gray-500")
                        ui.label(mp.get("type", "")).classes("text-xs text-gray-300")
                    ui.label(mp.get("description", "")).classes(
                        "text-[10px] text-gray-500 italic"
                    )

                # Fase Carriera
                phase = engine.get_career_phase()
                ui.separator().classes("my-3 bg-gray-700")
                ui.label("FASE").classes(
                    "text-xs font-bold text-gray-500 uppercase tracking-wider mb-1"
                )
                with ui.row().classes("items-center gap-1"):
                    ui.icon("timeline", size="14px").classes("text-gray-500")
                    ui.label(phase[1]).classes("text-xs text-gray-300")
                ui.label(phase[2]).classes("text-[10px] text-gray-500 italic")

                # STATO
                ui.separator().classes("my-3 bg-gray-700")
                ui.label("STATO").classes(
                    "text-xs font-bold text-gray-500 uppercase tracking-wider mb-2"
                )

                risk_critical = sum(1 for s in stats.values() if s <= 20) + (
                    1 if stats["stress"] >= 80 else 0
                )
                risk_warning = sum(
                    1 for s in stats.values() if 20 < s <= 35 or 65 <= s < 80
                )

                if not engine.player.is_alive:
                    risk_label = "Terminato"
                    risk_color = "text-gray-500"
                elif (
                    risk_critical >= 3 or stats["stress"] >= 85 or stats["health"] <= 15
                ):
                    risk_label = "Pericolo Imminente"
                    risk_color = "text-red-400 font-bold"
                elif risk_critical >= 1 or risk_warning >= 3:
                    risk_label = "Critico"
                    risk_color = "text-orange-400 font-bold"
                elif risk_warning >= 1:
                    risk_label = "Moderato"
                    risk_color = "text-yellow-400"
                else:
                    risk_label = "Stabile"
                    risk_color = "text-green-400"

                with ui.row().classes("items-center gap-2"):
                    state_img = state_icon(risk_label)
                    if not state_img:
                        state_img = state_icon(engine.player.status)
                    if state_img:
                        ui.image(state_img).style(
                            "width: 36px; height: 36px; border-radius: 6px"
                        )
                    ui.label(risk_label).classes(f"{risk_color} text-base")
                ui.linear_progress(
                    value=min(stats["stress"] / 100, 1.0),
                    size="sm",
                    show_value=False,
                    color="red"
                    if stats["stress"] > 65
                    else "orange"
                    if stats["stress"] > 40
                    else "green",
                ).classes("w-full mt-1")
                ui.label("Stress").classes("text-xs text-gray-500")

                danger_stats = []
                if stats["stress"] >= 75:
                    danger_stats.append("Stress: rischio burnout")
                if stats["health"] <= 25:
                    danger_stats.append("Salute: critica")
                if stats["energy"] <= 20:
                    danger_stats.append("Energia: esaurita")
                if stats["self_esteem"] <= 20:
                    danger_stats.append("Autostima: a terra")
                if stats["manager_rep"] <= 20:
                    danger_stats.append("Rep. Manager: rischio licenziamento")
                for msg in danger_stats[:2]:
                    ui.label(f"⚠ {msg}").classes("text-xs text-red-400 mt-1")

            # Event + Choices
            with ui.column().classes("flex-1 gap-6 min-w-0 fade-in"):
                # Mini-evento giornaliero
                if engine.current_mini_event:
                    mini_text, mini_effects = engine.current_mini_event
                    with (
                        ui.card()
                        .classes("w-full p-4 border-l-4 border-blue-500/50 vn-card")
                        .props("flat")
                    ):
                        with ui.row().classes("items-center justify-between"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("coffee", size="18px").classes("text-blue-400")
                                ui.label("DAILY ROUTINE").classes(
                                    "text-xs font-black text-blue-400 tracking-tighter"
                                )
                            with ui.row().classes("gap-1"):
                                for k, v in mini_effects.items():
                                    color = (
                                        "text-green-400" if v > 0 else "text-red-400"
                                    )
                                    sign = "+" if v > 0 else ""
                                    label = effect_label(k)[:6]
                                    ui.label(f"{label} {sign}{v}").classes(
                                        f"text-[10px] font-bold {color} px-1.5 py-0.5 rounded bg-black/20"
                                    )

                        ui.label(mini_text).classes(
                            "text-sm text-gray-300 italic mt-2 leading-relaxed"
                        )

                if event:
                    with ui.column().classes("w-full gap-2"):
                        with ui.row().classes("items-center justify-between"):
                            ui.badge(
                                event.category.replace("_", " ").upper(),
                                color="amber-9",
                            ).classes("px-3 py-1 text-[10px] font-bold tracking-widest")

                            with ui.row().classes("gap-2"):
                                if engine.real_cases_mode:
                                    ui.badge("CASO REALE", color="orange-10").classes(
                                        "px-2 py-0.5 text-[9px] font-black"
                                    )
                                if is_repeat:
                                    ui.label("🔄 DÉJÀ VU").classes(
                                        "text-[9px] text-gray-500 font-bold"
                                    )

                        # NPC portrait + narrative card (Visual Novel style)
                        npc_names = list(pdata["npcs"].keys())
                        npc_idx = (
                            (len(engine.history)) % max(len(npc_names), 1)
                            if npc_names
                            else 0
                        )
                        npc_trigger = npc_names[npc_idx] if npc_names else ""

                        with ui.row().classes("w-full gap-4 items-end"):
                            # NPC portrait
                            with ui.column().classes("items-center gap-1 shrink-0"):
                                nd = pdata["npcs"].get(npc_trigger, {})
                                nf = NPC_FACTION_MAP.get(npc_trigger, "")
                                nc = NPC_FACTION_COLORS.get(nf, "#6b7280")
                                portrait_url = npc_portrait(npc_trigger, nd)
                                with ui.element("div").classes("relative inline-block"):
                                    ui.image(portrait_url).style(
                                        f"border-color: {nc}; width: 80px; height: 80px; border-radius: 20px; border: 2px solid; object-fit: cover"
                                    ).classes("npc-portrait")
                                    # Emote bubble overlay
                                    if event.choices:
                                        emote_icon = EMOTE_ICONS.get(
                                            event.choices[0].category
                                        )
                                        if emote_icon:
                                            emote_url = (
                                                f"{GFX_PATH}/personaggi/{emote_icon}"
                                            )
                                            ui.image(emote_url).style(
                                                "width: 28px; height: 28px; position: absolute; top: -8px; right: -8px; border-radius: 50%; border: 2px solid rgba(0,0,0,0.5); background: rgba(0,0,0,0.6)"
                                            )
                                ui.label(npc_trigger.upper()).classes(
                                    "text-[9px] font-black text-gray-500 tracking-tighter"
                                )

                            # Narrative Card
                            with (
                                ui.card()
                                .classes(
                                    "flex-1 p-6 event-card vn-card-highlight min-h-[140px]"
                                )
                                .props("flat")
                            ):
                                with ui.row().classes("items-start gap-3"):
                                    ev_icon = event_icon(event)
                                    if ev_icon:
                                        ui.image(ev_icon).style(
                                            "width: 48px; height: 48px; border-radius: 8px; flex-shrink: 0"
                                        )
                                    narrative_container = ui.markdown("").classes(
                                        "narrative-text prose prose-invert max-w-none flex-1"
                                        " [&_strong]:text-blue-300 [&_strong]:font-bold typewriter-text"
                                    )
                                    # Typewriter effect
                                    ui.run_javascript(f"""
                                        (function() {{
                                            const text = {json.dumps(event.text)};
                                            const el = document.querySelector('.typewriter-text');
                                            if (!el) return;
                                            el.innerHTML = '';
                                            let i = 0;
                                            const speed = {state._reading_speed * 1000};
                                            if (speed <= 0) {{
                                                el.innerHTML = text;
                                                return;
                                            }}
                                            function type() {{
                                                if (i < text.length) {{
                                                    el.innerHTML = text.substring(0, i+1);
                                                    i++;
                                                    setTimeout(type, speed);
                                                }}
                                            }}
                                            type();
                                        }})();
                                    """)

                    n_choices = len(event.choices)
                    with ui.column().classes("w-full gap-3 mt-2"):
                        if n_choices > 1:
                            ui.label("PRENDI UNA DECISIONE").classes(
                                "text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1"
                            )

                    # Timer per scelte critiche (M12)
                    _timer_choice_idx = -1
                    if n_choices > 1:
                        _timer_choice_idx = random.randint(0, n_choices - 1)

                    # Track decision time (start counting from event render)
                    state._decision_start = __import__("time").time()

                    for i, choice in enumerate(event.choices):

                        def handle_choice_cb(idx=0, evt=None, ch=None):
                            return lambda: make_choice(idx, evt, ch)

                        timer_class = ""
                        if i == _timer_choice_idx and n_choices > 1:
                            timer_class = " timer-choice"

                        label = f"{chr(65 + i)}. {choice.text}"
                        if n_choices == 1:
                            label = "Continua →"

                        with (
                            ui.button(
                                on_click=handle_choice_cb(i, event, choice),
                            )
                            .classes(f"w-full choice-btn {timer_class} fade-in")
                            .props(
                                f"flat no-caps aria-label='Scelta {i + 1}: {choice.text}'"
                            )
                        ):
                            with ui.column().classes("w-full items-start gap-1"):
                                ui.label(label).classes("text-left")

                                # Effetti sempre visibili (chip) - Nascondi se è una 'grey choice'
                                if choice.effects and not getattr(choice, 'is_grey', False):
                                    with ui.row().classes("gap-1 mt-1 flex-wrap"):
                                        for ek, ev in list(choice.effects.items())[:4]:
                                            cls = "pos" if ev > 0 else "neg"
                                            sign = "+" if ev > 0 else ""
                                            ui.label(
                                                f"{effect_label(ek)}: {sign}{ev}"
                                            ).classes(f"effect-chip {cls}")
                                elif getattr(choice, 'is_grey', False):
                                    ui.label("???").classes("text-[10px] text-gray-600 italic")

                            # Timer su scelta critica
                            if i == _timer_choice_idx and n_choices > 1:
                                timer_id = f"timer_{uuid.uuid4().hex[:6]}"
                                ui.label().classes("timer-ring").props(f"id={timer_id}")
                                ui.run_javascript(f"""
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
                                """)

                            # Tooltip (M3) - Nascondi se è una 'grey choice'
                            if not getattr(choice, 'is_grey', False):
                                with ui.tooltip().classes(
                                    "p-2 bg-gray-800 border border-gray-600 rounded"
                                ):
                                    for effect_key, effect_val in choice.effects.items():
                                        sign = "+" if effect_val > 0 else ""
                                        ui.label(
                                            f"{effect_label(effect_key)}: {sign}{effect_val}"
                                        ).classes("text-xs font-mono")

    # Mobile bottom bar
    if state._layout_mode == "mobile":
        with ui.row().classes("w-full items-center justify-between mobile-bottom-bar"):
            with ui.row().classes("items-center gap-2"):
                ui.label("Giorno").classes(
                    "text-[9px] font-bold text-gray-500 uppercase tracking-widest"
                )
                ui.label(str(player.days_survived)).classes(
                    "text-lg font-black text-white"
                )
            with ui.row().classes("items-center gap-2"):
                ui.icon("speed", size="16px").classes(
                    "text-red-400"
                    if stats["stress"] > 65
                    else "text-yellow-400"
                    if stats["stress"] > 40
                    else "text-green-400"
                )
                ui.label(f"{stats['stress']}%").classes(
                    "text-xs font-bold font-mono text-gray-300"
                )
            with ui.row().classes("items-center gap-1"):
                ui.button(
                    icon="menu",
                    on_click=lambda: ui.run_javascript(
                        'document.querySelector(".stats-sidebar").classList.toggle("open")'
                    ),
                ).props("flat round color=white dense")
                ui.button(icon="help", on_click=show_help).props(
                    "flat round color=white dense"
                )
                ui.button(icon="hub", on_click=show_decision_graph).props(
                    "flat round color=blue dense"
                )
                ui.button(icon="logout", on_click=exit_game).props(
                    "flat round color=red dense"
                )


def render_reflection_dialog(deltas, category, choice_text, reflection_text=None):
    reflections = {
        "COMPLIANCE": "La **Compliance** (obbedienza) riduce il conflitto immediato ma erode l'integrità. In antropologia organizzativa, questo 'mimetismo' può proteggere nel breve termine ma porta all'alienazione dal proprio sé professionale.",
        "RESISTANCE": "La **Resistance** (resistenza) protegge l'identità e l'integrità, ma aumenta la visibilità e il rischio di sanzioni. È un atto di riappropriazione del potere individuale in contesti asimmetrici.",
        "NEGOTIATION": "La **Negotiation** (negoziazione) cerca un equilibrio precario. Richiede alto capitale relazionale e può essere interpretata come debolezza o come competenza politica a seconda della cultura aziendale.",
        "ESCAPE": "L' **Escape** (fuga/evitamento) è una strategia di preservazione dell'energia. Riduce l'impatto emotivo degli eventi ignorandone la fonte, ma non risolve le cause sistemiche del malessere."
    }

    with ui.dialog().props("persistent") as dialog, ui.card().classes("p-8 vn-card max-w-lg"):
        ui.label("MODALITÀ RIFLESSIONE").classes("text-[10px] font-black text-amber-400 tracking-[0.3em] mb-2")
        ui.label(f"Perché '{choice_text}'?").classes("text-xl font-bold mb-4")

        main_reflection = reflection_text or reflections.get(category, "Ogni scelta modella il tuo percorso nel sistema.")
        ui.markdown(main_reflection).classes("text-gray-300 italic mb-6")

        ui.label("IMPATTOSULLE STATISTICHE:").classes("text-[10px] font-bold text-gray-500 mb-2")
        with ui.row().classes("w-full gap-2 flex-wrap"):
            for key, delta in deltas.items():
                color = "text-green-400" if delta > 0 else "text-red-400"
                sign = "+" if delta > 0 else ""
                ui.badge(f"{effect_label(key)} {sign}{delta}", color="black").classes(f"{color} border border-white/10")

        ui.button("HO CAPITO", on_click=dialog.close).classes("w-full mt-8 bg-amber-600")
    dialog.open()

def render_tutorial():
    steps = [
        {
            "title": "Benvenuto in Burnout Simulator",
            "icon": "auto_awesome",
            "text": "Questa è una simulazione di antropologia organizzativa. <b>Ogni scelta conta:</b> le tue decisioni influenzeranno le tue statistiche, i rapporti con i colleghi e il finale della partita.",
        },
        {
            "title": "Le Statistiche",
            "icon": "query_stats",
            "text": "A sinistra trovi il <b>radar psicologico</b> e le barre numeriche. Tienile d'occhio: stress alto e salute bassa possono portare al burnout. Le barre pulsano quando sono in zona critica.",
        },
        {
            "title": "Fazioni e NPC",
            "icon": "groups",
            "text": "I tuoi colleghi appartengono a fazioni (Fedelissimi, Gruppo Silenzioso, Ribelli). Guadagnare o perdere fiducia con loro cambia il gioco. Ogni NPC ha un avatar colorato in base alla fazione.",
        },
        {
            "title": "Le Scelte",
            "icon": "ads_click",
            "text": "Le scelte mostrano gli effetti direttamente nel bottone (+/-). Su alcune scelte critiche parte un <b>timer di 15 secondi</b> per simulare la pressione lavorativa. Non farti prendere dal panico!",
        },
        {
            "title": "Pronto?",
            "icon": "rocket_launch",
            "text": "Ricorda: non esiste la scelta giusta. Esiste la scelta <b>coerente</b> con il tuo stile. Buona fortuna.",
        },
    ]
    if state._tutorial_step >= len(steps):
        return
    step = steps[state._tutorial_step]
    with ui.column().classes("tutorial-overlay fade-in"):
        with (
            ui.card()
            .classes("tutorial-card vn-card border-t-4 border-purple-500")
            .props("flat")
        ):
            ui.icon(step["icon"], size="48px").classes("text-purple-400 mb-4")
            ui.label(step["title"]).classes(
                "text-2xl font-black text-white mb-4 tracking-tight"
            )
            ui.html(step["text"]).classes(
                "text-base text-gray-300 leading-relaxed text-center"
            )

            with ui.row().classes("w-full items-center justify-center mt-8 gap-1"):
                for i in range(len(steps)):
                    color = (
                        "bg-purple-500" if i == state._tutorial_step else "bg-gray-700"
                    )
                    ui.html(f'<div class="w-2 h-2 rounded-full {color}"></div>')

            with ui.row().classes("justify-center gap-4 mt-8 w-full"):
                if state._tutorial_step > 0:
                    ui.button("INDIETRO", on_click=lambda: tutorial_prev()).props(
                        "flat"
                    ).classes("text-gray-500 font-bold")
                btn_label = (
                    "INIZIA ORA" if state._tutorial_step == len(steps) - 1 else "AVANTI"
                )
                ui.button(btn_label, on_click=tutorial_next).props(
                    "color=purple-10 elevation=0"
                ).classes("px-8 font-black rounded-xl")
