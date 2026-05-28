# Project Glasswing : note de mise à jour

## About

Lien : https://www.anthropic.com/research/glasswing-initial-update      
Date : 22/05/2026      

## Contexte

Project Glasswing est un effort collaboratif lancé par Anthropic avec environ 50 partenaires, dont l'objectif est de sécuriser les logiciels les plus critiques au monde avant que des modèles d'intelligence artificielle offensifs, toujours plus capables, ne puissent être retournés contre eux. Les partenaires initiaux construisent et maintiennent des logiciels fondamentaux pour le fonctionnement d'internet et d'autres infrastructures essentielles : corriger leurs failles réduit le risque pour les nombreuses organisations qui en dépendent, et donc pour des milliards d'utilisateurs finaux.

L'outil employé est Claude Mythos Preview, un modèle qui n'est pas encore rendu public. Anthropic précise ne pas pouvoir détailler toutes les découvertes, car les vulnérabilités suivent une politique de divulgation responsable (90 jours), si bien que les bugs publiés sont un indicateur retardé des capacités réelles du modèle. La note fournit donc des exemples illustratifs et des statistiques agrégées plutôt que le détail complet.

Le constat central inverse le problème habituel de la sécurité logicielle : trouver les vulnérabilités n'est plus le facteur limitant ; le facteur limitant est désormais la vitesse à laquelle on peut les vérifier, les divulguer et les corriger. Autrement dit, la capacité humaine de triage et de correction devient le véritable goulot d'étranglement, alors que la découverte est devenue quasi triviale avec Mythos Preview.

## Global (partenaires)

- Plus de 10 000 vulnérabilités hautes ou critiques trouvées en 1 mois
- La plupart des partenaires : des centaines de vulnérabilités critiques ou hautes chacun
- Rythme de découverte multiplié par 10 pour plusieurs partenaires

## Cloudflare

- 2 000 bugs trouvés
- Dont 400 hauts ou critiques
- Taux de faux positifs jugé meilleur que les testeurs humains

## Firefox (Mozilla)

- 271 vulnérabilités trouvées et corrigées dans Firefox 150
- Soit plus de 10 fois plus que dans Firefox 148 (testé avec Claude Opus 4.6)

## Autres validations externes

- UK AI Security Institute : premier modèle à résoudre ses 2 cyber-ranges de bout en bout
- XBOW : progrès net sur tous les modèles existants, précision « sans précédent » token pour token
- ExploitBench et ExploitGym : Mythos Preview = meilleur performeur

## Volume de correctifs côté éditeurs

- Palo Alto Networks : 5 fois plus de correctifs que d'habitude
- Microsoft : le nombre de correctifs « va continuer à augmenter pendant un moment »
- Oracle : détection et correction « plusieurs fois plus rapides »
- Banque partenaire : virement frauduleux de 1,5 million de dollars bloqué

## Open source (scan Anthropic sur plus de 1 000 projets)

- 6 202 vulnérabilités estimées hautes ou critiques, sur 23 019 au total (tous niveaux)
- 1 752 hautes ou critiques évaluées indépendamment (6 firmes externes ou Anthropic)
- 90,6 % (1 587) = vrais positifs
- 62,4 % (1 094) = confirmées hautes ou critiques
- Projection : environ 3 900 hautes ou critiques au rythme actuel, hors partenaires
- wolfSSL : exploit construit pour forger des certificats (faux sites bancaires), CVE-2026-5194, corrigée

## Divulgation et correction (le goulot)

- Fenêtre de divulgation : 90 jours (ou environ 45 jours après disponibilité d'un correctif)
- Délai moyen de correction d'un bug haut ou critique : 2 semaines
- 1 129 bugs « non vérifiés » signalés directement (sur demande des mainteneurs), dont 175 estimés hauts ou critiques
- 530 bugs hauts ou critiques divulgués aux mainteneurs
- 827 confirmés en attente de divulgation
- 75 sur 530 corrigés, 65 avec avis public
- Mainteneurs open source saturés (déluge de rapports générés par intelligence artificielle de mauvaise qualité), certains demandent de ralentir

## Outils et écosystème

- Claude Security en bêta publique (Enterprise) : plus de 2 100 vulnérabilités corrigées en 3 semaines avec Claude Opus 4.7
- Cyber Verification Program (levée de certains garde-fous pour usage légitime)
- Mise à disposition des skills, d'un harness (cartographie de la base de code + sous-agents + triage + rapports) et d'un threat model builder
- Cisco a publié en open source son Foundry Security Spec
- Partenariat avec l'OpenSSF Alpha-Omega pour aider les mainteneurs

## Stratégie de publication

- Mythos pas encore public : aucun acteur (Anthropic inclus) n'a de garde-fous assez solides contre l'usage malveillant
- Prochaine étape : extension à d'autres partenaires (dont gouvernements américain et alliés), puis publication générale une fois les garde-fous renforcés
