from nicegui import ui
import sqlite3, os, csv, io
from ui.theme import ARCHETYPE_THEMES, CAT_COLORS
from ui.pages.logic import play_again


def export_analytics_csv():
    """Esporta i dati delle sessioni in formato CSV."""
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "database", "analytics.db"
    )
    if not os.path.exists(db_path):
        ui.notify("Database non trovato", type="negative")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM sessions")
        rows = cur.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        # Header (basato sullo schema ipotizzato, andrebbe verificato nel file database/analytics.py)
        writer.writerow(
            [
                "session_id",
                "name",
                "company_type",
                "days_survived",
                "ending",
                "status",
                "created_at",
            ]
        )
        writer.writerows(rows)

        content = output.getvalue().encode("utf-8")
        ui.download(content, "burnout_analytics.csv")
        conn.close()
    except Exception as e:
        ui.notify(f"Errore export: {e}", type="negative")


def render_analytics():
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "database", "analytics.db"
    )
    with ui.column().classes("w-full max-w-4xl mx-auto"):
        with ui.row().classes("w-full items-center justify-between mb-4 pb-3 top-bar"):
            ui.label("📊 Dashboard Analytics").classes("text-2xl font-bold text-white")
            ui.button("← Torna al Menu", on_click=lambda: play_again()).props(
                "flat"
            ).classes("text-gray-400")

        if not os.path.exists(db_path):
            ui.label("Nessun dato analytics ancora disponibile.").classes(
                "text-gray-400"
            )
            return

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Finali più ottenuti
            cur.execute("""
                SELECT ending, COUNT(*) as cnt FROM sessions
                WHERE ending IS NOT NULL AND ending != ''
                GROUP BY ending ORDER BY cnt DESC LIMIT 10
            """)
            ending_data = cur.fetchall()

            # Scelte per categoria
            cur.execute("""
                SELECT category, COUNT(*) as cnt FROM choices
                GROUP BY category ORDER BY cnt DESC
            """)
            cat_data = cur.fetchall()

            # Sopravvivenza media per archetipo
            cur.execute("""
                SELECT company_type, ROUND(AVG(days_survived), 1) as avg_days,
                       COUNT(*) as sessions
                FROM sessions
                GROUP BY company_type ORDER BY avg_days DESC
            """)
            surv_data = cur.fetchall()

            # Totale sessioni
            cur.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cur.fetchone()[0]

            conn.close()
        except sqlite3.Error:
            ui.label("Errore lettura database.").classes("text-gray-400")
            return

        # Heatmap Scelte per Archetipo (Nuova Visualizzazione)
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT s.company_type, c.category, COUNT(*) as cnt
                FROM sessions s
                JOIN choices c ON s.session_id = c.session_id
                GROUP BY s.company_type, c.category
            """)
            heatmap_data = cur.fetchall()
            conn.close()

            if heatmap_data:
                archs = sorted(list(set(r[0] for r in heatmap_data)))
                cats = ["COMPLIANCE", "RESISTANCE", "NEGOTIATION", "ESCAPE"]

                # Prepara i dati per ECharts heatmap
                # Format: [arch_idx, cat_idx, value]
                data = []
                for arch_idx, arch in enumerate(archs):
                    for cat_idx, cat in enumerate(cats):
                        val = next(
                            (
                                r[2]
                                for r in heatmap_data
                                if r[0] == arch and r[1] == cat
                            ),
                            0,
                        )
                        data.append([arch_idx, cat_idx, val])

                heatmap_option = {
                    "title": {
                        "text": "Heatmap Strategie per Archetipo",
                        "textStyle": {"color": "#ccc", "fontSize": 12},
                        "left": "center",
                    },
                    "tooltip": {"position": "top"},
                    "grid": {"height": "70%", "top": "15%"},
                    "xAxis": {
                        "type": "category",
                        "data": archs,
                        "splitArea": {"show": True},
                    },
                    "yAxis": {
                        "type": "category",
                        "data": cats,
                        "splitArea": {"show": True},
                    },
                    "visualMap": {
                        "min": 0,
                        "max": max(r[2] for r in heatmap_data) if heatmap_data else 10,
                        "calculable": True,
                        "orient": "horizontal",
                        "left": "center",
                        "bottom": "0%",
                        "inRange": {"color": ["#111", "#3b82f6", "#ef4444"]},
                    },
                    "series": [
                        {
                            "name": "Scelte",
                            "type": "heatmap",
                            "data": data,
                            "label": {"show": True},
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                                }
                            },
                        }
                    ],
                    "backgroundColor": "transparent",
                }
                with (
                    ui.card().classes("w-full p-4 mt-4 vn-card").style("height: 350px")
                ):
                    ui.echart(heatmap_option)
        except Exception:
            pass

        with ui.grid(columns=2).classes("w-full gap-4"):
            with ui.card().classes("p-4 vn-card").props("flat tight"):
                ui.label("Finali più ottenuti").classes(
                    "text-sm font-bold text-gray-300 mb-2"
                )
                total = sum(r[1] for r in ending_data) or 1
                for name, cnt in ending_data:
                    perc = cnt / total * 100
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.label(name).classes("text-xs text-gray-400 flex-1")
                        ui.label(f"{cnt}").classes("text-xs font-mono text-gray-300")
                        ui.linear_progress(
                            value=perc / 100, size="xs", color="amber", show_value=False
                        ).classes("w-16")

            with ui.card().classes("p-4 vn-card").props("flat tight"):
                ui.label("Scelte per categoria").classes(
                    "text-sm font-bold text-gray-300 mb-2"
                )
                total_cat = sum(r[1] for r in cat_data) or 1
                for name, cnt in cat_data:
                    perc = cnt / total_cat * 100
                    cat_color = CAT_COLORS.get(name, "#6b7280")
                    with ui.row().classes("w-full items-center gap-2"):
                        ui.icon("circle", size="6px").style(f"color: {cat_color}")
                        ui.label(name).classes("text-xs text-gray-400 flex-1")
                        ui.label(f"{cnt}").classes("text-xs font-mono text-gray-300")
                        ui.linear_progress(
                            value=perc / 100, size="xs", color="amber", show_value=False
                        ).classes("w-16")

        # Tabella sopravvivenza
        with ui.card().classes("w-full p-4 mt-4 vn-card").props("flat"):
            ui.label(
                f"Sopravvivenza media per archetipo (totale: {total_sessions} partite)"
            ).classes("text-sm font-bold text-gray-300 mb-2")
            for arch, avg, sessions in surv_data:
                with ui.row().classes("w-full items-center gap-2"):
                    color = ARCHETYPE_THEMES.get(arch, {}).get("accent", "#6b7280")
                    ui.icon("circle", size="6px").style(f"color: {color}")
                    ui.label(arch).classes("text-xs text-gray-400 w-36")
                    ui.label(f"{avg} giorni").classes(
                        "text-xs font-mono text-gray-300 w-20"
                    )
                    ui.linear_progress(
                        value=min(float(avg) / 50, 1.0),
                        size="xs",
                        color="primary",
                        show_value=False,
                    ).classes("flex-1")
                    ui.label(f"({sessions} partite)").classes("text-xs text-gray-500")

        # Ultime partite
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT name, company_type, days_survived, ending, status
                FROM sessions ORDER BY rowid DESC LIMIT 10
            """)
            recent = cur.fetchall()
            conn.close()
        except sqlite3.Error:
            recent = []

        if recent:
            with ui.card().classes("w-full p-4 mt-4 vn-card").props("flat"):
                ui.label("Ultime partite").classes(
                    "text-sm font-bold text-gray-300 mb-2"
                )
                for name, arch, days, ending, status in recent:
                    with ui.row().classes(
                        "w-full items-center gap-2 border-b border-gray-800 pb-1"
                    ):
                        ui.label(name).classes("text-xs text-gray-300 w-24 truncate")
                        ui.label(arch).classes("text-xs text-gray-500 w-32")
                        ui.label(f"{days} gg").classes(
                            "text-xs font-mono text-gray-400 w-16"
                        )
                        ui.label(ending or "-").classes(
                            "text-xs text-yellow-400 flex-1"
                        )
                        ui.label(status or "-").classes("text-xs text-gray-500")
            ui.html("<br>")

        with ui.row().classes("w-full justify-center gap-4 mt-4 mb-12"):
            ui.button(
                "Esporta CSV", icon="download", on_click=export_analytics_csv
            ).props("color=blue flat")
            ui.button(
                "Gioca una partita", icon="play_arrow", on_click=play_again
            ).props("color=positive")
