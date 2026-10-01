from utils.json_manager import load_json


def rechercher_incidents_actifs(service_name: str):
    incidents = load_json("incidents.json")
    results = []
    for incident in incidents:
        if (
            incident["service"].lower() == service_name.lower()
            and incident["status"] == "active"
        ):
            results.append(incident)
    return {
        "success": True,
        "count": len(results),
        "incidents": results
    }