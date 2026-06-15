# Meetup Wroclaw 15/06/2026

## Notes en vrac

Utiliser Cowork au lieu du chat basique est vraiment pertinent, puisqu'il peut au final être un chat avec une meilleure gestion du contexte et des fichiers si on souhaite l'utiliser comme tel.

Un autre avantage des MCP Apps est qu'elles sont déterministes : elles rendent la réponse d'une façon fixe et prévisible (toujours un tableau, toujours tel formulaire, etc.), contrairement à un texte libre de LLM qui varie. Pour des usages professionnels c'est crucial.

### Sampling

En temps normal, c'est l'utilisateur (ou l'application) qui envoie un message au LLM et il répond. Avec le sampling MCP, c'est le serveur MCP lui-même qui peut déclencher une inférence LLM en cours d'exécution.

Exemple concret : un agent MCP doit rédiger un rapport. À mi-chemin, le serveur réalise qu'il a besoin de reformuler un paragraphe. Au lieu de tout renvoyer au client, il fait lui-même un appel "sample" au LLM, obtient la reformulation, et continue son workflow. Le LLM devient un sous-composant que le serveur orchestre, pas juste un endpoint passif.

C'est ce qui permet des agents véritablement autonomes : le serveur MCP prend des décisions, appelle le modèle quand il en a besoin, sans attendre l'utilisateur.

### Elicitation

C'est le mécanisme inverse : le serveur MCP a besoin d'une information de l'utilisateur pour continuer, et il la demande de façon structurée et typée.

Sans elicitation : le LLM pose la question en texte libre, l'utilisateur répond en texte libre, le LLM doit parser et espérer avoir bien compris.

Avec elicitation : le serveur MCP envoie une requête structurée qui dit "J'ai besoin d'une date, d'un booléen oui/non, et d'un choix parmi ces 3 options". Le client affiche un formulaire propre, l'utilisateur remplit, et le serveur reçoit des données typées et valides directement.

C'est ce qui relie elicitation et déterminisme : la réponse est structurée, pas de texte à interpréter. Et cela évite aussi les problèmes liés au "Weak Prompting" : l'utilisateur clique dans un formulaire au lieu de devoir formuler une instruction précise.

### MCP Specification

C'est le document qui définit formellement le protocole. Il spécifie comment un client (Claude, Cursor, etc.) et un serveur MCP doivent communiquer : format des messages, types de données, cycle de vie d'une connexion, capacités négociées au démarrage. Format JSON-RPC 2.0.

Elle standardise quatre primitives principales : Tools, Resources, Prompts et des capacités optionnelles comme Sampling ou Elicitation. Tout commence par un handshake de négociation des capacités, ce qui permet d'ajouter de nouvelles fonctionnalités sans casser la compatibilité entre implémentations.
