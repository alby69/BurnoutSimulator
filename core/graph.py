import json
from pathlib import Path
from collections import defaultdict

class DecisionGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(lambda: defaultdict(int))
        self.history = []

    def add_decision(self, event_id: str, choice_id: str, next_event_id: str = None):
        self.edges[event_id][choice_id] += 1
        self.history.append({
            "event_id": event_id,
            "choice_id": choice_id,
            "next_event_id": next_event_id
        })

    def get_weights(self):
        return {k: dict(v) for k, v in self.edges.items()}

    def export_graph(self, filepath: str):
        data = {
            "edges": self.get_weights(),
            "history": self.history
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def load_graph(self, filepath: str):
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.history = data.get("history", [])
                for event_id, choices in data.get("edges", {}).items():
                    for choice_id, weight in choices.items():
                        self.edges[event_id][choice_id] = weight
