import re
import unicodedata


# ============================================================
# CONFIGURATION
# ============================================================

MAX_LENGTH = 5000

SAFE = "SAFE"
SUSPICIOUS = "SUSPICIOUS"
HIGH_RISK = "HIGH_RISK"
BLOCK = "BLOCK"


# ============================================================
# MOTIFS DE DÉTECTION
# ============================================================

PATTERNS = {

    # --------------------------------------------------------
    # Tentative de modification des instructions
    # --------------------------------------------------------

    "instruction_override": {
        "weight": 3,
        "patterns": [
            r"\bignore(?:z|r)?\s+(toutes?|les)\s+(instructions?|règles?)",
            r"\bignore(?:z|r)?\s+(toutes?|les)\s+(instructions?|consignes?)\s+précédentes?",
            r"\boublie(?:z|r)?\s+(toutes?|les)\s+(instructions?|règles?|consignes?)",
            r"\bnéglige(?:z|r)?\s+(toutes?|les)\s+(instructions?|règles?|consignes?)",
            r"\bne\s+su(?:is|ivez)\s+plus\s+(les|ces)\s+(instructions?|règles?|consignes?)",
        ]
    },


    # --------------------------------------------------------
    # Tentative d'extraction du prompt système
    # --------------------------------------------------------

    "prompt_extraction": {
        "weight": 4,
        "patterns": [
            r"\bprompt\s+système\b",
            r"\binstructions?\s+système\b",
            r"\binstructions?\s+du\s+système\b",

            r"\brévèle(?:z|r)?\s+(ton|votre|le)\s+prompt\s+système\b",
            r"\bmontre(?:z|r)?\s+(moi\s+)?(ton|votre|le)\s+prompt\s+système\b",
            r"\bdonne(?:z|r)?\s+(moi\s+)?(ton|votre|le)\s+prompt\s+système\b",
            r"\baffiche(?:z|r)?\s+(ton|votre|le)\s+prompt\s+système\b",

            r"\bquelles?\s+sont\s+tes\s+instructions\s+système\b",
        ]
    },


    # --------------------------------------------------------
    # Tentative de contournement de la sécurité
    # --------------------------------------------------------

    "security_bypass": {
        "weight": 4,
        "patterns": [
            r"\bcontourne(?:z|r)?\s+(les|toutes?\s+les)\s+(règles?|restrictions?|sécurités?)",
            r"\bcontourne(?:z|r)?\s+(la|les)\s+(sécurité|protection)s?",
            r"\bignore(?:z|r)?\s+(les|toutes?\s+les)\s+(mesures?|protections?)\s+de\s+sécurité",
            r"\bdésactive(?:z|r)?\s+(la|les)\s+(sécurité|protections?)",
            r"\bsupprime(?:z|r)?\s+(les|toutes?\s+les)\s+(restrictions?|protections?)",
            r"\boutrepasse(?:z|r)?\s+(les|toutes?\s+les)\s+(règles?|restrictions?)",
        ]
    },


    # --------------------------------------------------------
    # Tentative de changement de rôle
    # --------------------------------------------------------

    "role_manipulation": {
        "weight": 2,
        "patterns": [
            r"\bfais\s+comme\s+si\s+tu\s+étais\b",
            r"\bprétends?\s+que\s+tu\s+es\b",
            r"\btu\s+es\s+maintenant\b",
            r"\bà\s+partir\s+de\s+maintenant\s+tu\s+es\b",
            r"\bjoue\s+le\s+rôle\s+de\b",
            r"\bcomporte[- ]toi\s+comme\s+un\b",
        ]
    }
}


# ============================================================
# NORMALISATION
# ============================================================

def normalize_text(text):
    """
    Normalise le texte avant l'analyse.
    """

    # Conversion en minuscules
    text = text.lower()

    # Normalisation Unicode
    text = unicodedata.normalize("NFKC", text)

    # Réduction des espaces multiples
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# VALIDATION DE BASE
# ============================================================

def basic_validation(user_input):
    """
    Vérifications basiques de sécurité.
    """

    # Type
    if not isinstance(user_input, str):
        return False, "INVALID_TYPE"

    # Entrée vide
    if not user_input.strip():
        return False, "EMPTY_INPUT"

    # Longueur
    if len(user_input) > MAX_LENGTH:
        return False, "INPUT_TOO_LONG"

    # Caractères de contrôle
    if any(
        ord(char) < 32 and char not in "\n\t\r"
        for char in user_input
    ):
        return False, "CONTROL_CHARACTER"

    return True, None


# ============================================================
# DÉTECTION DES MOTIFS
# ============================================================

def detect_patterns(text):
    """
    Recherche les comportements suspects.
    """

    score = 0
    detections = []

    for category, data in PATTERNS.items():

        for pattern in data["patterns"]:

            if re.search(pattern, text, re.IGNORECASE):

                score += data["weight"]

                detections.append({
                    "type": category,
                    "weight": data["weight"]
                })

                # Une catégorie ne compte qu'une seule fois
                break

    return score, detections


# ============================================================
# CALCUL DU RISQUE
# ============================================================

def calculate_risk(score):

    if score >= 7:
        return BLOCK

    if score >= 4:
        return HIGH_RISK

    if score >= 2:
        return SUSPICIOUS

    return SAFE


# ============================================================
# ANALYSE COMPLÈTE
# ============================================================

def analyze_input(user_input):

    # --------------------------------------------------------
    # Validation de base
    # --------------------------------------------------------

    valid, error = basic_validation(user_input)

    if not valid:

        return {
            "allowed": False,
            "risk_level": BLOCK,
            "score": 10,
            "reasons": [error],
            "detections": []
        }


    # --------------------------------------------------------
    # Normalisation
    # --------------------------------------------------------

    normalized = normalize_text(user_input)


    # --------------------------------------------------------
    # Détection
    # --------------------------------------------------------

    score, detections = detect_patterns(normalized)


    # --------------------------------------------------------
    # Calcul du risque
    # --------------------------------------------------------

    risk_level = calculate_risk(score)


    # --------------------------------------------------------
    # Raisons
    # --------------------------------------------------------

    reasons = [
        detection["type"]
        for detection in detections
    ]


    # --------------------------------------------------------
    # Autorisation
    # --------------------------------------------------------

    allowed = risk_level in [
        SAFE,
        SUSPICIOUS
    ]


    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    return {
        "allowed": allowed,
        "risk_level": risk_level,
        "score": score,
        "reasons": reasons,
        "detections": detections
    }


# ============================================================
# INTERFACE DE L'OUTIL
# ============================================================

def run(user_input):
    """
    Point d'entrée utilisé par agent.py.
    """

    return analyze_input(user_input)