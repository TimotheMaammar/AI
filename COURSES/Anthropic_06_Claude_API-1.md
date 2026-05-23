# Building with the Claude API (1/2)

Claude traite tout texte reçu en quatre étapes :
1. Tokenisation : le texte est découpé en tokens (mots, parties de mots, ponctuation, espaces, etc.).
2. Embedding : chaque token est converti en une liste de nombres qui encode toutes ses significations possibles.
3. Contextualisation : Claude ajuste ces représentations numériques en fonction du contexte (les mots autour) pour déterminer le sens le plus probable.
4. Génération : Claude calcule la probabilité de chaque mot suivant possible, puis choisit en mélangeant probabilité et une part de hasard contrôlé, ce qui donne des réponses naturelles et variées. Il répète cette opération mot par mot jusqu'à s'arrêter.

Après chaque token généré, Claude vérifie trois conditions :
- Le max_tokens est atteint
- Il a produit un token de fin de séquence (fin naturelle)
- Il a rencontré une "stop sequence" définie à l'avance

Quand on utilise l'API Claude, elle renvoie à chaque requête un objet structuré avec : 
- Texte généré
- Nombre de tokens utilisés
- Raison de l'arrêt

## Setup minimaliste

```
pip install anthropic python-dotenv
ANTHROPIC_API_KEY="XXX"
```

```
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-0"


message = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence"
        }
    ]
)

print(message.content[0].text)
```

Chaque appel à l'API est totalement indépendant et Claude n'a donc pas de mémoire entre les requêtes quand on scripte de cette façon. On doit gérer l'historique nous-mêmes en sauvegardant dans une liste et en renvoyant l'intégralité à chaque fois :

```
def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message.content[0].text
    
messages = []

add_user_message(messages, "Define quantum computing in one sentence")
answer = chat(messages)

add_assistant_message(messages, answer)

add_user_message(messages, "Write another sentence")
final_answer = chat(messages)
```

## System prompts

Sans system prompt, Claude répond de façon générique. Avec, on peut définir son rôle, son ton et son comportement pour un cas d'usage précis. 

```
system_prompt = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""

client.messages.create(
    model=model,
    messages=messages,
    max_tokens=1000,
    system=system_prompt
)
```

L'API n'accepte pas `system=None`, donc il faut inclure le paramètre de façon conditionnelle :

```
def chat(messages, system=None):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text
```

## Température

La température est un nombre entre 0 et 1 qui modifie la façon dont Claude choisit parmi les probabilités.

- **Proche de 0** : Claude choisit presque toujours le token le plus probable. Les réponses sont prévisibles et cohérentes.
- **Proche de 1** : les probabilités se répartissent plus équitablement entre les options. Les réponses sont plus variées et créatives.

On peut aussi ajouter ce paramètre avec un simple `"temperature": X` dans la fonction.

## Streaming

Sans streaming, le serveur attend que Claude ait fini de générer toute sa réponse avant de renvoyer quoi que ce soit. Sur des réponses longues, ça peut prendre 10 à 30 secondes. L'utilisateur fixe un écran vide.

Avec le streaming activé, Claude envoie le texte au fur et à mesure qu'il le génère, chunk par chunk. L'utilisateur voit la réponse s'afficher mot par mot, ce qui donne une impression de rapidité bien meilleure.

Quand le streaming est actif, Claude envoie plusieurs types d'événements : 

MessageStart => Début d'un nouveau message
ContentBlockStart => Début d'un bloc de contenu
ContentBlockDelta => Morceau de texte généré (c'est ce qui nous intéresse)
ContentBlockStop => Fin du bloc en cours
MessageDelta => Message complet
MessageStop => Fin de la réponse

Code minimaliste pour récupérer et stocker le texte en temps réel : 

```
with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=messages
) as stream:
    for text in stream.text_stream:
        pass  # envoie chaque chunk au client

    final_message = stream.get_final_message()
```

## Nettoyage de réponse

Par défaut, quand on demande à Claude de générer du JSON, on obtient du JSON mais enveloppé dans du Markdown et accompagné de texte. 

Solution : Faire du prefilling et utiliser une stop sequence astucieuse.

```
messages = []

add_user_message(messages, "Generate a very short event bridge rule as json")
add_assistant_message(messages, "```json")

text = chat(messages, stop_sequences=["```"])
```

1. Le message `user` demande le JSON
2. Le message `assistant` prefilled fait croire à Claude qu'il a déjà commencé un bloc Markdown
3. Claude continue en écrivant uniquement le contenu JSON
4. Quand Claude essaie de fermer le bloc avec ` ``` `, la stop sequence arrête immédiatement la génération

On obtient du JSON propre, sans aucune mise en forme autour. Et si jamais il reste des sauts de ligne, il suffira de passer le texte obtenu dans un strip().

Cette technique s'applique évidemment aussi à tout contenu structuré qu'on veut sans commentaires (Python, CSV, etc.).

## Prompt Evaluation

Prompt Engineering = Ensemble des techniques pour écrire de meilleurs prompts : multishot prompting, structuration avec des balises XML, bonnes pratiques diverses. L'objectif est de faire comprendre à Claude exactement ce qu'on attend de lui.

Prompt Evaluation = Démarche de tests automatisés pour mesurer à quel point un prompt fonctionne réellement. On peut tester sur des réponses attendues, comparer plusieurs versions d'un même prompt, détecter des erreurs, etc.

Faire passer un prompt par un pipeline d'évaluation pour le scorer est plus coûteux et chronophage mais permet de totalement le fiabiliser. Très important pour le scaling.

Étapes : 
1. Écrire un prompt de départ
2. Créer un dataset d'évaluation qui va complémenter ce prompt
3. Envoyer chaque question à Claude
4. Noter les réponses et en faire la moyenne
5. Modifier le prompt et recommencer

Pour noter les réponses on utilise généralement un "grader" qui peut être :
- Un code grader (évaluation programmatique sur des chiffres mesurables)
- Un model grader (autre appel API pour évaluer)
- Un human grader (notation manuelle par des humains)

## Prompt Engineering

Cycle simple à répéter jusqu'à obtenir les résultats voulus :

1. Définir un objectif
2. Écrire un premier prompt
3. Évaluer et tester le prompt sur les critères définis
4. Améliorer le prompt
5. Vérifier que les changements ont bien amélioré les scores

```
evaluator = PromptEvaluator(max_concurrent_tasks=5)

dataset = evaluator.generate_dataset(
    task_description="Write a compact, concise 1 day meal plan for a single athlete",
    prompt_inputs_spec={
        "height": "Athlete's height in cm",
        "weight": "Athlete's weight in kg",
        "goal": "Goal of the athlete",
        "restrictions": "Dietary restrictions of the athlete"
    },
    output_file="dataset.json",
    num_cases=3
)

def run_prompt(prompt_inputs):
    prompt = f"""
What should this person eat?

- Height: {prompt_inputs["height"]}
- Weight: {prompt_inputs["weight"]}
- Goal: {prompt_inputs["goal"]}
- Dietary restrictions: {prompt_inputs["restrictions"]}
"""
    messages = []
    add_user_message(messages, prompt)
    return chat(messages)
    
results = evaluator.run_evaluation(
    run_prompt_function=run_prompt,
    dataset_file="dataset.json",
    extra_criteria="""
The output should include:
- Daily caloric total
- Macronutrient breakdown
- Meals with exact foods, portions, and timing
"""
)
```

Au-delà de fournir des guidelines précises et de bien verbaliser sa demande, il peut être très pertinent de séparer les instructions et les données avec des balises XML : 

```
<athlete_information>
- Height: 6'2"
- Weight: 180 lbs
- Goal: Build muscle
- Dietary restrictions: Vegetarian
</athlete_information>

Generate a meal plan based on the athlete information above.
```

```
<sample_input>
[entrée exemple]
</sample_input>

<ideal_output>
[sortie idéale]
</ideal_output>

This example is well-structured, provides detailed information
on food choices and quantities, and aligns with the athlete's
goals and restrictions.
```

