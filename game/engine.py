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
        self.history = []

    def next_turn(self):
        self.player.days_survived += 1
        if not self.current_event or not hasattr(self.current_event, 'next_event_id') or not self.current_event.next_event_id:
             self.current_event = self.event_manager.get_random_event(exclude_ids=self.history[-5:])
        else:
            self.current_event = self.event_manager.get_event(self.current_event.next_event_id)

        self.history.append(self.current_event.id)
        return self.current_event

    def handle_choice(self, choice_index: int):
        if not self.current_event or choice_index >= len(self.current_event.choices):
            return False

        choice = self.current_event.choices[choice_index]
        self.player.update_stats(choice.effects)
        self.graph.add_decision(self.current_event.id, choice.id, choice.next_event_id)

        # In a real graph, we might want to set the next event explicitly
        # But for now let's just use it if it exists in the next_turn logic
        self.current_event.next_event_id = choice.next_event_id

        return True

    def is_game_over(self):
        return not self.player.is_alive

    def save_game(self):
        return self.save_manager.save_session(self.player, self.graph)
