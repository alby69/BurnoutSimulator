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
    is_grey: bool = False
    reflection: Optional[str] = None

@dataclass
class Event:
    id: str
    text: str
    category: str # toxic type
    choices: List[Choice]
    conditions: List[Dict] = field(default_factory=list) # e.g. [{"stat": "stress", "op": ">", "value": 50}]
    variants: List[Dict] = field(default_factory=list) # [{id: 'v1', text: '...', choices: [...]}]

class EventManager:
    def __init__(self, events_file: str):
        self.events = self.load_events(events_file)

    def load_events(self, events_file: str) -> Dict[str, Event]:
        with open(events_file, 'r') as f:
            data = json.load(f)

        events = {}
        for event_data in data:
            events[event_data['id']] = self._parse_event(event_data)
        return events

    def _parse_event(self, event_data: Dict) -> Event:
        choices = []
        for choice_data in event_data['choices']:
            choices.append(self._parse_choice(choice_data))

        return Event(
            id=event_data['id'],
            text=event_data['text'],
            category=event_data['category'],
            choices=choices,
            conditions=event_data.get('conditions', []),
            variants=event_data.get('variants', [])
        )

    def _parse_choice(self, choice_data: Dict) -> Choice:
        return Choice(
            id=choice_data['id'],
            text=choice_data['text'],
            effects=choice_data['effects'],
            category=choice_data['category'],
            tags=choice_data.get('tags', []),
            next_event_id=choice_data.get('next_event_id'),
            consequences=choice_data.get('consequences', []),
            is_grey=choice_data.get('is_grey', False),
            reflection=choice_data.get('reflection')
        )

    def get_event(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    def get_random_event(self, exclude_ids: List[str] = None, player=None) -> Event:
        import random
        available = [e for e in self.events.values() if e.id not in (exclude_ids or [])]

        if player:
            filtered = []
            for e in available:
                if not e.conditions:
                    filtered.append(e)
                    continue

                # Check conditions
                match = True
                for c in e.conditions:
                    stat_val = getattr(player, c["stat"], None)
                    if stat_val is None:
                        # try factions
                        if c["stat"].startswith("faction_"):
                            f_name = c["stat"].replace("faction_", "")
                            stat_val = player.factions.get(f_name)

                    if stat_val is None:
                        match = False
                        break

                    op = c["op"]
                    val = c["value"]
                    if op == ">" and not (stat_val > val): match = False
                    elif op == "<" and not (stat_val < val): match = False
                    elif op == ">=" and not (stat_val >= val): match = False
                    elif op == "<=" and not (stat_val <= val): match = False
                    elif op == "==" and not (stat_val == val): match = False

                    if not match: break

                if match:
                    filtered.append(e)

            if filtered:
                return random.choice(filtered)

        return random.choice(available) if available else random.choice(list(self.events.values()))
