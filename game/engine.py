from .player import Player
from .events import EventManager, Event, Choice
from .graph import DecisionGraph
from .save_manager import SaveManager
import random

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

    def apply_archetype(self, archetype_name):
        if archetype_name in self.COMPANY_ARCHETYPES:
            arch = self.COMPANY_ARCHETYPES[archetype_name]
            self.player.energy = arch.get("energy", 100)
            self.player.stress = arch.get("stress", 0)
            self.player.manager_rep = arch.get("manager_rep", 50)

    def next_turn(self):
        self.player.days_survived += 1
        player_dict = self.player.to_dict()
        combined_stats = {
            **player_dict['stats'],
            **player_dict['factions'],
            "days_survived": self.player.days_survived
        }

        if self.player.stress > 80 and random.random() < 0.3:
            self.current_event = self.event_manager.get_event("burnout_warning") or self.event_manager.get_random_event(combined_stats, exclude_ids=self.history[-10:])
        elif self.next_event_id_override:
            self.current_event = self.event_manager.get_event(self.next_event_id_override)
            self.next_event_id_override = None
        else:
             self.current_event = self.event_manager.get_random_event(combined_stats, exclude_ids=self.history[-10:])

        if self.current_event:
            self.history.append(self.current_event.id)
        return self.current_event

    def handle_choice(self, choice_index: int):
        if not self.current_event or choice_index >= len(self.current_event.choices):
            return False

        choice = self.current_event.choices[choice_index]

        # Update player stats
        self.player.update_stats(choice.effects)

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
