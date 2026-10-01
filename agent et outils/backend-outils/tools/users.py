from utils.json_manager import load_json


def rechercher_utilisateur(name: str):
    users = load_json("users.json")
    results = []
    for user in users:
        if name.lower() in user["name"].lower():
            results.append(user)

    if not results:
        return {
            "success": False,
            "error": "USER_NOT_FOUND",
            "message": f"Aucun utilisateur trouvé pour '{name}'"
        }
    return {
        "success": True,
        "results": results
    }