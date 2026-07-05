from typing import Dict, List, Any
import json

class StrategicAnalyzer:
    """
    Analizza il comportamento di un agente per generare report discorsivi
    sulle strategie adottate e sulla loro efficacia.
    """

    @staticmethod
    def analyze_agent(agent) -> Dict[str, Any]:
        memory = agent.memory
        decisions = memory.decisions
        if not decisions:
            return {"comment": "Nessuna decisione registrata per questo agente."}

        # 1. Distribuzione categorie
        cat_counts = memory.category_frequency
        total = sum(cat_counts.values())

        # 2. Analisi efficacia (stress delta medio per categoria)
        cat_efficiency = {}
        for cat in cat_counts:
            relevant_outcomes = [
                d.outcomes.get("stress_delta", 0)
                for d in decisions if d.category == cat and d.outcomes
            ]
            if relevant_outcomes:
                cat_efficiency[cat] = sum(relevant_outcomes) / len(relevant_outcomes)
            else:
                cat_efficiency[cat] = 0

        # 3. Identificazione strategia dominante
        dominant_cat = max(cat_counts, key=cat_counts.get)
        strategy_name = {
            "COMPLIANCE": "Adattamento Passivo",
            "RESISTANCE": "Opposizione Attiva",
            "NEGOTIATION": "Mediazione Strategica",
            "ESCAPE": "Evitamento Conservativo"
        }.get(dominant_cat, "Ibrida")

        # 4. Generazione commento discorsivo
        comment = StrategicAnalyzer._generate_discursive_comment(
            agent.name, strategy_name, dominant_cat, cat_counts, total, cat_efficiency, agent.profile
        )

        return {
            "strategy_name": strategy_name,
            "dominant_category": dominant_cat,
            "category_distribution": dict(cat_counts),
            "category_efficiency": cat_efficiency,
            "discursive_comment": comment,
            "total_days": agent.engine.player.days_survived if agent.engine else 0
        }

    @staticmethod
    def _generate_discursive_comment(name, strategy_name, dominant_cat, cat_counts, total, efficiency, profile) -> str:
        perc = (cat_counts[dominant_cat] / total) * 100

        intro = f"L'agente {name} ha adottato una strategia di **{strategy_name}**, basata per il {perc:.1f}% delle volte su scelte di {dominant_cat}. "

        if dominant_cat == "COMPLIANCE":
            if efficiency.get("COMPLIANCE", 0) > 0:
                body = "Questo approccio ha tentato di preservare la stabilità organizzativa a scapito del benessere individuale, accumulando stress residuo pur mantenendo alta la reputazione presso il management. "
            else:
                body = "Sorprendentemente, la sua conformità è stata premiata dal sistema, riuscendo a navigare le dinamiche tossiche senza un eccessivo logorio interno. "
        elif dominant_cat == "RESISTANCE":
            body = "Ha sfidato apertamente le dinamiche tossiche. Sebbene questo abbia preservato l'integrità e l'autostima, ha esposto l'agente a ritorsioni sistemiche e a un consumo accelerato di energia politica. "
        elif dominant_cat == "NEGOTIATION":
            body = "Ha cercato costantemente una 'terza via'. È un profilo che non accetta passivamente ma non rompe i ponti, ottimizzando il rapporto tra sforzo e rendimento reputazionale. "
        else: # ESCAPE
            body = "Ha operato in modalità 'disimpegno psicologico', cercando di ridurre al minimo i punti di contatto con la tossicità ambientale per pura sopravvivenza biologica. "

        # Influenza della personalità
        personality_impact = ""
        if profile.neuroticism > 60:
            personality_impact = "L'alto livello di nevroticismo ha reso ogni scelta più sofferta, amplificando l'impatto emotivo degli eventi negativi. "
        elif profile.agreeableness < 30:
            personality_impact = "Il basso livello di gradevolezza (cinismo emergente) ha facilitato decisioni distaccate, utili alla sopravvivenza in un ambiente ostile ma erosive per il tessuto sociale del team. "

        conclusion = "A posteriori, la sua 'dominanza' o sopravvivenza è dipesa dalla capacità di bilanciare le spinte del profilo psicologico con le richieste brutali dell'archetipo aziendale."

        return intro + body + personality_impact + conclusion
