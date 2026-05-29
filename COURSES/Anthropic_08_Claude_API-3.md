# Building with the Claude API (3/3)

## Model Context Protocol (MCP) 

Sans MCP, si on veut que Claude accède à GitHub, on doit écrire soi-même tous les outils : les schémas JSON, les fonctions d'implémentation, les tests, la maintenance. GitHub a des dizaines de fonctionnalités, ce qui représente une quantité de code énorme à produire et maintenir.

MCP déplace la responsabilité de créer et exécuter les outils vers des serveurs MCP spécialisés. Au lieu d'écrire toute l'intégration GitHub, on se connecte à un serveur MCP qui l'a déjà fait.

L'architecture est simple :

- MCP Client : notre serveur applicatif
- MCP Servers : des serveurs spécialisés qui exposent des outils, prompts et ressources pour un service donné

Le client MCP est le pont de communication entre notre serveur applicatif et les serveurs MCP. Il gère tous les détails du protocole et du passage de messages.

Le plus courant est la communication par entrée/sortie standard (stdin/stdout) quand les deux tournent sur la même machine. Mais on peut aussi utiliser HTTP, WebSockets, ou d'autres protocoles réseau.

Deux types de messages principaux :

- **ListToolsRequest / ListToolsResult** : le client demande au serveur quels outils il propose, le serveur répond avec la liste
- **CallToolRequest / CallToolResult** : le client demande au serveur d'exécuter un outil avec certains arguments, le serveur renvoie le résultat

Pour une question comme "Quels sont mes dépôts GitHub ?" :

1. L'utilisateur envoie sa question à notre serveur
2. Notre serveur demande la liste des outils disponibles au client MCP
3. Le client MCP envoie un `ListToolsRequest` au serveur MCP et reçoit un `ListToolsResult`
4. Notre serveur envoie la question et les outils disponibles à Claude
5. Claude décide d'appeler un outil et répond avec une demande d'appel d'outil
6. Notre serveur demande au client MCP d'exécuter l'outil
7. Le client MCP envoie un `CallToolRequest` au serveur MCP, qui appelle l'API GitHub
8. GitHub renvoie les données, qui remontent via `CallToolResult` jusqu'à notre serveur
9. Notre serveur renvoie le résultat à Claude
10. Claude formule la réponse finale

Le SDK Python MCP rend la création d'un serveur très simple :

```
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    ...
}

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
    

```

Exemple d'outil d'édition : 

```
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the document's content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(description="The new text to insert in place of the old text.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
```

Avantages du SDK :

- Génération automatique des schémas JSON depuis les type hints
- Validation des paramètres via Pydantic
- Code lisible et maintenable
- Moins de boilerplate qu'à la main

Le SDK inclut aussi un inspecteur intégré pour tester le serveur sans avoir à connecter toute l'application :

	mcp dev mcp_server.py

Cela démarre un serveur de développement sur le port 6277 avec une interface web. On peut alors :

- Cliquer sur "Connect" pour démarrer le serveur
- Naviguer vers la section "Tools"
- Cliquer "List Tools" pour voir les outils disponibles
- Sélectionner un outil, remplir les paramètres et l'exécuter

Un client MCP se compose de deux éléments :

- **MCPClient** : une classe personnalisée qui simplifie l'utilisation de la session et gère le nettoyage des ressources automatiquement
- **Client Session** : la vraie connexion au serveur, fournie par le SDK

### Ressources

Les ressources exposent des données aux clients, comme des handlers GET en HTTP. Elles suivent un pattern requête/réponse : le client envoie une `ReadResourceRequest` avec une URI, le serveur répond avec les données.

Deux types de ressources : 

1. Ressources directes : URI statique

```
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())
```

2. Ressources templatées : URI avec paramètres parsés automatiquement par le SDK

```
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

Le `mime_type` indique au client comment interpréter les données. Le SDK gère la sérialisation automatiquement.

Lire une ressource côté client : 

```
async def read_resource(self, uri: str) -> Any:
    result = await self.session().read_resource(AnyUrl(uri))
    resource = result.contents[0]

    if isinstance(resource, types.TextResourceContents):
        if resource.mimeType == "application/json":
            return json.loads(resource.text)
        return resource.text
```

L'avantage des ressources est que le contenu est injecté directement dans le prompt, sans passer par un appel d'outil.

### Prompts

Les auteurs d'un serveur MCP peuvent faire des templates d'instructions préparés pour gagner du temps et obtenir de meilleurs résultats : 

```
from mcp.server.fastmcp import base

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.
The id of the document you need to reformat is: {doc_id}
Add in headers, bullet points, tables, etc as necessary.
Use the 'edit_document' tool to edit the document after reformatting.
"""
    return [base.UserMessage(prompt)]
```

Lister les prompts : 

```
async def list_prompts(self) -> list[types.Prompt]: 
	result = await self.session().list_prompts() 
	return result.prompts
```

Récupérer un prompt : 

```
async def get_prompt(self, prompt_name, args: dict[str, str]):
    result = await self.session().get_prompt(prompt_name, args)
    return result.messages
```

Flux dans le CLI :

1. L'utilisateur tape `/` pour voir les prompts disponibles
2. Il sélectionne un prompt
3. Le système demande les arguments nécessaires
4. Le prompt interpolé est envoyé à Claude
5. Claude utilise les outils disponibles pour compléter la tâche

Claude Code intègre un client MCP natif. On peut y connecter des serveurs MCP pour étendre ses capacités avec des outils, prompts et ressources personnalisés : 

	claude mcp add [nom-du-serveur] [commande-de-démarrage]

## Agents et workflows

Les outils Claude Code et Computer Use illustrent les principes clés d'un agent efficace : intégration d'outils, exécution de tâches multi-étapes, interaction avec l'environnement, résolution autonome de problèmes.

Pas mal de patterns possibles pour l'agencement dans les tâches : 

1. Parallélisation : division en sous-tâches qui permet d'optimiser et de mieux scaler
2. Chaînage : découpage en étapes séquentielles qui s'empilent 
3. Routing : redirection des requêtes entrantes vers des pipelines spécialisés

Un agent reçoit un objectif et un ensemble d'outils, il détermine lui-même comment les combiner pour atteindre le but. Contrairement aux workflows, on ne connaît pas à l'avance les étapes exactes. La puissance vient de la combinaison d'outils.

Claude Code illustre bien ce principe : il dispose d'outils génériques (`bash`, `read`, `write`, `edit`, `grep`) et non d'outils spécialisés. Cette abstraction lui permet de gérer des scénarios que les développeurs n'avaient pas explicitement prévus

Claude opère à l'aveugle : il doit pouvoir observer les résultats de ses actions pour fonctionner efficacement :

- Avec Computer Use, chaque action est suivie d'une capture d'écran
- Avant de modifier un fichier, Claude doit d'abord le lire
- On peut guider ce comportement via le system prompt

Question à se poser quand on conçoit un agent : "Comment Claude saura-t-il si cette action a fonctionné ?" 

Toujours privilégier les workflows quand c'est possible. Les agents offrent de la flexibilité mais au prix de la fiabilité et de la prévisibilité. On ne recourt aux agents que quand les exigences ne peuvent vraiment pas être prédéterminées à l'avance.

