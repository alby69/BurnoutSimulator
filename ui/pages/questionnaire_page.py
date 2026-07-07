from nicegui import ui
import game.state as state
from database.analytics import record_questionnaire

MBI_QUESTIONS = [
    {"id": "q1", "text": "Mi sento emotivamente esaurito dal mio lavoro.", "category": "Esaurimento"},
    {"id": "q2", "text": "Mi sento logorato alla fine della giornata lavorativa.", "category": "Esaurimento"},
    {"id": "q3", "text": "Mi sento stanco quando mi alzo la mattina e devo affrontare un'altra giornata di lavoro.", "category": "Esaurimento"},
    {"id": "q4", "text": "Lavoro tutto il giorno con persone e questo mi richiede uno sforzo.", "category": "Esaurimento"},
    {"id": "q5", "text": "Sento di non poterne più del mio lavoro.", "category": "Esaurimento"},
    {"id": "q6", "text": "Sento che sto lavorando troppo duramente nel mio lavoro.", "category": "Esaurimento"},
    {"id": "q7", "text": "Mi sembra che lavorare con le persone tutto il giorno sia veramente faticoso.", "category": "Esaurimento"},
    {"id": "q8", "text": "Mi sento come se fossi alla fine delle mie forze.", "category": "Esaurimento"},
]

def render_questionnaire(q_type: str, on_complete):
    responses = {}

    with ui.column().classes("w-full max-w-2xl mx-auto p-8 gap-6 bg-slate-900 rounded-xl shadow-2xl"):
        title = "Questionario Pre-Partita" if q_type == "PRE" else "Questionario Post-Partita"
        ui.label(title).classes("text-3xl font-bold text-blue-400 text-center")

        ui.label("Per favore, rispondi a queste domande sulla base della tua esperienza attuale (o di come ti senti dopo il gioco).").classes("text-gray-300 italic text-center")

        with ui.scroll_area().classes("h-[500px] pr-4"):
            for q in MBI_QUESTIONS:
                with ui.column().classes("mb-6 p-4 bg-slate-800 rounded-lg"):
                    ui.label(q["text"]).classes("text-lg text-white mb-2")
                    responses[q["id"]] = ui.radio(
                        options={0: "Mai", 1: "Qualche volta l'anno", 2: "Una volta al mese", 3: "Qualche volta al mese", 4: "Una volta a settimana", 5: "Qualche volta a settimana", 6: "Ogni giorno"},
                        value=0
                    ).props("inline").classes("text-sm")

        def submit():
            final_responses = {q_id: r.value for q_id, r in responses.items()}
            score = sum(final_responses.values()) / len(MBI_QUESTIONS)
            record_questionnaire(state.session_id, q_type, final_responses, score)
            ui.notify("Risposte salvate, grazie!", type="positive")
            if q_type == "PRE":
                # For PRE, we need to pass back the temp data to on_start_cb
                name, arch, hr_params, skip_tutorial = state.temp_start_data
                on_complete(name, arch, hr_params, skip_tutorial=skip_tutorial)
            else:
                on_complete()

        ui.button("Invia e Prosegui", on_click=submit).classes("w-full py-4 text-xl bg-blue-600 hover:bg-blue-700")
