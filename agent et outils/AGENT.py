from tools import input_validator
import requests

import subprocess
import sys
import time

BACKEND_URL = "http://127.0.0.1:8000"
Tools = {
    
    "update_ticket":{
        "method": "PUT",
        "endpoint": "/tools/tickets/update/{ticket_id}"
    },

    "affect_ticket":{
        "method": "PUT",
        "endpoint": "/tools/tickets/affecter/{ticket_id}"
    },

    "escalader_ticket":{
        "method": "PUT",
        "endpoint": "/tools/tickets/escalader/{ticket_id}"
    },

    "rechercher_utilisateur":{
        "method": "GET",
        "endpoint": "/tools/users/search/{name}"
    },

    "rechercher_equipement":{
        "method": "GET",
        "endpoint": "/tools/equipment/{equipment_id}"
    },

    "rechercher_service":{
        "method": "GET",
        "endpoint": "/tools/service/{service_name}"
    },
    "rechercher_incident":{
        "method": "GET",
        "endpoint": "/tools/incidents/{service_name}"
    }
}

def use_tool(tool_name, **kwargs):
    if tool_name not in Tools:
        raise ValueError(f"Outil inconnu : {tool_name}")
    tool = Tools[tool_name]
    method = tool["method"]
    endpoint = tool["endpoint"]
    # Remplace les paramètres dans l'URL
    endpoint = endpoint.format(**kwargs)
    url = BACKEND_URL + endpoint
    # Données envoyées dans le body
    data = kwargs.get("data")
    response = requests.request(
        method=method,
        url=url,
        json=data,
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def start_backend():
    process = subprocess.Popen([
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
    ])
    time.sleep(2)
    return process



def main():
    backend_process = start_backend()
    try:
        user_input = input("Votre demande : ")
        security = input_validator.run(user_input)
        print("\n--- SECURITY ANALYSIS ---")
        print("Risk level :", security["risk_level"])
        print("Score      :", security["score"])
        if security["reasons"]:
            print("Reasons    :", security["reasons"])
        if security["risk_level"] in ["HIGH_RISK", "BLOCK"]:
            print("\n❌ Entrée bloquée.")
            return
        print("\n✅ Entrée acceptée.")
        # Ton agent IA viendra ici

        result = use_tool("rechercher_utilisateur", name="jean")
        print(result)
    finally:
        backend_process.terminate()
        backend_process.wait()

if __name__ == "__main__":
    main()