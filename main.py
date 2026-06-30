import sys
import os
from game.engine import GameEngine

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(player):
    print("=" * 60)
    print(f" BURNOUT SIMULATOR - Giorno {player.days_survived}")
    print("=" * 60)
    stats = player.to_dict()['stats']
    print(f" Energ: {stats['energy']}% | Mood: {stats['mood']}% | Rep: {stats['reputation']}%")
    print(f" Paz: {stats['patience']}% | Prep: {stats['preparation']}% | Coll: {stats['collaboration']}%")
    print("-" * 60)

def main():
    clear_screen()
    print("Benvenuto in Burnout Simulator.")
    print("Un gioco di simulazione antropologica sulle dinamiche aziendali tossiche.")
    player_name = input("\nInserisci il tuo nome: ") or "Impiegato Anonimo"

    engine = GameEngine(player_name, "game/data/events.json")

    while not engine.is_game_over():
        event = engine.next_turn()
        clear_screen()
        print_header(engine.player)
        print(f"EVENTO: {event.category.upper()}")
        print(f"\n{event.text}\n")

        for i, choice in enumerate(event.choices):
            print(f"{i+1}) {choice.text}")

        valid_choice = False
        while not valid_choice:
            try:
                choice_idx = int(input("\nScegli un'opzione (o 0 per uscire): ")) - 1
                if choice_idx == -1:
                    print("Uscita in corso...")
                    engine.save_game()
                    return

                if 0 <= choice_idx < len(event.choices):
                    engine.handle_choice(choice_idx)
                    valid_choice = True
                else:
                    print("Scelta non valida.")
            except ValueError:
                print("Inserisci un numero.")

    clear_screen()
    print("=" * 60)
    print("   PARTITA CONCLUSA   ")
    print("=" * 60)
    print(f"Risultato: {engine.player.status}")
    print(f"Giorni sopravvissuti: {engine.player.days_survived}")
    print("-" * 60)

    final_stats = engine.player.to_dict()['stats']
    for stat, val in final_stats.items():
        print(f"{stat.capitalize():<15}: {val}")

    print("-" * 60)
    save_path = engine.save_game()
    print(f"Sessione salvata in: {save_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
