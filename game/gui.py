import tkinter as tk
from tkinter import ttk, messagebox
from .engine import GameEngine
from collections import Counter

class BurnoutGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Burnout Simulator - Corporate Anthropology")
        self.root.geometry("1100x800")
        self.root.configure(bg="#2c3e50")

        self.engine = None
        self.setup_start_screen()

    def setup_start_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="BURNOUT SIMULATOR", font=("Helvetica", 24, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=20)

        tk.Label(frame, text="Scegli il tipo di azienda:", font=("Helvetica", 12), fg="#bdc3c7", bg="#2c3e50").pack()
        self.arch_var = tk.StringVar(value="Corporate Tossica")
        archetypes = list(GameEngine.COMPANY_ARCHETYPES.keys())
        self.arch_menu = ttk.Combobox(frame, textvariable=self.arch_var, values=archetypes, state="readonly", width=30)
        self.arch_menu.pack(pady=10)

        tk.Label(frame, text="Inserisci il tuo nome:", font=("Helvetica", 12), fg="#bdc3c7", bg="#2c3e50").pack()
        self.name_entry = tk.Entry(frame, font=("Helvetica", 12), width=33)
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, "Impiegato Anonimo")

        tk.Button(frame, text="Inizia Avventura", command=self.start_game, font=("Helvetica", 12, "bold"),
                  bg="#27ae60", fg="white", padx=20, pady=10).pack(pady=20)

    def start_game(self):
        name = self.name_entry.get()
        arch = self.arch_var.get()
        self.engine = GameEngine(name, "game/data/events.json", company_type=arch)
        self.setup_game_screen()
        self.update_turn()

    def setup_game_screen(self):
        self.clear_screen()

        # Main container
        self.main_container = tk.Frame(self.root, bg="#2c3e50")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Panel: Stats
        self.left_panel = tk.Frame(self.main_container, bg="#34495e", width=300)
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))

        tk.Label(self.left_panel, text="STATISTICHE", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#34495e").pack(pady=10)

        self.stat_bars = {}
        stats_to_show = ["energy", "stress", "health", "integrity", "self_esteem", "employability", "manager_rep", "team_rep"]
        for stat in stats_to_show:
            frame = tk.Frame(self.left_panel, bg="#34495e")
            frame.pack(fill="x", padx=10, pady=2)
            tk.Label(frame, text=stat.replace('_', ' ').capitalize(), font=("Helvetica", 9), fg="#bdc3c7", bg="#34495e").pack(side="left")
            bar = ttk.Progressbar(frame, orient="horizontal", length=120, mode="determinate")
            bar.pack(side="right")
            self.stat_bars[stat] = bar

        # Factions
        tk.Label(self.left_panel, text="FAZIONI", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#34495e").pack(pady=(15, 5))
        self.faction_labels = {}
        for faction in ["Fedelissimi", "Gruppo Silenzioso", "Ribelli"]:
            label = tk.Label(self.left_panel, text=f"{faction}: 0%", font=("Helvetica", 9), fg="#bdc3c7", bg="#34495e")
            label.pack(anchor="w", padx=20)
            self.faction_labels[faction] = label

        # Relationships
        tk.Label(self.left_panel, text="RELAZIONI NPC", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#34495e").pack(pady=(15, 5))
        self.npc_labels = {}
        for npc in ["Marco", "Giulia", "Roberto", "Elena"]:
            label = tk.Label(self.left_panel, text=f"{npc}: Trust 50", font=("Helvetica", 9), fg="#bdc3c7", bg="#34495e")
            label.pack(anchor="w", padx=20)
            self.npc_labels[npc] = label

        # Right Panel: Events and Choices
        self.right_panel = tk.Frame(self.main_container, bg="#2c3e50")
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.info_label = tk.Label(self.right_panel, text="", font=("Helvetica", 12), fg="#f1c40f", bg="#2c3e50")
        self.info_label.pack(pady=(0, 5))

        self.day_label = tk.Label(self.right_panel, text="Giorno 1", font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.day_label.pack(pady=(0, 10))

        self.event_text = tk.Text(self.right_panel, font=("Helvetica", 13), wrap="word", height=10,
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
        if not event:
            self.show_game_over()
            return

        self.info_label.config(text=f"Azienda: {self.engine.player.company_type} | Categoria: {event.category.replace('_', ' ').upper()}")
        self.day_label.config(text=f"Giorno {self.engine.player.days_survived}")

        # Update Stats
        player_dict = self.engine.player.to_dict()
        stats = player_dict['stats']
        for stat, bar in self.stat_bars.items():
            bar['value'] = stats[stat]

        # Update Factions
        factions = player_dict['factions']
        for faction, label in self.faction_labels.items():
            label.config(text=f"{faction}: {factions[faction]}%")

        # Update NPCs
        npcs = player_dict['npcs']
        for npc_name, label in self.npc_labels.items():
            npc_data = npcs[npc_name]
            label.config(text=f"{npc_name}: T {npc_data['trust']} | R {npc_data['respect']} | F {npc_data['fear']}")

        # Update Event Text
        self.event_text.config(state="normal")
        self.event_text.delete(1.0, tk.END)
        self.event_text.insert(tk.END, event.text)
        self.event_text.config(state="disabled")

        # Update Choices
        for widget in self.choices_frame.winfo_children():
            widget.destroy()

        for i, choice in enumerate(event.choices):
            btn = tk.Button(self.choices_frame, text=f"{i+1}. {choice.text}", command=lambda idx=i: self.make_choice(idx),
                           font=("Helvetica", 11), bg="#34495e", fg="white", activebackground="#2980b9",
                           relief="flat", pady=10, anchor="w", padx=20)
            btn.pack(fill="x", pady=5)

    def make_choice(self, index):
        self.engine.handle_choice(index)
        self.update_turn()

    def show_game_over(self):
        self.clear_screen()
        player = self.engine.player

        # Determine Ending (re-using logic from main.py)
        ending = "IL SOPRAVVISSUTO"
        if player.status == "Promosso":
            ending = "IL POLITICO"
        elif player.status == "Promozione Tossica":
            ending = "IL CINICO"
        elif player.integrity >= 80 and player.manager_rep <= 30:
            ending = "IL MARTIRE"
        elif player.integrity <= 25:
            ending = "IL CINICO"
        elif player.employability >= 70 and player.is_alive:
            ending = "IL FUGGITIVO"
        elif player.manager_rep >= 70 and player.integrity >= 70:
            ending = "IL RIFORMATORE"
        elif "Burnout" in player.status:
            ending = "IL CADUTO"

        canvas = tk.Canvas(self.root, bg="#2c3e50", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        frame = tk.Frame(canvas, bg="#2c3e50")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="REPORT FINALE", font=("Helvetica", 24, "bold"), fg="#e74c3c", bg="#2c3e50").pack(pady=10)
        tk.Label(frame, text=f"ARCHETIPO: {ending}", font=("Helvetica", 18, "bold"), fg="#f1c40f", bg="#2c3e50").pack()
        tk.Label(frame, text=f"Stato: {player.status}", font=("Helvetica", 14), fg="#ecf0f1", bg="#2c3e50").pack(pady=5)
        tk.Label(frame, text=f"Giorni sopravvissuti: {player.days_survived}", font=("Helvetica", 12), fg="#bdc3c7", bg="#2c3e50").pack()

        # Tags analysis
        tags = player.tags
        total_tags = sum(tags.values())
        if total_tags > 0:
            tk.Label(frame, text="PROFILO COMPORTAMENTALE:", font=("Helvetica", 12, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(20, 5))
            for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    perc = (count/total_tags)*100
                    tk.Label(frame, text=f"{tag.replace('_', ' ').title()}: {perc:.1f}%", font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50").pack()

        # Achievements
        if player.achievements:
            tk.Label(frame, text="ACHIEVEMENTS:", font=("Helvetica", 12, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=(20, 5))
            for ach in player.achievements:
                tk.Label(frame, text=f"🏆 {ach}", font=("Helvetica", 10), fg="#f1c40f", bg="#2c3e50").pack()

        tk.Button(frame, text="Salva ed Esci", command=self.root.quit, bg="#27ae60", fg="white", font=("Helvetica", 12), padx=20, pady=10).pack(pady=30)
        self.engine.save_game()
