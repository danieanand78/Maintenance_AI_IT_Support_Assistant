from fastapi import FastAPI

from tools.users import rechercher_utilisateur
from tools.equipments import consulter_equipement
from tools.service import verifier_etat_service
from tools.incidents import rechercher_incidents_actifs
from tools.tickets import TicketCreate, creer_ticket, mettre_a_jour_ticket, affecter_ticket, escalader_vers_technicien

app = FastAPI(
    title="IT Support Backend"
)

@app.get("/")
def home():
    return {
        "message": "Backend fonctionne !"
    }



@app.put("/tools/tickets/update/{ticket_id}")
def update_ticket(ticket_id: str, updates: dict):
    return mettre_a_jour_ticket(ticket_id, updates)

@app.put("/tools/tickets/affecter/{ticket_id}")
def affect_ticket(ticket_id: str, tech_id: str):
    return affecter_ticket(ticket_id, tech_id)

@app.put("/tools/tickets/escalader/{ticket_id}")
def escalade_vers_technicien(ticket_id: str, tech_id: str):
    return escalader_vers_technicien(ticket_id, tech_id)

@app.get("/tools/users/search/{name}")
def search_user(name: str):
    return rechercher_utilisateur(name)

@app.get("/tools/equipment/{equipment_id}")
def get_equipment(equipment_id: str):
    return consulter_equipement(equipment_id)

@app.get("/tools/service/{service_name}")
def get_service(service_name: str):
    return verifier_etat_service(service_name)

@app.get("/tools/incidents/{incident_name}")
def get_incidents(incident_name: str):
    return rechercher_incidents_actifs(incident_name)