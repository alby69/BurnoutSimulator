from nicegui import ui
from game.engine import GameEngine
from ui.theme import ARCHETYPE_THEMES
from ui.i18n import t, load_translations
import game.state as state

def render_start(on_start_cb, show_help, show_config, go_analytics):
    with ui.column().classes("w-full items-center justify-center min-h-[80vh] fade-in"):
        with (
            ui.card()
            .classes("w-full max-w-xl p-12 text-center vn-card vn-card-highlight mt-10")
            .props("flat")
        ):
            theme = ARCHETYPE_THEMES["Corporate Tossica"]
            ui.label("BURNOUT SIMULATOR").classes(
                "text-5xl font-black tracking-tighter mb-2"
            ).style(
                f"color: {theme['header']}; text-shadow: 0 0 30px {theme['accent']}60"
            )
            ui.label("Simulatore di Antropologia delle Organizzazioni").classes(
                "text-lg text-gray-400 mb-10 italic"
            )

            with ui.column().classes("w-full gap-6 items-center"):
                with ui.column().classes("w-full items-start"):
                    ui.label("ARCHETIPO AZIENDALE").classes(
                        "text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-1 ml-1"
                    )
                    arch_options = {
                        k: f"{k} — {v['description']}"
                        for k, v in GameEngine.COMPANY_ARCHETYPES.items()
                    }
                    arch_select = (
                        ui.select(
                            arch_options,
                            value="Corporate Tossica",
                        )
                        .classes("w-full")
                        .props("outlined standout dark color=blue")
                    )

                def on_arch_change():
                    t_theme = ARCHETYPE_THEMES.get(
                        arch_select.value, ARCHETYPE_THEMES["Corporate Tossica"]
                    )
                    ui.run_javascript(f"""
                        document.documentElement.style.setProperty('--theme-accent', '{t_theme["accent"]}');
                        document.documentElement.style.setProperty('--theme-header', '{t_theme["header"]}');
                        document.documentElement.style.setProperty('--theme-glow', '{t_theme["glow"]}');
                    """)

                arch_select.on("change", on_arch_change)

                with ui.column().classes("w-full items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10"):
                    ui.label("PARAMETRI HR (DSS)").classes(
                        "text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-1 ml-1"
                    )

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Tossicità Ambientale").classes("text-xs text-gray-300")
                        tox_slider = ui.slider(min=0, max=100, value=30).props("color=red-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Pressione Risorse").classes("text-xs text-gray-300")
                        res_slider = ui.slider(min=0, max=100, value=50).props("color=orange-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Coesione Sociale").classes("text-xs text-gray-300")
                        coh_slider = ui.slider(min=0, max=100, value=40).props("color=green-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Competizione Interna").classes("text-xs text-gray-300")
                        comp_slider = ui.slider(min=0, max=100, value=60).props("color=purple-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Supporto Sociale").classes("text-xs text-gray-300")
                        supp_slider = ui.slider(min=0, max=100, value=50).props("color=blue-5").classes("w-32")

                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Trasparenza Decisionale").classes("text-xs text-gray-300")
                        trans_slider = ui.slider(min=0, max=100, value=30).props("color=cyan-5").classes("w-32")

                with ui.row().classes(
                    "w-full items-center justify-between bg-white/5 p-4 rounded-xl border border-white/10 mt-2"
                ):
                    with ui.column().classes("gap-0"):
                        ui.label('Modalità "Casi Reali"').classes(
                            "text-sm font-bold text-gray-200"
                        )
                        ui.label("Eventi ispirati a storie vere").classes(
                            "text-[10px] text-gray-400"
                        )
                    real_cases_toggle = ui.switch().props("color=blue-4")

                with ui.row().classes(
                    "w-full items-center justify-between bg-white/5 p-3 rounded-xl border border-white/10 mt-2"
                ):
                    with ui.column().classes("gap-0"):
                        ui.label("Salta tutorial").classes(
                            "text-sm font-bold text-gray-200"
                        )
                        ui.label("Non mostrare le istruzioni iniziali").classes(
                            "text-[10px] text-gray-400"
                        )
                    skip_tutorial_toggle = ui.switch().props("color=purple-4")

            def start_lab_internal():
                hr_params = {
                    "toxicity": tox_slider.value,
                    "pressure": res_slider.value,
                    "cohesion": coh_slider.value,
                    "competition": comp_slider.value,
                    "social_support": supp_slider.value,
                    "transparency": trans_slider.value,
                    "real_cases": real_cases_toggle.value
                }
                on_start_cb("HR_Manager", arch_select.value, hr_params, go_to_lab=True, skip_tutorial=skip_tutorial_toggle.value)

            with ui.button(on_click=start_lab_internal).classes(
                "w-full mt-10 py-6 text-xl font-bold rounded-xl shadow-xl hover:scale-102 transition-transform bg-purple-600 text-white"
            ):
                with ui.row().classes("items-center gap-3 no-wrap"):
                    ui.icon("psychology", size="md")
                    ui.label("ENTRA NEL LABORATORIO")

            with ui.row().classes(
                "w-full justify-center mt-6 pt-6 border-t border-white/5 gap-3"
            ):
                ui.button(
                    "Analytics", on_click=lambda: go_analytics(), icon="insights"
                ).props("flat color=grey-5").classes("text-xs")
                ui.button("Editor", on_click=lambda: ui.navigate.to("/editor"), icon="edit").props(
                    "flat color=grey-5"
                ).classes("text-xs")
                ui.button("Help", on_click=show_help, icon="help").props(
                    "flat color=grey-5"
                ).classes("text-xs")
                ui.button(
                    "Config",
                    on_click=show_config,
                    icon="settings",
                ).props("flat color=grey-5").classes("text-xs")

                with ui.row().classes("gap-1 items-center ml-4"):
                    ui.button("IT", on_click=lambda: (load_translations("it"), ui.navigate.to("/"))).props("flat dense color=blue size=sm").classes("text-[10px]")
                    ui.label("|").classes("text-gray-700")
                    ui.button("EN", on_click=lambda: (load_translations("en"), ui.navigate.to("/"))).props("flat dense color=blue size=sm").classes("text-[10px]")
