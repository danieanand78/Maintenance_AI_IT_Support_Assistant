from utils.json_manager import load_json


def verifier_etat_service(service_name: str):
    services = load_json("services.json")
    for service in services:
        if service["name"].lower() == service_name.lower():

            return {
                "success": True,
                "service": service
            }
    return {
        "success": False,
        "error": "SERVICE_NOT_FOUND",
        "message": f"Le service '{service_name}' n'existe pas"
    }