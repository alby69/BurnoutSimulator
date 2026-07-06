from nicegui import ui
import json
import os

def render_editor():
    """Visual Editor for narrative events."""
    events_path = "game/data/events.json"

    def load_events():
        try:
            with open(events_path, "r") as f:
                return json.load(f)
        except:
            return {"events": []}

    def save_events(data):
        with open(events_path, "w") as f:
            json.dump(data, f, indent=4)
        ui.notify("Eventi salvati con successo!", type="positive")

    events_data = load_events()

    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-6"):
        ui.label("EDITOR EVENTI NARRATIVI").classes("text-3xl font-black text-blue-400 mb-4")

        json_editor = ui.codemirror(json.dumps(events_data, indent=4), language="json").classes("w-full h-96 border border-white/10 rounded-xl")

        with ui.row().classes("w-full justify-between mt-4"):
            ui.button("Annulla", on_click=lambda: ui.navigate.to("/")).props("flat color=gray")
            ui.button("SALVA MODIFICHE", on_click=lambda: save_events(json.loads(json_editor.value))).props("color=blue").classes("px-8 py-2 font-bold")

        ui.markdown("""
        ### Istruzioni
        - Modifica il JSON direttamente nel box sopra.
        - Assicurati di mantenere la struttura valida (array di oggetti `events`).
        - Ogni evento deve avere `id`, `text`, `category` e `choices`.
        """).classes("text-sm text-gray-500 mt-8")
