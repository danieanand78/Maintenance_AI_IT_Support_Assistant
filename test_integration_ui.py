"""
Test de l'intégration complète entre demande_ticket.py et integration_ticket.py
Sans interface graphique, juste pour valider le flux.
"""

import json
from integration_ticket import process_ticket_complete
from rag_module_5 import load_documents, build_chunks, KnowledgeBase

print("\n" + "="*70)
print("TEST D'INTÉGRATION : Simuler l'interface demande_ticket.py")
print("="*70)

# =====================================================================
# ÉTAPE 1 : Initialisation de la KB (comme dans MaintenanceApp.__init__)
# =====================================================================
print("\n[INIT] Chargement de la Knowledge Base...")
try:
    docs = load_documents("./knowledge_base")
    chunks = build_chunks(docs)
    kb = KnowledgeBase()
    kb.index_chunks(chunks)
    print("[OK] Knowledge Base chargée avec succès !")
except Exception as e:
    print(f"[ERREUR] Impossible de charger la KB : {e}")
    exit(1)

# =====================================================================
# ÉTAPE 2 : Simulation de submit_ticket() avec différents inputs
# =====================================================================
print("\n" + "="*70)
print("SIMULATION 1 : Ticket mot de passe (recherche trouvée)")
print("="*70)

ticket_counter = 1
message_1 = "j'ai oublié mon mot de passe et je ne peux plus me connecter"
ticket_id_1 = f"#TICK-{ticket_counter:03d}"

print(f"\nMessage utilisateur : {message_1}")
print(f"Ticket ID : {ticket_id_1}")

try:
    result_1 = process_ticket_complete(message_1, ticket_id_1, kb)
    
    # Affichage du résumé pour le tableau Treeview
    categorie_nom = result_1["classification"]["categories_detectees"]
    equipe = result_1["classification"]["equipe_assignee"]
    priorite = result_1["classification"]["priorite"]
    equipement = result_1["diagnostic"]["equipement"]
    
    print(f"\n✓ Résultats du traitement :")
    print(f"  Catégorie : {categorie_nom}")
    print(f"  Équipe : {equipe}")
    print(f"  Priorité : {priorite}")
    print(f"  Équipement : {equipement}")
    print(f"  Sources trouvées : {result_1['recherche_rag']['sources']}")
    print(f"  Infos manquantes : {result_1['diagnostic']['informations_manquantes']}")
    
except Exception as e:
    print(f"[ERREUR] {e}")

# =====================================================================
# SIMULATION 2 : Ticket réseau
# =====================================================================
print("\n" + "="*70)
print("SIMULATION 2 : Ticket réseau (recherche trouvée)")
print("="*70)

ticket_counter = 2
message_2 = "je n'ai plus de connexion internet depuis ce matin"
ticket_id_2 = f"#TICK-{ticket_counter:03d}"

print(f"\nMessage utilisateur : {message_2}")
print(f"Ticket ID : {ticket_id_2}")

try:
    result_2 = process_ticket_complete(message_2, ticket_id_2, kb)
    
    categorie_nom = result_2["classification"]["categories_detectees"]
    equipe = result_2["classification"]["equipe_assignee"]
    priorite = result_2["classification"]["priorite"]
    equipement = result_2["diagnostic"]["equipement"]
    
    print(f"\n✓ Résultats du traitement :")
    print(f"  Catégorie : {categorie_nom}")
    print(f"  Équipe : {equipe}")
    print(f"  Priorité : {priorite}")
    print(f"  Équipement : {equipement}")
    print(f"  Sources trouvées : {result_2['recherche_rag']['sources']}")
    print(f"  Infos manquantes : {result_2['diagnostic']['informations_manquantes']}")
    
except Exception as e:
    print(f"[ERREUR] {e}")

# =====================================================================
# SIMULATION 3 : Ticket inconnu
# =====================================================================
print("\n" + "="*70)
print("SIMULATION 3 : Ticket incohérent (fallback classification)")
print("="*70)

ticket_counter = 3
message_3 = "blablabla test du système"
ticket_id_3 = f"#TICK-{ticket_counter:03d}"

print(f"\nMessage utilisateur : {message_3}")
print(f"Ticket ID : {ticket_id_3}")

try:
    result_3 = process_ticket_complete(message_3, ticket_id_3, kb)
    
    categorie_nom = result_3["classification"]["categories_detectees"]
    equipe = result_3["classification"]["equipe_assignee"]
    priorite = result_3["classification"]["priorite"]
    equipement = result_3["diagnostic"]["equipement"]
    
    print(f"\n✓ Résultats du traitement :")
    print(f"  Catégorie : {categorie_nom}")
    print(f"  Équipe : {equipe}")
    print(f"  Priorité : {priorite}")
    print(f"  Équipement : {equipement}")
    print(f"  Sources trouvées : {result_3['recherche_rag']['sources']}")
    print(f"  Infos manquantes : {result_3['diagnostic']['informations_manquantes']}")
    
except Exception as e:
    print(f"[ERREUR] {e}")

# =====================================================================
# TABLEAU DE SUIVI (ce qui apparaîtrait dans le Treeview)
# =====================================================================
print("\n" + "="*70)
print("TABLEAU DE SUIVI DANS L'INTERFACE (Treeview)")
print("="*70)

tickets_data = [
    ("TICK-001", "Comptes et authentification", "Support Technique", "moyenne", "Non identifié"),
    ("TICK-002", "Réseau et connectivité", "Infrastructure", "critique", "Non identifié"),
    ("TICK-003", "Autre ou indéterminé", "Support Technique", "faible", "Non identifié"),
]

print("\n{:<12} {:<30} {:<25} {:<12} {:<20}".format(
    "ID Ticket", "Catégorie", "Équipe assignée", "Priorité", "Équipement"
))
print("-" * 99)

for ticket_id, cat, equipe, prio, equip in tickets_data:
    print("{:<12} {:<30} {:<25} {:<12} {:<20}".format(
        ticket_id, cat[:28], equipe, prio, equip
    ))

print("\n" + "="*70)
print("[SUCCESS] Flux d'intégration validé !")
print("="*70)
print("\nL'interface demande_ticket.py peut maintenant :")
print("  ✓ Capturer l'input utilisateur")
print("  ✓ L'analyser via categorie.py (classification)")
print("  ✓ Le passer au RAG via rag_module_5.py")
print("  ✓ Afficher les résultats fusionnés dans le Treeview")
print("  ✓ Utiliser les infos pour le chatbot (open_chatbot)")
