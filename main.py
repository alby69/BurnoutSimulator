import sys
import os
from game.engine import GameEngine
from collections import Counter

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(engine):
    player = engine.player
    print("=" * 70)
    print(f" BURNOUT SIMULATOR - Giorno {player.days_survived}")
    print(f" AZIENDA: {player.company_type.upper()}")
    print("=" * 70)
    stats = player.to_dict()['stats']
    print(f" Energ: {stats['energy']}% | Stress: {stats['stress']}% | Salute: {stats['health']}%")
    print(f" Integ: {stats['integrity']}% | Autost: {stats['self_esteem']}% | Occup: {stats['employability']}%")
    print(f" Rep. Manager: {stats['manager_rep']}% | Rep. Team: {stats['team_rep']}%")
    print("-" * 70)

def print_relationships(player):
    print("\nRELAZIONI NPC:")
    for name, npc in player.npcs.items():
        print(f"- {name} ({npc.role}): Trust {npc.trust} | Respect {npc.respect} | Fear {npc.fear}")

    print("\nFAZIONI:")
    for faction, score in player.factions.items():
        print(f"- {faction}: {score}%")
    print("-" * 70)

def main():
    clear_screen()
    print("=" * 70)
    print("           BURNOUT SIMULATOR - ARCHETYPI AZIENDALI")
    print("=" * 70)
    print("Benvenuto. Scegli il tipo di azienda in cui inizierai il tuo percorso:")

    archetypes = list(GameEngine.COMPANY_ARCHETYPES.keys())
    for i, arch in enumerate(archetypes):
        desc = GameEngine.COMPANY_ARCHETYPES[arch]["description"]
        print(f"{i+1}) {arch}: {desc}")

    arch_choice = 0
    while arch_choice < 1 or arch_choice > len(archetypes):
        try:
            arch_input = input("\nScegli (1-4): ")
            arch_choice = int(arch_input)
        except ValueError:
            pass

    company_type = archetypes[arch_choice-1]
    player_name = input("\nInserisci il tuo nome: ") or "Impiegato Anonimo"

    engine = GameEngine(player_name, "game/data/events.json", company_type=company_type)

    exit_game = False
    while not engine.is_game_over() and not exit_game:
        event = engine.next_turn()
        if not event:
             break

        clear_screen()
        print_header(engine)
        print(f"CATEGORIA: {event.category.replace('_', ' ').upper()}")
        print(f"\n{event.text}\n")

        for i, choice in enumerate(event.choices):
            print(f"{i+1}) {choice.text}")

        print("\n0) Esci e vedi report finale")
        print("9) Vedi Relazioni e Fazioni")

        valid_choice = False
        while not valid_choice:
            try:
                choice_input = input("\nScegli un'opzione: ")
                if not choice_input:
                    continue
                choice_idx = int(choice_input)

                if choice_idx == 0:
                    print("Uscita in corso...")
                    valid_choice = True
                    exit_game = True
                    break

                if choice_idx == 9:
                    print_relationships(engine.player)
                    input("\nPremi invio per tornare all'evento...")
                    clear_screen()
                    print_header(engine)
                    print(f"CATEGORIA: {event.category.replace('_', ' ').upper()}")
                    print(f"\n{event.text}\n")
                    for i, choice in enumerate(event.choices):
                        print(f"{i+1}) {choice.text}")
                    print("\n0) Esci e vedi report finale")
                    print("9) Vedi Relazioni e Fazioni")
                    continue

                choice_idx -= 1
                if 0 <= choice_idx < len(event.choices):
                    engine.handle_choice(choice_idx)
                    valid_choice = True
                else:
                    print("Scelta non valida.")
            except ValueError:
                print("Inserisci un numero.")

    clear_screen()
    print("=" * 70)
    print("   REPORT FINALE SCIENTIFICO-ANTROPOLOGICO   ")
    print("=" * 70)

    # Complex Ending Determination
    p = engine.player
    ending = "IL SOPRAVVISSUTO"
    if p.status == "Promosso":
        ending = "IL POLITICO"
    elif p.status == "Promozione Tossica":
        ending = "IL CINICO"
    elif p.integrity >= 80 and p.manager_rep <= 30:
        ending = "IL MARTIRE"
    elif p.integrity <= 25:
        ending = "IL CINICO"
    elif p.employability >= 70 and p.is_alive:
        ending = "IL FUGGITIVO"
    elif p.manager_rep >= 70 and p.integrity >= 70:
        ending = "IL RIFORMATORE"
    elif "Burnout" in p.status:
        ending = "IL CADUTO"

    print(f"FINALE: {ending}")
    print(f"Stato Finale: {p.status}")
    print(f"Giorni in {p.company_type}: {p.days_survived}")
    print("-" * 70)

    # Behavioral Profile
    tags = p.tags
    total_tags = sum(tags.values())
    if total_tags > 0:
        print("PROFILO COMPORTAMENTALE:")
        for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True):
            perc = (count / total_tags) * 100
            print(f"- {tag:<15}: {perc:>3.1f}%")
        print("-" * 70)

    # Achievements
    if p.achievements:
        print("ACHIEVEMENT SBLOCCATI:")
        for ach in p.achievements:
            print(f"[*] {ach}")
        print("-" * 70)

    # Scientific Analysis
    print("ANALISI ANTROPOLOGICA:")
    if p.factions["Ribelli"] > 30:
        print("- Hai mostrato una forte tendenza alla resistenza attiva, prioritizzando l'integrità individuale.")
    if p.factions["Fedelissimi"] > 30:
        print("- Il tuo adattamento è stato di tipo opportunistico, integrando i valori dominanti dell'organizzazione.")
    if p.stress > 70:
        print("- L'esposizione prolungata a dinamiche tossiche ha eroso le tue barriere psicologiche (Burnout Alert).")

    print("-" * 70)
    save_path = engine.save_game()
    print(f"Sessione salvata: {save_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
