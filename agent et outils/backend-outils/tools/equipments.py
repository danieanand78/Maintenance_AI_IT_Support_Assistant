from utils.json_manager import load_json


def consulter_equipement(equipment_id: str):
    equipment = load_json("equipment.json")
    for item in equipment:
        if item["id"] == equipment_id:
            return {
                "success": True,
                "equipment": item
            }
    return {
        "success": False,
        "error": "EQUIPMENT_NOT_FOUND",
        "message": f"L'équipement '{equipment_id}' n'existe pas"
    }