from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Player:
    name: str
    patience: int = 50
    preparation: int = 50
    collaboration: int = 50
    mood: int = 50
    energy: int = 100
    reputation: int = 30
    assertiveness: int = 30
    resilience: int = 50
    days_survived: int = 0
    is_alive: bool = True
    status: str = "Active"

    # NPC Relationships: Stat from -100 to 100
    relationships: Dict[str, int] = field(default_factory=lambda: {
        "Manager": 0,
        "Colleagues": 0,
        "HR": 0
    })

    def update_stats(self, effects: dict):
        for stat, value in effects.items():
            if stat.startswith("rel_"):
                npc_raw = stat.split("_")[1]
                # Map specific keys to their display names
                mapping = {
                    "manager": "Manager",
                    "colleagues": "Colleagues",
                    "hr": "HR"
                }
                npc = mapping.get(npc_raw.lower(), npc_raw.capitalize())

                if npc in self.relationships:
                    self.relationships[npc] = max(-100, min(100, self.relationships[npc] + value))
            elif hasattr(self, stat):
                current_val = getattr(self, stat)
                setattr(self, stat, max(0, min(100, current_val + value)))

        self.check_conditions()

    def check_conditions(self):
        if self.energy <= 0:
            self.is_alive = False
            self.status = "Burnout"
        elif self.reputation <= 0:
            self.is_alive = False
            self.status = "Fired"
        elif self.mood <= 10:
            self.is_alive = False
            self.status = "Quiet Quitting"
        elif self.reputation >= 90 and self.preparation >= 80:
            self.is_alive = False
            self.status = "Promoted"
        elif self.days_survived >= 365:
            self.is_alive = False
            self.status = "Survived"

    def get_behavioral_title(self):
        # Logic to return a title based on stats
        if self.assertiveness > 70:
            return "The Disruptor"
        if self.patience > 80:
            return "The Martyr"
        if self.reputation > 80 and self.collaboration > 80:
            return "The Corporate Star"
        return "Standard Employee"

    def to_dict(self):
        return {
            "name": self.name,
            "stats": {
                "patience": self.patience,
                "preparation": self.preparation,
                "collaboration": self.collaboration,
                "mood": self.mood,
                "energy": self.energy,
                "reputation": self.reputation,
                "assertiveness": self.assertiveness,
                "resilience": self.resilience
            },
            "relationships": self.relationships,
            "days_survived": self.days_survived,
            "status": self.status,
            "title": self.get_behavioral_title()
        }
