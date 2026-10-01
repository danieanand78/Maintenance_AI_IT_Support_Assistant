import json
import re
from typing import Dict, List, Any

CATEGORY_RULES = {
    "Comptes et authentification": {"equipe": "Support Technique", "priorite_defaut": "moyenne"},
    "Réseau et connectivité": {"equipe": "Infrastructure", "priorite_defaut": "critique"},
    "Matériel informatique": {"equipe": "IT", "priorite_defaut": "moyenne"},
    "Logiciels et applications": {"equipe": "Support Technique", "priorite_defaut": "moyenne"},
    "Imprimantes et périphériques": {"equipe": "IT", "priorite_defaut": "faible"},
    "Droits d'accès": {"equipe": "Administration Système", "priorite_defaut": "moyenne"},
    "Cybersécurité": {"equipe": "Sécurité", "priorite_defaut": "critique"},
    "Autre ou indéterminé": {"equipe": "Support Technique", "priorite_defaut": "faible"}
}

KEYWORDS_MAP = {
    "Comptes et authentification": ["authentification", "compte", "comptes", "mot de passe", "mdp"],
    "Réseau et connectivité": ["connexion", "reseau", "internet", "wifi", "e-mail", "mail", "base de données"],
    "Matériel informatique": ["ordinateur", "pc", "clavier", "ecran", "écran", "souris", "prise", "tour"],
    "Imprimantes et périphériques": ["imprimante", "impression", "casque", "scanner"],
    "Droits d'accès": ["droit d'accès", "acces", "accès", "habilitation"],
    "Cybersécurité": ["courriel suspect", "phishing", "poste compromis", "virus", "piratage"]
}

def step_1_collect_and_clean(raw_text: str) -> str:
    if not raw_text:
        return ""
    # Nettoyage simple et suppression des espaces superflus sans remplacer les mots aléatoirement
    return re.sub(r"\s+", " ", raw_text).strip()

def step_2_classify(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    matched_categories = []
    
    # Vérifie uniquement les mots-clés réellement présents dans le texte
    for cat, keywords in KEYWORDS_MAP.items():
        for kw in keywords:
            if kw in text_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                break

    if not matched_categories:
        matched_categories = ["Autre ou indéterminé"]

    primary_cat = matched_categories[0]
    config = CATEGORY_RULES.get(primary_cat, {"equipe": "Support Technique", "priorite_defaut": "faible"})
    
    return {
        "categorie": ", ".join(matched_categories),
        "equipe_assignee": config["equipe"],
        "priorite": config["priorite_defaut"]
    }

def step_3_extract_entities(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    equipments = ["souris", "casque", "imprimante", "clavier", "ecran", "écran", "ordinateur", "pc", "e-mail"]
    
    # Extrait uniquement les équipements explicitement trouvés dans le texte
    found_equipment = [eq for eq in equipments if eq in text_lower]

    return {
        "utilisateur": "Non spécifié",
        "equipement": ", ".join(found_equipment) if found_equipment else "Non identifié",
        "symptomes": text[:100],
        "moment_apparition": "Non spécifié",
        "impact_activite": "À évaluer",
        "manipulations_effectuees": []
    }

def step_4_detect_missing_info(entities: Dict[str, Any], text: str) -> List[str]:
    missing = []
    if "depuis" not in text.lower() and "matin" not in text.lower():
        missing.append("À quel moment précis l'incident est-il apparu ?")
    if not entities["manipulations_effectuees"]:
        missing.append("Avez-vous déjà effectué des manipulations ou redémarré l'appareil ?")
    return missing

def process_ticket(raw_ticket: str) -> str:
    cleaned_text = step_1_collect_and_clean(raw_ticket)
    classification = step_2_classify(cleaned_text)
    diagnostic = step_3_extract_entities(cleaned_text)
    missing_info = step_4_detect_missing_info(diagnostic, cleaned_text)
    
    confidence = 0.90 if not missing_info else 0.70
    action = "demande_information" if missing_info else "resolution"

    output_data = {
        "categorie": classification["categorie"],
        "priorite": classification["priorite"],
        "equipe_assignee": classification["equipe_assignee"],
        "confiance": confidence,
        "informations_manquantes": missing_info,
        "diagnostic_extrait": diagnostic,
        "action": action,
        "validation_humaine_requise": False,
        "sources": []
    }

    return json.dumps(output_data, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    import sys
    # Si un argument est passé en ligne de commande (ex: le message du ticket depuis Tkinter)
    if len(sys.argv) > 1:
        raw_ticket_message = sys.argv[1]
        resultat_json = process_ticket(raw_ticket_message)
        print(resultat_json)
    else:
        # Fallback si testé directement dans la console
        ticket_exemple = input("ticket : ")
        resultat_json = process_ticket(ticket_exemple)
        print("resultat")
        print(resultat_json)