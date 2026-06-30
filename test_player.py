from game.player import Player

def test_player_endings():
    # Test Burnout
    p1 = Player(name="Burnout Test", energy=5)
    p1.update_stats({"energy": -10})
    assert p1.status == "Burnout"
    print("Burnout condition passed.")

    # Test Fired
    p2 = Player(name="Fired Test", reputation=5)
    p2.update_stats({"reputation": -10})
    assert p2.status == "Fired"
    print("Fired condition passed.")

    # Test Quiet Quitting
    p3 = Player(name="Quiet Quitting Test", mood=15)
    p3.update_stats({"mood": -10})
    assert p3.status == "Quiet Quitting"
    print("Quiet Quitting condition passed.")

    # Test Promotion
    p4 = Player(name="Promotion Test", reputation=85, preparation=85)
    p4.update_stats({"reputation": 10})
    assert p4.status == "Promoted"
    print("Promotion condition passed.")

if __name__ == "__main__":
    test_player_endings()
