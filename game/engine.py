from .player import Player
from .events import EventManager, Event, Choice
from .graph import DecisionGraph
from .save_manager import SaveManager
import random

MINI_EVENTS = [
    ("Trovi traffico, arrivi in ufficio già stressato.", {"stress": 3, "energy": -2}),
    ("Un collega ti offre un caffè e due parole di incoraggiamento.", {"energy": 3, "stress": -2}),
    ("Ricevi una notifica da un headhunter su LinkedIn.", {"employability": 5, "self_esteem": 3}),
    ("La macchinetta del caffè è rotta. Mattinata storta.", {"energy": -3, "stress": 2}),
    ("Un gatto randagio entra in ufficio e tutti si fermano 5 minuti.", {"stress": -3, "energy": 2}),
    ("Il PC si blocca proprio mentre stavi salvando il file.", {"stress": 4, "energy": -1}),
    ("Trovi un biglietto anonimo positivo sulla scrivania.", {"self_esteem": 5, "stress": -2}),
    ("L'ascensore è guasto, fai 8 piani a piedi.", {"energy": -2, "health": 1}),
    ("Il riscaldamento è rotto, si lavora col cappotto.", {"stress": 3, "energy": -3}),
    ("Una riunione viene cancellata all'ultimo minuto.", {"stress": -3, "energy": 1}),
    ("Oggi è il compleanno di un collega, c'è torta in ufficio.", {"stress": -3, "self_esteem": 2}),
    ("La connessione internet è lentissima tutto il giorno.", {"stress": 4, "energy": -2}),
    ("Trovi un parcheggio sotto ufficio, giornata comincia bene.", {"stress": -2, "energy": 1}),
    ("Il manager ti manda una mail alle 7:30 del mattino.", {"stress": 3, "self_esteem": -2}),
    ("La pausa pranzo si allunga perché si discute di film.", {"energy": 2, "stress": -2}),
]

NPC_FACTION_MAP = {
    "Marco": "Fedelissimi",
    "Giulia": "Fedelissimi",
    "Roberto": "Gruppo Silenzioso",
    "Elena": "Gruppo Silenzioso",
}


class GameEngine:
    COMPANY_ARCHETYPES = {
        "Startup Caotica": {
            "energy": 80,
            "stress": 20,
            "manager_rep": 60,
            "description": "Overwork, nessun processo, ritmi frenetici.",
            "hidden_vars": {"agility": 80, "stability": 20}
        },
        "Corporate Tossica": {
            "energy": 100,
            "stress": 10,
            "manager_rep": 50,
            "description": "Politica interna, micromanagement, burocrazia.",
            "hidden_vars": {"agility": 20, "stability": 80}
        },
        "Azienda Familiare": {
            "energy": 100,
            "stress": 5,
            "manager_rep": 40,
            "description": "Nepotismo, favoritismi, dinamiche 'da famiglia'.",
            "hidden_vars": {"loyalty": 90, "merit": 10}
        },
        "Consulting": {
            "energy": 70,
            "stress": 30,
            "manager_rep": 70,
            "description": "KPI ossessivi, disponibilità continua, orientamento al cliente.",
            "hidden_vars": {"pressure": 90, "prestige": 70}
        }
    }

    def __init__(self, player_name: str, events_file: str, company_type: str = "Corporate Tossica"):
        self.player = Player(name=player_name, company_type=company_type)
        self.apply_archetype(company_type)
        self.event_manager = EventManager(events_file)
        self.graph = DecisionGraph()
        self.save_manager = SaveManager()
        self.current_event = None
        self.next_event_id_override = None
        self.history = []
        self.hidden_vars = self.COMPANY_ARCHETYPES[company_type].get("hidden_vars", {}).copy()
        self.hidden_vars["manager_patience"] = 70
        self.hidden_vars["company_crisis"] = 10
        self.current_mini_event = None
        self._last_factions = dict(self.player.factions)
        self.deferred_events = []
        self._tutorial_step = 0

    def apply_archetype(self, archetype_name):
        if archetype_name in self.COMPANY_ARCHETYPES:
            arch = self.COMPANY_ARCHETYPES[archetype_name]
            self.player.energy = arch.get("energy", 100)
            self.player.stress = arch.get("stress", 0)
            self.player.manager_rep = arch.get("manager_rep", 50)

    def next_turn(self):
        self.player.days_survived += 1

        # Mini-evento giornaliero
        self.current_mini_event = random.choice(MINI_EVENTS)
        self.player.update_stats(self.current_mini_event[1])

        # Process deferred events
        deferred_override = None
        for d in self.deferred_events:
            d["due_in"] -= 1
            if d["due_in"] <= 0:
                deferred_override = d["event_id"]
        self.deferred_events = [d for d in self.deferred_events if d["due_in"] > 0]

        if deferred_override:
            self.current_event = self.event_manager.get_event(deferred_override)
        elif self.next_event_id_override:
            self.current_event = self.event_manager.get_event(self.next_event_id_override)
            self.next_event_id_override = None
        else:
            self.current_event = self.event_manager.get_random_event(exclude_ids=self.history[-10:])

        if self.current_event:
            self.history.append(self.current_event.id)
        return self.current_event

    def _sync_factions_to_npcs(self):
        p = self.player
        current = dict(p.factions)

        for faction, value in current.items():
            prev = self._last_factions.get(faction, value)
            if value == prev:
                continue
            delta = value - prev

            if faction == 'Fedelissimi':
                p.npcs['Marco'].trust = max(0, min(100, p.npcs['Marco'].trust + delta // 5))
                p.npcs['Marco'].respect = max(0, min(100, p.npcs['Marco'].respect + delta // 8))
                p.npcs['Giulia'].trust = max(0, min(100, p.npcs['Giulia'].trust + delta // 6))
                if value > 60:
                    p.npcs['Roberto'].respect = max(0, p.npcs['Roberto'].respect - delta // 10)

            elif faction == 'Ribelli':
                p.npcs['Marco'].trust = max(0, p.npcs['Marco'].trust - delta // 4)
                p.npcs['Giulia'].fear = max(0, min(100, p.npcs['Giulia'].fear + delta // 6))
                p.npcs['Roberto'].respect = max(0, min(100, p.npcs['Roberto'].respect + delta // 6))
                p.npcs['Elena'].trust = max(0, min(100, p.npcs['Elena'].trust + delta // 10))

            elif faction == 'Gruppo Silenzioso':
                p.npcs['Elena'].trust = max(0, min(100, p.npcs['Elena'].trust + delta // 8))
                p.npcs['Roberto'].trust = max(0, min(100, p.npcs['Roberto'].trust + delta // 10))

        self._last_factions = current

    def handle_choice(self, choice_index: int):
        if not self.current_event or choice_index >= len(self.current_event.choices):
            return False

        choice = self.current_event.choices[choice_index]

        # Update player stats
        self.player.update_stats(choice.effects)

        # Sincronizza fazioni → NPC
        self._sync_factions_to_npcs()

        if hasattr(choice, 'tags') and choice.tags:
            self.player.add_tags(choice.tags)

        self.graph.add_decision(self.current_event.id, choice.id, choice.next_event_id)

        if "manager_patience" in self.hidden_vars:
            if choice.category == "RESISTANCE":
                self.hidden_vars["manager_patience"] -= 5
            elif choice.category == "COMPLIANCE":
                self.hidden_vars["manager_patience"] += 2

        if random.random() < 0.1:
            self.hidden_vars["company_crisis"] += 5

        # Deferred consequences
        for con in choice.consequences:
            self.deferred_events.append({
                "event_id": con["event_id"],
                "due_in": con["after_turns"],
                "label": con.get("label", ""),
            })

        if choice.next_event_id:
            if "|" in choice.next_event_id:
                parts = choice.next_event_id.split("|")
                options = parts[1].split(";")
                choices_list = []
                weights = []
                for opt in options:
                    ev_id, weight = opt.split(":")
                    choices_list.append(ev_id)
                    weights.append(int(weight))
                self.next_event_id_override = random.choices(choices_list, weights=weights)[0]
            else:
                self.next_event_id_override = choice.next_event_id

        return True

    def is_game_over(self):
        return not self.player.is_alive

    def save_game(self):
        return self.save_manager.save_session(self.player, self.graph)
