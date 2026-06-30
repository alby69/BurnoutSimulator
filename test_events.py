from game.events import EventManager
import os

def test_load_events():
    events_file = "game/data/events.json"
    if not os.path.exists(events_file):
        print("Events file not found!")
        return

    manager = EventManager(events_file)
    print(f"Loaded {len(manager.events)} events.")
    for eid, event in manager.events.items():
        print(f"Event: {eid} ({event.category})")
        for choice in event.choices:
            print(f"  - {choice.id}: {choice.category}")

if __name__ == "__main__":
    test_load_events()
