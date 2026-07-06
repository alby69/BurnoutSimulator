def determine_ending(player) -> str:
    endings = []

    # Finali basati sulle fazioni (priorità alta)
    if player.factions["Ribelli"] >= 70 and player.integrity >= 60:
        endings.append(("IL WHISTLEBLOWER", 7))
    if player.factions["Fedelissimi"] >= 70 and player.manager_rep >= 80:
        endings.append(("IL BRACCIO DESTRO", 7))
    if player.factions["Gruppo Silenzioso"] >= 70:
        endings.append(("LO SPETTATORE", 6))
    if all(v >= 50 for v in player.factions.values()):
        endings.append(("IL CAMALEONTE", 5))

    # Nuovi finali combinati (incrociano archetipo + profilo comportamentale)
    arch = player.company_type
    t = player.tags
    if arch == "Startup Caotica" and t.get("burnout_risk", 0) >= 5:
        endings.append(("IL FONDATORE ESAURITO", 6))
    if (
        arch == "Azienda Familiare"
        and t.get("truth_teller", 0) >= 5
        and player.manager_rep <= 30
    ):
        endings.append(("IL PECORA NERA", 6))
    if arch == "Consulting" and t.get("yes_man", 0) >= 10:
        endings.append(("L'INGRANAGGIO PERFETTO", 5))
    if player.energy <= 10 and player.days_survived >= 20:
        endings.append(("IL RESISTENTE", 4))
    if player.self_esteem >= 80 and player.is_alive:
        endings.append(("L'INDIOMABILE", 3))

    # Finali basati sullo stato
    if player.status == "Promosso":
        endings.append(("IL POLITICO", 4))
    elif player.status == "Promozione Tossica":
        endings.append(("IL CINICO", 4))
    elif player.status == "Licenziato":
        endings.append(("IL CINESE", 3))

    # Finali basati sulle statistiche
    if player.integrity >= 80 and player.manager_rep <= 30:
        endings.append(("IL MARTIRE", 3))
    if player.integrity <= 25:
        endings.append(("IL CINICO", 2))
    if player.employability >= 70 and player.is_alive:
        endings.append(("IL FUGGITIVO", 2))
    if player.manager_rep >= 70 and player.integrity >= 70:
        endings.append(("IL RIFORMATORE", 3))
    if "Burnout" in player.status:
        endings.append(("IL CADUTO", 4))

    if not endings:
        endings.append(("IL SOPRAVVISSUTO", 1))

    endings.sort(key=lambda x: x[1], reverse=True)
    return endings[0][0]
