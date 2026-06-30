import json
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
                choices=choices
            )
        return events

    def get_event(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    def get_random_event(self, exclude_ids: List[str] = None) -> Event:
        import random
        available = [e for e in self.events.values() if e.id not in (exclude_ids or [])]
        return random.choice(available) if available else random.choice(list(self.events.values()))
