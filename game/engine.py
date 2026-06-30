from .player import Player
from .events import EventManager, Event, Choice
from .graph import DecisionGraph
from .save_manager import SaveManager
import random

class GameEngine:
    def __init__(self, player_name: str, events_file: str):
        self.player = Player(name=player_name)
        self.event_manager = EventManager(events_file)
        self.graph = DecisionGraph()
        self.save_manager = SaveManager()
        self.current_event = None
        self.next_event_id_override = None
        self.history = []

    def next_turn(self):
        self.player.days_survived += 1
        if self.next_event_id_override:
            self.current_event = self.event_manager.get_event(self.next_event_id_override)
            self.next_event_id_override = None
        else:
             # Exclude last 5 events to avoid repetition
             self.current_event = self.event_manager.get_random_event(exclude_ids=self.history[-5:])

        if self.current_event:
            self.history.append(self.current_event.id)
        return self.current_event

    def handle_choice(self, choice_index: int):
        if not self.current_event or choice_index >= len(self.current_event.choices):
            return False

        choice = self.current_event.choices[choice_index]

        # Update player stats
        self.player.update_stats(choice.effects)

        # Add tags to player
        if hasattr(choice, 'tags') and choice.tags:
            self.player.add_tags(choice.tags)

        # Record decision in graph
        self.graph.add_decision(self.current_event.id, choice.id, choice.next_event_id)

        # Handle random next_event_id if it's a list or similar (not implemented yet in JSON, but good to think about)
        # For now we use the one specified
        if choice.next_event_id:
            # If next_event_id is something like "EVENT_ID|RANDOM_CHANCE", we could handle it here
            if "|" in choice.next_event_id:
                parts = choice.next_event_id.split("|")
                # Example: "outcome_pos:50;outcome_neg:50"
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
