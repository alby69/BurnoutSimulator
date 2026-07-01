from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class WorldSnapshot(BaseModel):
    timestamp: datetime
    agents_state: Dict[str, Any]
    global_metrics: Dict[str, float]
    active_events: List[Any]

class World:
    """Stato globale della simulazione"""
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.current_time = datetime.now()
        self.tick_interval = 1.0 # secondi
        self.global_metrics = {"well_being_aggregate": 1.0}

    def get_current_snapshot(self) -> WorldSnapshot:
        """Ritorna lo snapshot corrente del mondo"""
        return WorldSnapshot(
            timestamp=self.current_time,
            agents_state={aid: a.profile.model_dump() for aid, a in self.agents.items()},
            global_metrics=self.global_metrics,
            active_events=[]
        )

    def restore_from_snapshot(self, snapshot: WorldSnapshot):
        """Ripristina lo stato da uno snapshot"""
        self.current_time = snapshot.timestamp
        self.global_metrics = snapshot.global_metrics
        # TODO: Ripristinare stato agenti

    def tick(self):
        """Avanza la simulazione di un tick"""
        self.current_time += timedelta(seconds=self.tick_interval)
        # TODO: Evolvere stato agenti ed eventi
