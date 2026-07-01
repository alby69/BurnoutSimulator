import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Choice:
    id: str
    text: str
    effects: Dict[str, int]
    category: str  # e.g., COMPLIANCE, RESISTANCE, NEGOTIATION, ESCAPE
    tags: List[str] = field(default_factory=list)
    next_event_id: Optional[str] = None
    consequences: List[Dict] = field(default_factory=list)

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
            choices = []
            for choice_data in event_data['choices']:
                # Extract tags if they exist, otherwise default to empty list
                tags = choice_data.get('tags', [])
                # Ensure all required fields for Choice dataclass are present
                c = Choice(
                        id=choice_data['id'],
                        text=choice_data['text'],
                        effects=choice_data['effects'],
                        category=choice_data['category'],
                        tags=tags,
                        next_event_id=choice_data.get('next_event_id'),
                        consequences=choice_data.get('consequences', [])
                    )
                choices.append(c)

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
