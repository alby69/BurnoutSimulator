from game.engine import GameEngine
import os
import shutil

def test_full_simulation():
    # Setup
    if os.path.exists("game/sessions"):
        shutil.rmtree("game/sessions")
    os.makedirs("game/sessions")

    engine = GameEngine("Test Player", "game/data/events.json")

    # Simulate a few turns
    max_turns = 100
    turns = 0
    while not engine.is_game_over() and turns < max_turns:
        event = engine.next_turn()
        # Always pick the first choice
        engine.handle_choice(0)
        turns += 1

    print(f"Simulation finished after {turns} turns.")
    print(f"Final Status: {engine.player.status}")
    print(f"Final Energy: {engine.player.energy}")

    save_path = engine.save_game()
    print(f"Save created at: {save_path}")

    assert os.path.exists(save_path), "Save file was not created"

    # Verify contents of the save file
    import json
    with open(save_path, 'r') as f:
        data = json.load(f)
        assert data['player']['name'] == "Test Player"
        assert len(data['graph']['history']) > 0
        print("Save file content verified.")

if __name__ == "__main__":
    test_full_simulation()
