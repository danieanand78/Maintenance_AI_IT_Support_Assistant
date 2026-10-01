# KB-NET-04 — Perte de connexion réseau (poste individuel)

Catégorie : Réseau et connectivité
Priorité habituelle : moyenne

## Symptômes
L'utilisateur ne peut plus accéder à Internet ni aux ressources internes depuis son poste. Les autres collègues du même bureau ne semblent pas affectés.

## Diagnostic
1. Vérifier l'état du câble réseau ou de la connexion Wi-Fi.
2. Vérifier via verifier_etat_service si le service réseau est opérationnel globalement.
3. Vérifier via rechercher_incidents_actifs s'il existe un incident réseau en cours dans le secteur de l'utilisateur.

## Procédure de résolution
1. Redémarrer l'équipement réseau local (box, switch) si accessible.
2. Redémarrer le poste de l'utilisateur.
3. Si le problème persiste, vérifier la configuration IP du poste.
4. Si aucun incident global n'est détecté et que le problème persiste après redémarrage, créer un ticket matériel pour vérification du câblage ou de la carte réseau.

## Escalade
Si plusieurs utilisateurs du même secteur signalent le même problème dans un court délai, il peut s'agir d'un incident réseau global : transmettre immédiatement à l'équipe infrastructure.
