import json
import uuid
from pathlib import Path
from .player import Player
from .graph import DecisionGraph

class SaveManager:
    def __init__(self, sessions_dir: str = "game/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, player: Player, graph: DecisionGraph):
        session_id = f"{player.name}_{uuid.uuid4().hex[:8]}"
        filepath = self.sessions_dir / f"{session_id}.json"

        data = {
            "player": player.to_dict(),
            "graph": {
                "weights": graph.get_weights(),
                "history": graph.history
            }
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

        return filepath
