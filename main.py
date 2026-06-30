import sys
import os
import tkinter as tk
from game.gui import BurnoutGUI
from game.engine import GameEngine
from collections import Counter

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(player):
    print("=" * 60)
    print(f" BURNOUT SIMULATOR - Giorno {player.days_survived}")
    print("=" * 60)
    player_dict = player.to_dict()
    stats = player_dict['stats']
    print(f" Energ: {stats['energy']}% | Mood: {stats['mood']}% | Rep: {stats['reputation']}%")
    print(f" Paz: {stats['patience']}% | Prep: {stats['preparation']}% | Coll: {stats['collaboration']}%")
    rels = player_dict['relationships']
    print(f" Manager: {rels['Manager']} | Colleagues: {rels['Colleagues']} | HR: {rels['HR']}")
    print("-" * 60)

def run_cli():
    clear_screen()
    print("Benvenuto in Burnout Simulator (CLI Mode).")
    print("Un gioco di simulazione antropologica sulle dinamiche aziendali tossiche.")
    player_name = input("\nInserisci il tuo nome: ") or "Impiegato Anonimo"

    engine = GameEngine(player_name, "game/data/events.json")

    while not engine.is_game_over():
        event = engine.next_turn()
        clear_screen()
        print_header(engine.player)
        print(f"CATEGORIA TOSSICA: {event.category.replace('_', ' ').upper()}")
        print(f"\n{event.text}\n")

        for i, choice in enumerate(event.choices):
            print(f"{i+1}) {choice.text}")

        valid_choice = False
        while not valid_choice:
            try:
                choice_input = input("\nScegli un'opzione (o 0 per uscire): ")
                if not choice_input:
                    continue
                choice_idx = int(choice_input) - 1
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
    print(f"Titolo: {engine.player.get_behavioral_title()}")
    print(f"Giorni sopravvissuti: {engine.player.days_survived}")
    print("-" * 60)

    history = engine.graph.history
    if history:
        categories = []
        toxic_types = []
        for entry in history:
            event = engine.event_manager.get_event(entry['event_id'])
            toxic_types.append(event.category)
            for c in event.choices:
                if c.id == entry['choice_id']:
                    categories.append(c.category)

        prof_counts = Counter(categories)
        total = len(categories)
        print("PROFILO COMPORTAMENTALE:")
        for cat, count in prof_counts.items():
            perc = (count / total) * 100
            print(f"- {cat:<12}: {perc:>3.1f}%")

    save_path = engine.save_game()
    print(f"\nSessione salvata in: {save_path}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        try:
            root = tk.Tk()
            app = BurnoutGUI(root)
            root.mainloop()
        except Exception as e:
            print(f"Impossibile avviare la GUI: {e}")
            print("Avvio in modalità CLI...")
            run_cli()

if __name__ == "__main__":
    main()
