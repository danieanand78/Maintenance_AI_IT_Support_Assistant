"""
Intégration entre categorie.py et rag_module_5.py

Pipeline complet :
1. Utilisateur soumet une requête brute
2. categorie.py → Classification et extraction d'infos
3. rag_module_5.py → Recherche filtrée par catégorie
4. Résultat enrichi pour l'Agent (Personne 3)
"""

import json
from typing import Dict, Any

from categorie import process_ticket, CATEGORY_RULES
from rag_module_5 import load_documents, build_chunks, KnowledgeBase, search_with_log


def process_ticket_complete(raw_ticket: str, ticket_id: str, kb: KnowledgeBase) -> Dict[str, Any]:
    """
    Pipeline complet d'un ticket :
    1. Classification par categorie.py
    2. Recherche RAG filtrée par categorie.py's output
    3. Fusion des résultats
    
    Args:
        raw_ticket: Message brut de l'utilisateur
        ticket_id: ID unique du ticket (ex: "T-001")
        kb: Instance KnowledgeBase déjà indexée
    
    Returns:
        Dict fusionné avec :
        - Infos de classification (categorie, equipe, priorite)
        - Infos de recherche RAG (passages, sources)
        - Infos diagnostiques (équipement, symptômes, infos manquantes)
    """
    
    # =====================================================================
    # ÉTAPE 1 : Classification par categorie.py
    # =====================================================================
    classification_json = process_ticket(raw_ticket)
    classification = json.loads(classification_json)
    
    print("\n" + "="*70)
    print("ÉTAPE 1 : Classification (categorie.py)")
    print("="*70)
    print(json.dumps(classification, ensure_ascii=False, indent=2))
    
    # Extraction de la catégorie primaire (prendre la première si multiples)
    categorie_str = classification["categorie"]
    categories_list = [c.strip() for c in categorie_str.split(",")]
    primary_category = categories_list[0]
    
    print(f"\n[OK] Catégorie primaire détectée : {primary_category}")
    print(f"[OK] Équipe assignée : {classification['equipe_assignee']}")
    print(f"[OK] Priorité : {classification['priorite']}")
    
    # =====================================================================
    # ÉTAPE 2 : Recherche RAG filtrée par catégorie
    # =====================================================================
    print("\n" + "="*70)
    print("ÉTAPE 2 : Recherche RAG (rag_module_5.py)")
    print("="*70)
    
    result, log_entry = search_with_log(
        kb,
        query=raw_ticket,
        ticket_id=ticket_id,
        k=3,
        categorie=primary_category  # ← Filtre par catégorie détectée
    )
    
    print(f"[OK] Sources trouvées : {result['sources']}")
    print(f"[OK] Found : {result['found']}")
    
    # =====================================================================
    # ÉTAPE 3 : Fusion des résultats
    # =====================================================================
    print("\n" + "="*70)
    print("ÉTAPE 3 : Résultat fusionné")
    print("="*70)
    
    merged_result = {
        # === Classification (Personne 1)
        "ticket_id": ticket_id,
        "classification": {
            "categories_detectees": classification["categorie"],
            "categorie_primaire": primary_category,
            "equipe_assignee": classification["equipe_assignee"],
            "priorite": classification["priorite"],
            "confiance_classification": classification["confiance"],
            "action": classification["action"],
        },
        
        # === Diagnostic (Personne 1)
        "diagnostic": {
            "symptomes": classification["diagnostic_extrait"]["symptomes"],
            "equipement": classification["diagnostic_extrait"]["equipement"],
            "utilisateur": classification["diagnostic_extrait"]["utilisateur"],
            "informations_manquantes": classification["informations_manquantes"],
        },
        
        # === Recherche RAG (Personne 2)
        "recherche_rag": {
            "query": raw_ticket,
            "found": result["found"],
            "sources": result["sources"],
            "passages": result["passages"] if result["found"] else [],
            "message": result.get("message", ""),
        },
        
        # === Log d'observabilité
        "log": log_entry,
    }
    
    return merged_result


def main():
    """Test du pipeline complet avec plusieurs requêtes."""
    
    # =====================================================================
    # Initialisation : charger et indexer la KB une fois
    # =====================================================================
    print("\n" + "="*70)
    print("INITIALISATION : Chargement et indexation de la KB")
    print("="*70)
    
    docs = load_documents("./knowledge_base")
    chunks = build_chunks(docs)
    kb = KnowledgeBase()
    kb.index_chunks(chunks)
    
    # =====================================================================
    # Test 1 : Requête "mot de passe oublié"
    # =====================================================================
    print("\n\n" + "="*70)
    print("TEST 1 : Mot de passe oublié")
    print("="*70)
    
    ticket_1 = "j'ai oublié mon mot de passe et je ne peux plus me connecter"
    result_1 = process_ticket_complete(ticket_1, "T-001", kb)
    
    print("\n" + "-"*70)
    print("RÉSUMÉ POUR L'AGENT (Personne 3)")
    print("-"*70)
    print(json.dumps({
        "ticket_id": result_1["ticket_id"],
        "categorie": result_1["classification"]["categorie_primaire"],
        "equipe": result_1["classification"]["equipe_assignee"],
        "priorite": result_1["classification"]["priorite"],
        "sources_trouvees": result_1["recherche_rag"]["sources"],
        "nombre_passages": len(result_1["recherche_rag"]["passages"]),
        "infos_manquantes": result_1["diagnostic"]["informations_manquantes"],
    }, ensure_ascii=False, indent=2))
    
    # =====================================================================
    # Test 2 : Requête "pas de connexion réseau"
    # =====================================================================
    print("\n\n" + "="*70)
    print("TEST 2 : Problème réseau")
    print("="*70)
    
    ticket_2 = "je n'ai plus d'accès à internet depuis ce matin"
    result_2 = process_ticket_complete(ticket_2, "T-002", kb)
    
    print("\n" + "-"*70)
    print("RÉSUMÉ POUR L'AGENT (Personne 3)")
    print("-"*70)
    print(json.dumps({
        "ticket_id": result_2["ticket_id"],
        "categorie": result_2["classification"]["categorie_primaire"],
        "equipe": result_2["classification"]["equipe_assignee"],
        "priorite": result_2["classification"]["priorite"],
        "sources_trouvees": result_2["recherche_rag"]["sources"],
        "nombre_passages": len(result_2["recherche_rag"]["passages"]),
        "infos_manquantes": result_2["diagnostic"]["informations_manquantes"],
    }, ensure_ascii=False, indent=2))
    
    # =====================================================================
    # Test 3 : Requête "redémarre en boucle" (cas sans résultat)
    # =====================================================================
    print("\n\n" + "="*70)
    print("TEST 3 : Redémarre en boucle (cas sans résultat)")
    print("="*70)
    
    ticket_3 = "mon ordinateur redémarre en boucle"
    result_3 = process_ticket_complete(ticket_3, "T-003", kb)
    
    print("\n" + "-"*70)
    print("RÉSUMÉ POUR L'AGENT (Personne 3)")
    print("-"*70)
    print(json.dumps({
        "ticket_id": result_3["ticket_id"],
        "categorie": result_3["classification"]["categorie_primaire"],
        "equipe": result_3["classification"]["equipe_assignee"],
        "priorite": result_3["classification"]["priorite"],
        "sources_trouvees": result_3["recherche_rag"]["sources"],
        "nombre_passages": len(result_3["recherche_rag"]["passages"]),
        "infos_manquantes": result_3["diagnostic"]["informations_manquantes"],
        "message_rag": result_3["recherche_rag"]["message"],
    }, ensure_ascii=False, indent=2))
    
    print("\n\n[OK] Pipeline complet d'intégration exécuté avec succès !")


if __name__ == "__main__":
    main()
