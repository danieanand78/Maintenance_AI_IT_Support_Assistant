"""
Module RAG - mAIntenance & Assistance
Pipeline : Documents -> Chunking -> Embeddings -> Vector DB -> Recherche -> Top passages

Installation :
    pip install chromadb sentence-transformers

Usage rapide en bas du fichier (section __main__).
"""

import os
import re
import uuid
from typing import List, Dict, Optional, Optional

import chromadb
from sentence_transformers import SentenceTransformer


# ----------------------------------------------------------------------
# 1. CHARGEMENT + NETTOYAGE
# ----------------------------------------------------------------------

def load_documents(folder_path: str) -> List[Dict]:
    """
    Charge tous les fichiers texte/markdown d'un dossier.
    Chaque fichier devient un "document" avec un id = nom de fichier (sans extension).
    Adapte cette fonction si tes docs sont dans un autre format (csv, json, pdf...).
    """
    documents = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".txt", ".md")):
            doc_id = os.path.splitext(filename)[0]  # ex: "KB-NET-04"
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                raw_text = f.read()
            documents.append({
                "doc_id": doc_id,
                "text": clean_text(raw_text),
            })
    return documents


def clean_text(text: str) -> str:
    """Nettoyage minimal : espaces multiples, sauts de ligne superflus."""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


# ----------------------------------------------------------------------
# 2. CHUNKING
# ----------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> List[str]:
    """
    Découpe un texte en chunks de ~chunk_size mots, avec chevauchement.
    Simple et suffisant pour un corpus de fiches techniques / procédures.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# Catégories alignées exactement avec CATEGORY_RULES de Personne 1 (categorie.py),
# pour que la recherche puisse être filtrée/priorisée par catégorie détectée.
DOC_CATEGORY = {
    "KB-AUTH-01": "Comptes et authentification",
    "KB-AUTH-02": "Comptes et authentification",
    "KB-NET-04": "Réseau et connectivité",
    "KB-NET-07": "Réseau et connectivité",
    "KB-HW-02": "Matériel informatique",
    "KB-APP-03": "Logiciels et applications",
    "KB-PRINT-01": "Imprimantes et périphériques",
    "KB-ACCESS-01": "Droits d'accès",
    "KB-SEC-01": "Cybersécurité",
    "KB-ESC-01": "Toutes catégories",  # document d'escalade générale, hors filtrage
}


def build_chunks(documents: List[Dict]) -> List[Dict]:
    """Transforme chaque document en une liste de chunks avec métadonnées,
    y compris la catégorie alignée avec celles de Personne 1."""
    all_chunks = []
    for doc in documents:
        categorie = DOC_CATEGORY.get(doc["doc_id"], "Autre ou indéterminé")
        for chunk_text_value in chunk_text(doc["text"]):
            all_chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk_text_value,
                "doc_id": doc["doc_id"],
                "categorie": categorie,
            })
    return all_chunks


# ----------------------------------------------------------------------
# 3. EMBEDDINGS + 4. VECTOR DB (Chroma)
# ----------------------------------------------------------------------

class KnowledgeBase:
    def __init__(self, persist_dir: str = "./chroma_kb",
                 model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.client = chromadb.PersistentClient(path=persist_dir)
        # metadata "hnsw:space": "cosine" -> distances bornées entre 0 et 2,
        # beaucoup plus simples à seuiller que la distance L2 par défaut.
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )

    def index_chunks(self, chunks: List[Dict]):
        """Calcule les embeddings et les insère dans Chroma.
        Supprime et recrée entièrement la collection avant d'indexer, pour
        garantir une base propre à chaque exécution (évite les doublons
        accumulés au fil des tests successifs)."""
        self.client.delete_collection(name="knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )

        texts = [c["text"] for c in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True).tolist()

        self.collection.add(
            ids=[c["id"] for c in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"doc_id": c["doc_id"], "categorie": c["categorie"]} for c in chunks],
        )
        print(f"{len(chunks)} chunks indexés.")

    # ------------------------------------------------------------------
    # 5. RECHERCHE
    # ------------------------------------------------------------------

    def search(self, query: str, k: int = 3, min_relevance: float = 0.15,
               categorie: Optional[str] = None) -> Dict:
        """
        Recherche les k passages les plus pertinents.
        min_relevance : seuil de similarité en dessous duquel on considère
        qu'il n'y a PAS de source pertinente (cas obligatoire du sujet).
        categorie : si fournie (ex. issue de la classification de Personne 1),
        restreint la recherche aux documents de cette catégorie. Le document
        d'escalade générale (KB-ESC-01, "Toutes catégories") reste toujours
        inclus quel que soit le filtre.

        Avec l'espace "cosine" configuré sur la collection, Chroma retourne
        une distance cosinus (0 = identique, 2 = opposé).
        similarité cosinus = 1 - distance cosinus.
        """
        query_embedding = self.model.encode([query]).tolist()

        where_filter = None
        if categorie:
            where_filter = {
                "$or": [
                    {"categorie": categorie},
                    {"categorie": "Toutes catégories"},
                ]
            }

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=where_filter,
        )

        passages = []
        for text, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            similarity = 1 - distance  # conversion distance cosinus -> similarité
            passages.append({
                "text": text,
                "doc_id": meta["doc_id"],
                "score": round(similarity, 3),
            })

        # Filtrage par seuil de pertinence
        relevant = [p for p in passages if p["score"] >= min_relevance]

        if not relevant:
            return {
                "found": False,
                "passages": [],
                "sources": [],
                "message": "Aucune source suffisamment pertinente trouvée.",
            }

        return {
            "found": True,
            "passages": relevant,
            "sources": list(dict.fromkeys(p["doc_id"] for p in relevant)),  # uniques, ordonnés
        }


# ----------------------------------------------------------------------
# UTILISATION
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 6. RETOUR AU LLM + LOG D'OBSERVABILITÉ
# ----------------------------------------------------------------------

import time
from datetime import datetime


def search_with_log(kb: "KnowledgeBase", query: str, ticket_id: str, k: int = 3,
                     categorie: Optional[str] = None) -> tuple:
    """
    Effectue la recherche et produit en même temps :
    - result : à transmettre à l'Agent (Personne 3) pour rédiger la réponse
    - log_entry : à transmettre au journal d'observabilité (Personne 5),
      dans le même format que les autres composantes de l'équipe
      (component / action / parameters / result / status / latency_ms).

    categorie : catégorie déjà déterminée par Personne 1 (optionnel), permet
    de restreindre/prioriser la recherche sur les documents correspondants.
    """
    start = time.time()
    result = kb.search(query, k=k, categorie=categorie)
    latency_ms = round((time.time() - start) * 1000)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "ticket_id": ticket_id,
        "component": "rag",
        "action": "search_passages",
        "parameters": {"query": query, "k": k, "categorie": categorie},
        "result": {
            "found": result["found"],
            "sources": result["sources"],
        },
        "status": "success" if result["found"] else "no_relevant_source",
        "latency_ms": latency_ms,
    }

    return result, log_entry


if __name__ == "__main__":
    # 1. Charger + nettoyer
    docs = load_documents("./knowledge_base")  # adapte le chemin

    # 2. Chunker
    chunks = build_chunks(docs)

    # 3-4. Embeddings + indexation dans Chroma
    kb = KnowledgeBase()
    kb.index_chunks(chunks)

    # 5-6-7. Recherche + retour au LLM
    query = "redémarre en boucle"
    result = kb.search(query, k=3)

    print(result)
    # -> à transmettre tel quel (ou après un léger formatage) à la Personne "Agent"
    #    pour qu'elle génère une réponse citant result["sources"]