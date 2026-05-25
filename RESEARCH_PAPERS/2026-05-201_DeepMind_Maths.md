# AI-Driven Formal Proof Search (AlphaProof Nexus)

## Références

Titre : Advancing Mathematics Research with AI-Driven Formal Proof Search

Lien : https://arxiv.org/abs/2605.22763

Chercheurs : George Tsoukalas, Anton Kovsharov, Sergey Shirobokov, Anja Surina, Moritz Firsching, Gergely Bérczi, Francisco J. R. Ruiz, Arun Suggala, Adam Zsolt Wagner, Eric Wieser, Lei Yu, Aja Huang, Miklós Z. Horváth, Andrew Ferrauiolo, Henryk Michalewski, Codrut Grosu, Thomas Hubert, Matej Balog, Pushmeet Kohli, Swarat Chaudhuri

Entreprise : Google DeepMind (avec Aarhus University) 

LLM utilisé : Gemini 3.1 Pro (subagents prouveurs), Gemini 3.0 Flash (agents de notation), et AlphaProof comme outil

Date : 21/05/2026

## Abstract

Les LLM excellent de plus en plus dans le raisonnement mathématique, mais leur manque de fiabilité limite leur usage en recherche réelle, car les preuves en langage naturel demandent une relecture experte coûteuse et les erreurs se propagent en cascade à travers la preuve. Une parade consiste à faire générer aux LLM des preuves formelles dans des langages comme Lean, où un compilateur vérifie automatiquement chaque étape logique.

Ce papier présente la première évaluation à grande échelle de cette méthode sur des problèmes ouverts de niveau recherche. L'agent le plus capable a résolu de façon autonome 9 des 353 problèmes d'Erdős ouverts, pour un coût de quelques centaines de dollars par problème, a prouvé 44 des 492 conjectures OEIS, et est déployé en combinatoire, optimisation, théorie des graphes, géométrie algébrique et optique quantique.

Un résultat clé pour le domaine : un agent basique alternant génération par LLM et vérification par Lean a reproduit les 9 succès sur les problèmes d'Erdős, bien qu'à un coût plus élevé sur les problèmes les plus durs. Cela pointe vers un glissement des systèmes spécialisés entraînés vers de simples boucles agentiques à mesure que les LLM progressent.

## Contenu

### Contexte : Lean et les preuves formelles

Lean est un assistant de preuve dans lequel définitions, théorèmes et preuves sont tous du code vérifié mécaniquement par un compilateur, étape par étape. Une preuve est correcte quand il ne reste aucun but à démontrer. L'agent prend en entrée un fichier Lean (une "esquisse de preuve") où le théorème cible a un `sorry` à la place de la preuve, avec des marqueurs (EVOLVE-BLOCK, EVOLVE-VALUE) délimitant ce qu'il peut modifier, et doit produire une preuve sans aucun `sorry`.

### Architecture des agents (framework AlphaProof Nexus)

Quatre configurations de capacité croissante. L'agent A (basique) est un ensemble de subagents prouveurs indépendants, chacun bouclant entre génération par LLM (Gemini 3.1 Pro, raisonnement par chain-of-thought) et vérification par Lean, les erreurs de compilation orientant le tour suivant. L'agent B ajoute la possibilité d'appeler AlphaProof (prouveur Lean basé sur le RL) comme outil. L'agent C (évolutionnaire, inspiré d'AlphaEvolve) fait évoluer une population partagée d'esquisses notées par Elo. L'agent D (full-featured) combine AlphaProof et recherche évolutionnaire ; c'est l'agent principal des expériences.

### Résultats : Erdős et OEIS

L'agent D a tourné sur les 353 problèmes d'Erdős formalisés en Lean (dépôt Formal Conjectures), avec arrêt après 3000 épisodes.

|Résultat|Valeur|
|---|---|
|Problèmes d'Erdős résolus (Agent D)|9 / 353|
|Conjectures OEIS prouvées|44 / 492|
|Coût d'inférence par problème|quelques centaines de dollars|
|Problèmes les plus anciens résolus|ouverts depuis 56 ans|

Deux exemples de constructions sophistiquées :

- Problème #12(i) (Erdős et Sárközy, 1970) : existence d'un ensemble infini avec une contrainte de divisibilité restrictive et une condition de densité. L'agent a construit l'ensemble comme une union infinie de blocs disjoints, intégrant le théorème des restes chinois aux propriétés des ensembles évitant les progressions arithmétiques de longueur 3.
- Problème #125 (ouvert depuis 1996) : concerne la somme A+B d'ensembles à chiffres restreints en base 3 et base 4. L'agent a synthétisé un argument d'amincissement inductif exploitant la proximité diophantienne des deux bases (3^m proche de 4^k).

Pour OEIS, Gemini a autoformalisé 492 questions ; l'agent devait d'abord prouver des "lemmes de test" sur les premiers termes (garde-fou contre les erreurs de formalisation) avant la conjecture cible. L'agent a aussi détecté et corrigé des erreurs de formalisation dans la littérature (interprétation de "densité" corrigée sur les problèmes #125 et #741(i)).

### Déploiement en recherche active

L'agent est utilisé dans plusieurs domaines, avec des résultats concrets : un taux de convergence exact O(1/t) prouvé en optimisation min-max (resserrant une borne connue, avec découverte d'un paramètre inédit via EVOLVE-VALUE), une variante de la conjecture de reconstruction des graphes, une question ouverte depuis environ 15 ans sur les O-séquences pures en géométrie algébrique, le problème #57 de la liste de Ben Green en combinatoire additive (via un contre-exemple sur Z/3Z prouvé formellement), et des travaux en cours en optique quantique avec Mario Krenn.

### Architecture et échecs

Enseignement architectural central : sur les 9 problèmes d'Erdős, l'agent basique (A) les a tous résolus aussi, juste à un coût plus élevé sur les plus durs. Une simple boucle génération-validation égale donc le système évolutionnaire sophistiqué à mesure que les LLM progressent.

Quand l'agent échoue, c'est typiquement en cachant la difficulté dans un `sorry` au sein d'un lemme qui reformule l'énoncé, ou en s'appuyant sur des lemmes qu'il prétend connus mais qui sont des hallucinations. Ces deux modes d'échec sont précisément ce que la vérification formelle de bout en bout attrape.

## Quelques conclusions

- La recherche de preuves formelles par LLM est un outil viable pour la vraie recherche mathématique, pas seulement pour les mathématiques de compétition. L'agent a résolu de façon autonome des problèmes ouverts de longue date (certains ouverts depuis des décennies) dans plusieurs domaines distincts.
- La vérification formelle en Lean est ce qui rend l'approche fiable : elle attrape les hallucinations et les lemmes-raccourcis qui plombent les preuves LLM en langage naturel, ce qui est exactement là où les agents échouent quand ils échouent.
- La tendance la plus importante : une simple boucle génération-validation a égalé l'agent full-featured (évolutionnaire plus AlphaProof) sur les 9 problèmes d'Erdős, suggérant un glissement continu des systèmes spécialisés entraînés vers de simples boucles agentiques à mesure que les LLM de base progressent.
- Les agents jouent aussi des rôles secondaires en recherche : détecter les erreurs de formalisation dans la littérature et découvrir des paramètres algorithmiques inédits (le schéma d'optimisation), pas seulement vérifier des énoncés figés.
- Toutes les preuves Lean et une sélection de preuves en langage naturel sont disponibles sur https://www.github.com/google-deepmind/alphaproof-nexus-results
