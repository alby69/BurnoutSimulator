from dataclasses import dataclass, field

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

    def update_stats(self, effects: dict):
        for stat, value in effects.items():
            if hasattr(self, stat):
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
            "days_survived": self.days_survived,
            "status": self.status
        }
