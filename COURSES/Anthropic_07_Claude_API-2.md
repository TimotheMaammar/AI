# Building with the Claude API (2/3)

Par défaut, Claude ne connaît que ce qu'il a appris pendant son entraînement. Il ne peut pas accéder à bon nombre de données en temps réel : météo, cours de bourse, bases de données externes, etc. Les outils résolvent ce problème en créant une façon structurée pour Claude de demander et recevoir des informations fraîches.

Une fonction outil est une fonction Python classique que Claude peut appeler quand il a besoin d'informations supplémentaires. Par exemple, si quelqu'un demande l'heure, Claude appelle une fonction `get_current_datetime()` pour obtenir l'heure réelle.

Bonnes pratiques pour écrire ces fonctions : 

- Le nom de la fonction et des paramètres doit clairement indiquer leur rôle
- Vérifier que les paramètres requis ne sont pas vides ou invalides
- Messages d'erreur clairs pour que Claude puisse réessayer l'appel avec des paramètres corrigés

```
def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)
    
get_current_datetime()        # "2024-01-15 14:30:25"
get_current_datetime("%H:%M") # "14:30"
```

Le flux suit un pattern précis en quatre étapes :

1. **Requête initiale** : on envoie la question à Claude avec des instructions sur comment récupérer des données externes
2. **Demande d'outil** : Claude analyse la question, décide qu'il a besoin d'informations supplémentaires et demande des données précises
3. **Récupération** : notre serveur exécute du code pour aller chercher les données (API, base de données, etc.)
4. **Réponse finale** : on renvoie les données à Claude, qui génère une réponse complète en combinant la question originale et les données fraîches


Après avoir écrit la fonction, on crée un schéma JSON qui sert de documentation pour Claude. Il lui explique quand et comment appeler l'outil.

Un schéma complet contient trois parties :

- **name** : nom de l'outil
- **description** : ce que fait l'outil, quand l'utiliser, ce qu'il retourne
- **input_schema** : description des paramètres attendus

## Gérer les outils dans le code 

Quand Claude utilise un outil, il ne renvoie plus un simple bloc de texte mais un message multi-blocs contenant :

- **Un bloc texte** : ce que Claude dit à l'utilisateur ("Je vais chercher l'heure...")
- **Un bloc `tool_use`** : les instructions pour appeler la fonction, avec un ID unique, le nom de la fonction et les paramètres

Et de la même manière, il faut aussi ajouter les outils lors de l'appel : 

```
response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=messages,
    tools=[get_current_datetime_schema],
)
```

Si Claude doit utiliser plusieurs outils, il faut une boucle de conversation (voir les codes complets pour plus de détails).

Le champ `stop_reason` de la réponse indique si Claude veut appeler un outil. Quand c'est le cas, sa valeur est `"tool_use"` :

```
def run_conversation(messages):
    while True:
        response = chat(messages, tools=[get_current_datetime_schema])
        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages
```

Claude a quelques outils natifs assez utiles : 
- Éditeur de texte 
- Recherche web
- ...

## RAG et recherche agentique

Quand on travaille avec un document très long (exemple : rapport financier de 800 pages), on ne peut pas tout mettre dans un seul prompt. Il y a des limites de longueur, les prompts trop longs coûtent plus cher, prennent plus de temps, et Claude est moins efficace sur des contextes très longs. Pour ce cas de figure, la meilleure option est en général de faire du RAG. 

On découpe le document en morceaux (chunks) en amont. Quand l'utilisateur pose une question, on cherche les chunks les plus pertinents et on n'inclut que ceux-là dans le prompt.

Exemple : si quelqu'un demande "Quels sont les risques de cette entreprise ?", on trouve le chunk correspondant à la section "Facteurs de risque" et on l'envoie à Claude, pas les 800 pages.

Avantages : 
- Moins cher et plus rapide
- Claude se concentre sur l'essentiel

Inconvénients : 
- Nécessite un prétraitement et un mécanisme de recherche
- Plusieurs façons de chunker et pas de solution universelle

### Stratégies de découpage (chunking)

La façon dont on découpe les documents impacte directement la qualité du système RAG. Un mauvais découpage peut insérer du contexte complètement hors sujet dans le prompt.

En production, le découpage par taille avec overlap est souvent le choix par défaut : simple, fiable, et compatible avec tous les types de documents. Il n'existe pas de stratégie universellement meilleure. Le bon choix dépend des documents, du cas d'usage et du compromis accepté entre complexité et qualité.

1. Découpage par taille

On divise le texte en morceaux de longueur égale. Simple et universel, mais les mots peuvent être coupés en milieu de phrase et les sections peuvent être séparées de leurs titres.

Pour atténuer ces problèmes, on ajoute un overlap : chaque chunk inclut quelques caractères des chunks voisins.

```
def chunk_by_char(text, chunk_size=150, chunk_overlap=20):
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)

    return chunks
```

2. Découpage par structure

On divise selon la structure naturelle du document : titres, paragraphes, sections. Idéal pour les fichiers Markdown ou les documents bien formatés.

```
def chunk_by_section(document_text):
    pattern = r"\n## "
    return re.split(pattern, document_text)
```

3. Découpage par phrases

Compromis pratique : on découpe en phrases avec une regex, puis on les regroupe par blocs avec overlap optionnel.

```
def chunk_by_sentence(text, max_sentences_per_chunk=5, overlap_sentences=1):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        chunks.append(" ".join(sentences[start_idx:end_idx]))
        start_idx += max_sentences_per_chunk - overlap_sentences

    return chunks
```

4. Découpage sémantique

L'approche la plus sophistiquée : on analyse la relation entre les phrases via du NLP pour regrouper celles qui sont liées. Produit les chunks les plus pertinents, mais coûteux en calcul et complexe à implémenter.

### Embeddings 

Un embedding est une représentation numérique du sens d'un texte. On passe du texte dans un modèle d'embedding, qui retourne une longue liste de nombres entre -1 et +1. Chaque nombre représente une "dimension" du sens du texte.

On peut imaginer que certains nombres représentent "à quel point le texte parle d'océans" ou "à quel point le texte est joyeux", mais ce ne sont que des exemples conceptuels. En réalité, la signification exacte de chaque dimension est apprise par le modèle pendant l'entraînement et n'est pas directement interprétable.

Anthropic ne fournit pas de génération d'embeddings. Le provider recommandé est VoyageAI. 

On crée un compte séparé, on récupère une clé API, et on l'ajoute au fichier `.env` :

```
VOYAGE_API_KEY="XYZ"
```

Implémentation : 

```
# pip install voyageai

from dotenv import load_dotenv
import voyageai

load_dotenv()
client = voyageai.Client()

def generate_embedding(text, model="voyage-3-large", input_type="query"):
    result = client.embed([text], model=model, input_type=input_type)
    return result.embeddings[0]
```

### Pipeline complet

Le pipeline RAG suit six étapes, dont les trois premières sont du prétraitement qui s'effectue en amont, avant toute question utilisateur.

**Étape 1 : découper le document en chunks**

On prend le document source et on le divise en morceaux. Exemple avec deux sections :

- Section 1 (recherche médicale) : "This year saw significant strides in our understanding of XDR-47, a 'bug' we have not seen before."
- Section 2 (génie logiciel) : "This division dedicated significant effort to studying various infection vectors in our distributed systems"

**Étape 2 : générer les embeddings**

On convertit chaque chunk en vecteur numérique. Pour simplifier, imaginons un modèle qui retourne deux nombres : le premier représente "à quel point le texte parle de médecine", le second "à quel point il parle de logiciel".

- Section médicale : `[0.944, 0.331]` (très médical, un peu logiciel à cause du mot "bug")
- Section logiciel : `[0.295, 0.955]` (très logiciel, un peu médical à cause d'"infection vectors")

L'API normalise automatiquement les vecteurs pour que leur magnitude soit égale à 1.

**Étape 3 : stocker dans une base vectorielle**

On stocke ces embeddings dans une base de données vectorielle, optimisée pour stocker et comparer des listes de nombres.

On s'arrête ici et on attend qu'un utilisateur pose une question.

**Étape 4 : traiter la question utilisateur**

Quand l'utilisateur pose une question, on la passe dans le même modèle d'embedding. La question "What did the software engineering dept do this year?" donne quelque chose comme `[0.112, 0.993]` : faible score médical, fort score logiciel.

**Étape 5 : trouver les chunks similaires**

On envoie l'embedding de la question à la base vectorielle, qui retourne les chunks les plus proches.      
La similarité se mesure avec la **similarité cosinus** : le cosinus de l'angle entre deux vecteurs.

- Résultat entre -1 et 1
- Proche de 1 : très similaire
- Proche de -1 : très différent
- 0 : aucune relation

Dans notre exemple :

- Similarité avec la section logiciel : **0.983** (très proche)
- Similarité avec la section médicale : **0.398** (peu proche)

On voit aussi souvent la **distance cosinus** = 1 - similarité cosinus. Plus elle est proche de 0, plus les vecteurs sont similaires.

**Étape 6 : construire le prompt final**

On combine la question de l'utilisateur et le chunk pertinent trouvé, puis on envoie le tout à Claude :

```
Answer the user's question about the financial document.

<user_question>
How many bugs did engineers fix this year?
</user_question>

<report>
## Section 2: Software Engineering
This division dedicated significant effort to studying various infection vectors in our distributed systems
</report>
```

Claude génère alors une réponse basée uniquement sur le contexte pertinent, sans bruit ni hors-sujet.

Voir le code Python si besoin.
### Recherche hybride : combiner vecteurs et BM25

La recherche vectorielle (sémantique) et la recherche BM25 (lexicale) ont chacune leurs forces. On les combine dans une classe `Retriever` qui interroge les deux index en parallèle et fusionne les résultats.

Les deux classes `VectorIndex` et `BM25Index` partagent la même API (`add_document()` et `search()`), ce qui rend la combinaison simple.

La formule : 

	RRF_score(d) = Σ(1 / (k + rank_i(d)))

|Chunk|Rang vecteur|Rang BM25|Score RRF|
|---|---|---|---|
|Section 2|1|2|1/(1+1) + 1/(1+2) = **0.833**|
|Section 6|3|1|1/(1+3) + 1/(1+1) = **0.750**|
|Section 7|2|3|1/(1+2) + 1/(1+3) = **0.583**|
Implémentation : 

```
class Retriever:
    def __init__(self, *indexes: SearchIndex):
        if len(indexes) == 0:
            raise ValueError("At least one index must be provided")
        self._indexes = list(indexes)

    def add_document(self, document: Dict[str, Any]):
        for index in self._indexes:
            index.add_document(document)

    def search(self, query_text: str, k: int = 1, k_rrf: int = 60):
        all_results = []
        for idx, results in enumerate(all_results):
            for rank, (doc, _) in enumerate(results):
                # calcul RRF et fusion
        # retourner les résultats triés
```

Puisque tous les index implémentent le même protocole `SearchIndex`, on peut en ajouter autant qu'on veut (recherche par mots-clés, par graphe, par domaine spécialisé...) sans modifier le reste du code. Le `Retriever` les intègre automatiquement dans la fusion.

## Features 

### Extended thinking 

Extended thinking : fonctionnalité qui donne à Claude le temps de raisonner sur un problème avant de générer sa réponse finale. C'est le "brouillon" de Claude : on peut voir le processus de réflexion qui mène à la réponse. La réponse contient alors deux parties : le raisonnement intermédiaire et la réponse finale. Meilleur raisonnement sur les tâches complexes mais coût plus élevé

Pour l'utiliser de manière optimale, on commence sans thinking, on optimise le prompt avec les évaluations, et si la précision n'est toujours pas satisfaisante, on active l'extended thinking. C'est un outil de dernier recours, pas un réflexe par défaut.

Note : l'extended thinking est incompatible avec certaines fonctionnalités comme le prefilling et la température. La liste complète est dans la documentation Anthropic.

Les blocs de thinking incluent une signature cryptographique qui garantit que le texte de raisonnement n'a pas été modifié. Cela empêche de manipuler le raisonnement de Claude pour l'orienter dans des directions non souhaitées.

Parfois Claude retourne un bloc de thinking chiffré au lieu du raisonnement lisible. Cela se produit quand le contenu du raisonnement est signalé par les systèmes de sécurité internes. Le contenu chiffré peut quand même être renvoyé à Claude dans les échanges suivants sans perdre le contexte.

Implémentation : 

```
def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    thinking=False,
    thinking_budget=1024
):
[...]
if thinking:
    params["thinking"] = {
        "type": "enabled",
        "budget": thinking_budget
    }
[...]    
chat(messages, thinking=True)
```

### Images

On inclut un bloc image dans le message utilisateur, aux côtés d'un bloc texte. L'image est encodée en base64 : 

```
with open("image.png", "rb") as f:
    image_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

add_user_message(messages, [
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": image_bytes,
        }
    },
    {
        "type": "text",
        "text": "What do you see in this image?"
    }
])
```

Limites à connaître :
- Maximum 100 images par requête
- Taille maximale de 5 Mo par image
- Une seule image : max 8000px de hauteur/largeur
- Plusieurs images : max 2000px de hauteur/largeur
- Coût en tokens : (largeur × hauteur) / 750

Les mêmes techniques de prompt engineering s'appliquent aux images. Un prompt simple donne de mauvais résultats. On peut améliorer drastiquement la précision en fournissant une méthodologie détaillée, des exemples (one-shot/multi-shot), ou en décomposant la tâche en étapes.

Exemple pour compter des objets :

```
Analyze this image of marbles and determine the exact count using this methodology:
1. Begin by identifying each unique marble one at a time. Assign each a number as you identify it.
2. Verify your result by counting with a different method. Start from the bottom-left corner and work row by row, from left to right.
```

### Documents PDF

Le code est quasiment identique à celui des images, avec quatre différences : 

```
with open("earth.pdf", "rb") as f:
    file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

add_user_message(messages, [
    {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": file_bytes,
        }
    },
    {"type": "text", "text": "Summarize the document in one sentence"}
])
```

Claude peut extraire le texte, analyser les images et graphiques intégrés, lire les tableaux, et comprendre la structure du document.

### Citations

Sans citations, quand Claude répond à partir d'un document fourni, l'utilisateur ne sait pas d'où vient l'information. Les citations créent un lien transparent entre la réponse de Claude et le texte source exact.

On ajoute deux champs au bloc document : `title` et `citations` :

```
{
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": file_bytes,
    },
    "title": "earth.pdf",
    "citations": { "enabled": True }
}
```

Quand les citations sont activées, la réponse de Claude contient des données structurées pour chaque affirmation :

- `cited_text` : le texte exact du document qui supporte l'affirmation
- `document_index` : quel document est référencé (utile avec plusieurs documents)
- `document_title` : le titre du document
- `start_page_number` / `end_page_number` : les pages concernées

Les citations fonctionnent aussi avec des sources texte. Au lieu de numéros de page, on obtient des positions en caractères : 

```
{
    "type": "document",
    "source": {
        "type": "text",
        "media_type": "text/plain",
        "data": article_text,
    },
    "title": "earth_article",
    "citations": { "enabled": True }
}
```

Les citations sont particulièrement utiles quand les utilisateurs ont besoin de vérifier l'information, quand on travaille avec des documents de référence, ou quand la transparence sur les sources est critique pour l'application.

### Prompt caching

Avant de générer une réponse, Claude effectue un prétraitement important :

1. Tokenisation du prompt
2. Création des embeddings pour chaque token
3. Contextualisation selon les mots environnants
4. Génération de la réponse

Sans caching, tout ce travail est jeté après chaque requête. Si on envoie une requête suivante avec le même contenu, Claude recommence tout depuis zéro. 

Avec le caching, Claude sauvegarde les résultats du prétraitement au lieu de les jeter. Les requêtes suivantes contenant le même contenu réutilisent ce travail déjà effectué.

Limitations :

- Le cache expire après 1 heure
- Utile uniquement quand le même contenu est envoyé de façon répétée
- Nécessite une fréquence élevée pour être vraiment rentable

#### Implémentation

Le caching n'est pas automatique. On doit ajouter manuellement des "cache breakpoints" à des blocs spécifiques. Tout le contenu avant le breakpoint sera mis en cache.

Pour ajouter un breakpoint, on utilise la forme longue d'un bloc texte avec le champ `cache_control` :

```
{
    "type": "text",
    "text": "mon contenu",
    "cache_control": {"type": "ephemeral"}
}
```

Règles importantes :

- Le contenu doit être identique jusqu'au breakpoint pour que le cache soit réutilisé et le moindre changement invalide le cache.
- Minimum 1024 tokens de contenu pour être éligible au caching.
- Maximum 4 breakpoints par requête.

Claude traite les composants dans cet ordre :      
- Outils => System prompt => Messages.       

Pour mettre en cache des outils, on ajoute le `cache_control` au dernier outil de la liste, en travaillant sur des copies pour ne pas modifier les originaux : 

```
if tools:
    tools_clone = tools.copy()
    last_tool = tools_clone[-1].copy()
    last_tool["cache_control"] = {"type": "ephemeral"}
    tools_clone[-1] = last_tool
    params["tools"] = tools_clone
```

Pour mettre en cache le system prompt (meilleur candidat pour le caching), on convertit le system prompt d'une chaîne simple en bloc structuré : 

```
if system:
    params["system"] = [
        {
            "type": "text",
            "text": system,
            "cache_control": {"type": "ephemeral"}
        }
    ]
```

