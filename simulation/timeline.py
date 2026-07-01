from .world import World, WorldSnapshot
from typing import List, Optional
from datetime import datetime
import copy

class SimulationTimeline:
    """
    Timeline navigabile (play/pause/rewind)
    """
    def __init__(self, world: World):
        self.world = world
        self.snapshots: List[WorldSnapshot] = []
        self.current_index: int = -1

    def create_snapshot(self):
        snapshot = self.world.get_current_snapshot()
        self.snapshots.append(copy.deepcopy(snapshot))
        self.current_index = len(self.snapshots) - 1

    def step_backward(self, steps: int = 1):
        if not self.snapshots: return
        self.current_index = max(0, self.current_index - steps)
        self.world.restore_from_snapshot(self.snapshots[self.current_index])

    def step_forward(self, steps: int = 1):
        if self.current_index < len(self.snapshots) - 1:
            self.current_index = min(len(self.snapshots) - 1, self.current_index + steps)
            self.world.restore_from_snapshot(self.snapshots[self.current_index])
        else:
            # Se siamo alla fine, facciamo avanzare la simulazione
            for _ in range(steps):
                self.world.tick()
            self.create_snapshot()
