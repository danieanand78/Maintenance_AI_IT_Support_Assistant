# KB-NET-07 — Incident réseau global (panne étendue)

Catégorie : Réseau et connectivité
Priorité habituelle : haute

## Symptômes
Plusieurs utilisateurs de plusieurs services signalent une perte de connexion simultanée, ou une lenteur extrême affectant toute une zone géographique ou un bâtiment entier.

## Diagnostic
1. Consulter rechercher_incidents_actifs pour vérifier si un incident global est déjà déclaré.
2. Vérifier verifier_etat_service pour l'ensemble des services réseau critiques.
3. Estimer le nombre d'utilisateurs impactés et les services concernés (SLA à risque si un service critique est touché).

## Procédure de résolution
Un incident réseau global ne doit jamais être traité comme un ticket individuel. Il doit être immédiatement rattaché à l'incident actif correspondant, ou un nouvel incident doit être créé et transmis à l'équipe infrastructure avec la priorité haute.

## Escalade
Validation humaine obligatoire avant toute action corrective sur l'infrastructure réseau centrale. L'assistant doit se limiter au diagnostic et au routage, jamais à une intervention automatique sur l'équipement réseau critique.
