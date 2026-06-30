import sys
import os
from game.engine import GameEngine
from collections import Counter

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(player):
    print("=" * 60)
    print(f" BURNOUT SIMULATOR - Giorno {player.days_survived}")
    print("=" * 60)
    stats = player.to_dict()['stats']
    print(f" Energ: {stats['energy']}% | Rep: {stats['reputation']}% | Integ: {stats['integrity']}%")
    print(f" Stress: {stats['stress']}% | Occup: {stats['employability']}%")
    print("-" * 60)

def main():
    clear_screen()
    print("Benvenuto in Burnout Simulator.")
    print("Un gioco di simulazione antropologica sulle dinamiche aziendali tossiche.")
    player_name = input("\nInserisci il tuo nome: ") or "Impiegato Anonimo"

    engine = GameEngine(player_name, "game/data/events.json")

    exit_game = False
    while not engine.is_game_over() and not exit_game:
        event = engine.next_turn()
        if not event:
             break

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
                    valid_choice = True
                    exit_game = True
                    break

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

    # Analyze behavioral profile from TAGS
    tags = engine.player.tags
    total_tags = sum(tags.values())

    if total_tags > 0:
        print("PROFILO COMPORTAMENTALE (Basato sui Tag):")
        # Sort tags by frequency
        sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags:
            perc = (count / total_tags) * 100
            print(f"- {tag:<15}: {perc:>3.1f}% ({count})")
        print("-" * 60)

    # Analyze behavioral profile from CATEGORIES
    history = engine.graph.history
    if history:
        categories = []
        toxic_types = []
        for entry in history:
            event = engine.event_manager.get_event(entry['event_id'])
            if event:
                toxic_types.append(event.category)
                for c in event.choices:
                    if c.id == entry['choice_id']:
                        categories.append(c.category)

        prof_counts = Counter(categories)
        total_cat = len(categories)
        print("STRATEGIE DI SOPRAVVIVENZA:")
        for cat, count in prof_counts.items():
            perc = (count / total_cat) * 100
            print(f"- {cat:<12}: {perc:>3.1f}%")

        print("-" * 60)
        print("ANALISI TOSSICITÀ AFFRONTATA:")
        toxic_counts = Counter(toxic_types)
        for ttype, count in toxic_counts.items():
            print(f"- {ttype.replace('_', ' ').capitalize():<25}: {count} eventi")

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
