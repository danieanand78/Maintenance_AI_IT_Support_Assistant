from utils.json_manager import load_json, save_json
from pydantic import BaseModel
from uuid import uuid4
class TicketCreate(BaseModel):
    user_id: str
    description: str
    category: str
    priority: str
    team: str


def mettre_a_jour_ticket(ticket_id: str, updates: dict):
    tickets = load_json("tickets.json")
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket.update(updates)
            save_json("tickets.json", tickets)
            return {
                "success": True,
                "ticket": ticket
            }
    return {
        "success": False,
        "error": "TICKET_NOT_FOUND"
    }


def affecter_ticket(ticket_id: str, technician_id: str):
    tickets = load_json("tickets.json")
    technicians = load_json("technician.json")
    technician = None

    for tech in technicians:
        if tech["id"] == technician_id:
            technician = tech
            break
    if technician is None:
        return {
            "success": False,
            "error": "TECHNICIAN_NOT_FOUND"
        }
    if technician["available"]=="Non":
        return {
            "success": False,
            "error": "TECHNICIAN_UNAVAILABLE"
        }
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["assigned_to"] = technician_id
            ticket["status"] = "in_progress"
            save_json("tickets.json", tickets)
            return {
                "success": True,
                "ticket": ticket
            }
    return {
        "success": False,
        "error": "TICKET_NOT_FOUND"
    }


def escalader_vers_technicien(ticket_id: str, technician_id: str):
    result = affecter_ticket(ticket_id, technician_id)
    if not result["success"]:
        return result
    tickets = load_json("tickets.json")
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = "escalated"
            save_json("tickets.json", tickets)
            return {
                "success": True,
                "ticket": ticket
            }