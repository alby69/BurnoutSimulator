import tkinter as tk
from tkinter import ttk, messagebox
from .engine import GameEngine
from collections import Counter

class BurnoutGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Burnout Simulator - Corporate Anthropology")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")

        self.engine = None
        self.setup_start_screen()

    def setup_start_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="BURNOUT SIMULATOR", font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=20)
        tk.Label(frame, text="Inserisci il tuo nome:", font=("Helvetica", 12), fg="#bdc3c7", bg="#2c3e50").pack()

        self.name_entry = tk.Entry(frame, font=("Helvetica", 12), width=30)
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, "Impiegato Anonimo")

        tk.Button(frame, text="Inizia Avventura", command=self.start_game, font=("Helvetica", 12, "bold"),
                  bg="#27ae60", fg="white", padx=20, pady=10).pack(pady=20)

    def start_game(self):
        name = self.name_entry.get()
        self.engine = GameEngine(name, "game/data/events.json")
        self.setup_game_screen()
        self.update_turn()

    def setup_game_screen(self):
        self.clear_screen()

        # Main container
        self.main_container = tk.Frame(self.root, bg="#2c3e50")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Panel: Stats
        self.left_panel = tk.Frame(self.main_container, bg="#34495e", width=250)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))

        tk.Label(self.left_panel, text="STATISTICHE", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#34495e").pack(pady=10)

        self.stat_bars = {}
        for stat in ["energy", "mood", "reputation", "patience", "preparation", "collaboration"]:
            frame = tk.Frame(self.left_panel, bg="#34495e")
            frame.pack(fill="x", padx=10, pady=5)
            tk.Label(frame, text=stat.capitalize(), font=("Helvetica", 10), fg="#bdc3c7", bg="#34495e").pack(side="left")
            bar = ttk.Progressbar(frame, orient="horizontal", length=150, mode="determinate")
            bar.pack(side="right")
            self.stat_bars[stat] = bar

        # Relationships
        tk.Label(self.left_panel, text="RELAZIONI", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#34495e").pack(pady=(20, 10))
        self.rel_labels = {}
        for npc in ["Manager", "Colleagues", "HR"]:
            label = tk.Label(self.left_panel, text=f"{npc}: 0", font=("Helvetica", 10), fg="#bdc3c7", bg="#34495e")
            label.pack(anchor="w", padx=20)
            self.rel_labels[npc] = label

        # Right Panel: Events and Choices
        self.right_panel = tk.Frame(self.main_container, bg="#2c3e50")
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.day_label = tk.Label(self.right_panel, text="Giorno 1", font=("Helvetica", 16, "bold"), fg="#f1c40f", bg="#2c3e50")
        self.day_label.pack(pady=(0, 10))

        self.event_text = tk.Text(self.right_panel, font=("Helvetica", 13), wrap="word", height=8,
                                 bg="#ecf0f1", fg="#2c3e50", padx=15, pady=15)
        self.event_text.pack(fill="x", pady=10)
        self.event_text.config(state="disabled")

        self.choices_frame = tk.Frame(self.right_panel, bg="#2c3e50")
        self.choices_frame.pack(fill="both", expand=True)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def update_turn(self):
        if self.engine.is_game_over():
            self.show_game_over()
            return

        event = self.engine.next_turn()
        self.day_label.config(text=f"Giorno {self.engine.player.days_survived} - {event.category.replace('_', ' ').upper()}")

        # Update Stats
        stats = self.engine.player.to_dict()['stats']
        for stat, bar in self.stat_bars.items():
            bar['value'] = stats[stat]

        # Update Relationships
        rels = self.engine.player.relationships
        for npc, label in self.rel_labels.items():
            label.config(text=f"{npc}: {rels[npc]}")

        # Update Event Text
        self.event_text.config(state="normal")
        self.event_text.delete(1.0, tk.END)
        self.event_text.insert(tk.END, event.text)
        self.event_text.config(state="disabled")

        # Update Choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()

        for i, choice in enumerate(event.choices):
            btn = tk.Button(self.choices_frame, text=choice.text, command=lambda idx=i: self.make_choice(idx),
                           font=("Helvetica", 11), bg="#34495e", fg="white", activebackground="#2980b9",
                           relief="flat", pady=8, anchor="w", padx=20)
            btn.pack(fill="x", pady=5)

    def make_choice(self, index):
        self.engine.handle_choice(index)
        self.update_turn()

    def show_game_over(self):
        self.clear_screen()
        player = self.engine.player
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="PARTITA CONCLUSA", font=("Helvetica", 24, "bold"), fg="#e74c3c", bg="#2c3e50").pack(pady=10)
        tk.Label(frame, text=f"Stato Finale: {player.status}", font=("Helvetica", 16), fg="#ecf0f1", bg="#2c3e50").pack()
        tk.Label(frame, text=f"Titolo Ottenuto: {player.get_behavioral_title()}", font=("Helvetica", 14, "italic"), fg="#f1c40f", bg="#2c3e50").pack(pady=5)
        tk.Label(frame, text=f"Giorni sopravvissuti: {player.days_survived}", font=("Helvetica", 12), fg="#bdc3c7", bg="#2c3e50").pack()

        # Behavioral analysis
        history = self.engine.graph.history
        if history:
            tk.Label(frame, text="Profilo Comportamentale:", font=("Helvetica", 12, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(20, 5))
            categories = []
            for entry in history:
                evt = self.engine.event_manager.get_event(entry['event_id'])
                for c in evt.choices:
                    if c.id == entry['choice_id']:
                        categories.append(c.category)

            counts = Counter(categories)
            total = len(categories)
            for cat, count in counts.items():
                perc = (count/total)*100
                tk.Label(frame, text=f"{cat}: {perc:.1f}%", font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50").pack()

        tk.Button(frame, text="Salva ed Esci", command=self.root.quit, bg="#27ae60", fg="white", font=("Helvetica", 12), padx=20, pady=10).pack(pady=30)
        self.engine.save_game()

if __name__ == "__main__":
    root = tk.Tk()
    app = BurnoutGUI(root)
    root.mainloop()
