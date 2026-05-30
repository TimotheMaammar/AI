# FuzzingBrain V2 : détection de vulnérabilités par LLM multi-agents

## Références

Titre complet : "FuzzingBrain V2: A Multi-Agent LLM System for Automated Vulnerability Discovery and Reproduction"

Lien : https://arxiv.org/abs/2605.21779

Date : 20/05/2026

Chercheurs : Ze Sheng, Zhicheng Chen, Qingxiao Xu, Kewen Zhu, Jeff Huang

## Abstract

Les LLM appliqués à la détection de vulnérabilités souffrent de trois problèmes structurels : taux de faux positifs élevé faute de vérification reproductible, granularité de localisation sous-optimale (trop large au niveau fonction, trop étroite au niveau ligne), et difficulté à raisonner sur les dépendances croisées entre fonctions. FuzzingBrain V2 est un système multi-agents qui attaque ces trois points simultanément, en s'appuyant sur OSS-Fuzz de Google comme oracle de vérification automatique.

Sur le dataset C/C++ de la compétition AIxCC 2025, le système atteint un taux de détection de 90% (36 vulnérabilités sur 40). En déploiement réel sur 12 projets open source, il a découvert 29 vulnérabilités zero-day, toutes confirmées et corrigées par les mainteneurs, avec 2 CVE attribuées.

## Contenu

### Quatre contributions techniques

**1. Intégration avec OSS-Fuzz.** Toutes les vulnérabilités reportées sont vérifiées comme reproductibles par fuzzer. Ce point élimine le problème des faux positifs : aucun rapport ne sort sans confirmation automatisée.

**2. Suspicious Point.** Nouvelle abstraction basée sur le flux de contrôle pour localiser les vulnérabilités à la granularité optimale, entre le niveau fonction (trop large) et le niveau ligne (trop étroit). Suspicious Point désigne un point de contrôle suspect dans le graphe d'exécution, là où un chemin anormal est susceptible de déclencher le bug.

**3. Analyse hiérarchique des fonctions par double couche de fuzzing.** L'analyse est pilotée par la logique du code plutôt que par un balayage exhaustif, ce qui permet d'augmenter la couverture fonctionnelle sous contrainte de ressources.

**4. Outils statiques et dynamiques via MCP.** Des outils d'analyse statique et dynamique sont exposés via le protocole MCP (Model Context Protocol), couplés à de l'ingénierie de contexte pour améliorer le raisonnement sur les vulnérabilités impliquant des dépendances inter-fonctions complexes.

### Résultats

| Benchmark | Résultat |
| --- | --- |
| AIxCC 2025 Final (C/C++) | 36/40 détectées (90%) |
| Zero-days découverts en production | 29 sur 12 projets open source |
| Confirmation par les mainteneurs | 100% des 29 |
| CVE attribuées | 2 |

### Quelques conclusions

Le travail pointe deux limites fondamentales des approches LLM existantes pour la sécurité : l'absence de vérification reproductible et le mauvais choix de granularité de localisation. FuzzingBrain V2 répond aux deux par des mécanismes complémentaires (oracle de fuzzing + Suspicious Point). La validation sur une compétition officielle (AIxCC 2025) et sur des projets réels renforce la crédibilité des résultats.
