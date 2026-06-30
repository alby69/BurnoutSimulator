import json
import random
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Choice:
    id: str
    text: str
    effects: Dict[str, int]
    category: str  # e.g., COMPLIANCE, RESISTANCE, NEGOTIATION, ESCAPE
    next_event_id: Optional[str] = None

@dataclass
class Event:
    id: str
    text: str
    category: str # toxic type
    choices: List[Choice]
    requirements: Optional[Dict[str, Dict[str, int]]] = None # e.g. {"mood": {"min": 0, "max": 30}}

class EventManager:
    def __init__(self, events_file: str):
        self.events = self.load_events(events_file)

    def load_events(self, events_file: str) -> Dict[str, Event]:
        with open(events_file, 'r') as f:
            data = json.load(f)

        events = {}
        for event_data in data:
            choices = [
                Choice(**choice_data) for choice_data in event_data['choices']
            ]
            events[event_data['id']] = Event(
                id=event_data['id'],
                text=event_data['text'],
                category=event_data['category'],
                choices=choices,
                requirements=event_data.get('requirements')
            )
        return events

    def get_event(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    def check_requirements(self, event: Event, player_stats: dict) -> bool:
        if not event.requirements:
            return True

        for stat, bounds in event.requirements.items():
            # For stats not in player_stats, we assume a default value of 0 for days_survived,
            # or 50 for others to avoid premature triggering of negative events
            default = 0 if stat == "days_survived" else 50
            val = player_stats.get(stat, default)

            if 'min' in bounds and val < bounds['min']:
                return False
            if 'max' in bounds and val > bounds['max']:
                return False
        return True

    def get_random_event(self, player_stats: dict, exclude_ids: List[str] = None) -> Event:
        available = [
            e for e in self.events.values()
            if e.id not in (exclude_ids or []) and self.check_requirements(e, player_stats)
        ]
        if not available:
            # Fallback to any event if requirements are too restrictive
            available = list(self.events.values())

        return random.choice(available)
