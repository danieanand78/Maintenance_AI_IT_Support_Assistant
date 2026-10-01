import json
import os
from datetime import datetime, timezone


LOG_DIR = "LOGS"
LOG_FILE = os.path.join(LOG_DIR, "logs.json")


def load_json_file(file_path):
    """Lit un fichier JSON et retourne son contenu."""

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_logs(logs):
    """Sauvegarde les logs."""

    os.makedirs(LOG_DIR, exist_ok=True)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2, ensure_ascii=False)


def load_logs():
    """Charge les anciens logs."""

    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def log_ticket_file(file_path):
    """
    Lit le résultat JSON produit par l'agent
    et l'ajoute au journal d'observabilité.
    """

    # Lire le résultat de l'agent
    analysis = load_json_file(file_path)

    # Créer l'événement
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "component": "agent",

        "action": "ticket_analysis",

        "result": analysis,

        "status": "success"
    }

    # Charger les anciens logs
    logs = load_logs()

    # Ajouter le nouvel événement
    logs.append(event)

    # Sauvegarder
    save_logs(logs)

    return event


if __name__ == "__main__":

    # Fichier produit par l'agent
    result_file = "resultat.json"

    event = log_ticket_file(result_file)

    print("Ticket enregistré avec succès.")
    print(json.dumps(event, indent=2, ensure_ascii=False))