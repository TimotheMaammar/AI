# Scaling Laws for Neural Language Models

## Références

Titre complet : "Scaling Laws for Neural Language Models"

Lien : <https://arxiv.org/abs/2001.08361>

Date : 23/01/2020

Entreprise : OpenAI

Chercheurs : Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jeffrey Wu, Dario Amodei

Autre papier lié : <https://arxiv.org/abs/1812.06162> ("An Empirical Model of Large-Batch Training")

## Abstract

Les auteurs étudient empiriquement les lois d'échelle qui régissent la performance des modèles de langage Transformer sur la cross-entropy loss. La loss suit une power-law avec la taille du modèle N, la taille du dataset D, et la compute C utilisée pour l'entraînement, avec des tendances qui s'étendent sur plus de sept ordres de grandeur. Les autres détails architecturaux comme la largeur ou la profondeur du réseau ont des effets minimes dans une large plage.

Des équations simples gouvernent la dépendance de l'overfitting à la taille modèle/dataset et la dépendance de la vitesse d'entraînement à la taille du modèle. Ces relations permettent de déterminer l'allocation optimale d'un budget de compute fixé.

Conclusion centrale : les modèles plus grands sont significativement plus sample-efficient. L'entraînement optimal en compute consiste à entraîner de très grands modèles sur une quantité de données relativement modeste, et à arrêter significativement avant la convergence.

Définitions utiles : 
- Loss =  Nombre qui mesure à quel point le modèle se trompe
- Cross-entropy loss = Forme particulière de loss qui mesure la "surprise" d'un modèle dans la prédiction de probabilités
- Power-law = Relation mathématique où une quantité varie comme une puissance d'une autre
- Overfitting = Cas où un modèle apprend "trop bien" ses données d'entraînement au point de mémoriser leurs détails et leur bruit au lieu d'apprendre les régularités générales
- Têtes d'attention = Mécanismes parallèles qui regardent chacun les relations entre les mots d'une phrase sous un angle différent
- Feed-forward = Petit réseau de neurones appliqué à chaque mot après l'étape d'attention

## Contenu

### Setup expérimental

Les auteurs entraînent une grande variété de modèles Transformer décodeur-only sur WebText2 (extension du dataset WebText), en variant :

- Taille du modèle : de 768 à 1.5 milliard de paramètres non-embedding
- Taille du dataset : de 22 millions à 23 milliards de tokens
- Forme architecturale : profondeur, largeur, têtes d'attention, dimension feed-forward
- Longueur de contexte : 1024 pour la plupart
- Batch size : 2^19 = 524288 tokens pour la plupart

### Les sept résultats clés

1. **La performance dépend fortement de l'échelle, faiblement de la forme** : la performance dépend essentiellement de N, D, C. Les hyperparamètres architecturaux (profondeur vs largeur) ont un effet négligeable dans une plage large.

2. **Power-laws lisses** : la loss suit une relation power-law avec chacun des trois facteurs N, D, C quand les deux autres ne sont pas le goulot d'étranglement, sur plus de six ordres de grandeur. Aucun signe de déviation observé en haut de l'échelle (même si la loss doit forcément finir par se stabiliser puisque l'entropie du langage naturel est non-nulle).

3. **Universalité de l'overfitting** : la performance s'améliore prévisiblement tant qu'on scale N et D ensemble, mais entre dans un régime de rendements décroissants si l'un est fixé pendant que l'autre augmente. La pénalité dépend du ratio N^0.74 / D : pour multiplier N par 8, il suffit de multiplier D par environ 5 pour éviter la pénalité.

4. **Universalité de l'entraînement** : les courbes d'entraînement suivent des power-laws prévisibles dont les paramètres sont presque indépendants de la taille du modèle. En extrapolant le début d'une courbe, on peut prédire la loss qu'elle atteindrait avec un entraînement beaucoup plus long.

5. **Le transfert s'améliore avec la performance de test** : évalués sur des distributions de texte différentes de l'entraînement, les modèles montrent une loss fortement corrélée à celle sur la validation, avec un offset constant. Transférer vers une autre distribution coûte une pénalité constante mais s'améliore au même rythme.

6. **Sample efficiency** : les grands modèles sont plus sample-efficient que les petits, atteignant le même niveau de performance avec moins de steps d'optimisation et moins de données.

7. **La convergence est inefficace** : avec un budget de compute C fixé sans contrainte sur N ou D, la performance optimale s'obtient en entraînant de très grands modèles et en s'arrêtant significativement avant la convergence. Les besoins en données croissent très lentement, comme D proportionnel à C^0.27 avec la compute.


## Quelques conclusions

- Les Transformer language models s'améliorent de façon lisse et prévisible quand on scale N, D, et C ensemble. Les power laws gouvernent cette amélioration sur 7+ ordres de grandeur.

- Les détails architecturaux (largeur vs profondeur, nombre de têtes, etc.) ont un impact très mineur comparé à l'échelle globale. Les paramètres d'embedding doivent être exclus du compte N pour obtenir des trends propres.

- L'entraînement compute-efficient implique d'entraîner des modèles plus grands que ce que font typiquement les chercheurs, sur moins de données, sans aller jusqu'à la convergence. "Big models may be more important than big data".

- Les grands modèles sont plus sample-efficient. Cela suggère que les améliorations futures passeront principalement par l'augmentation de la taille des modèles plutôt que par celle des datasets.

- Les contraintes pratiques d'aujourd'hui (mémoire GPU, parallélisme) poussent les chercheurs à entraîner des modèles plus petits que l'optimum compute. Le model parallelism (pipelining, sparsity, branching) est une direction de recherche importante.

- Conjecture ouverte : les scaling laws pourraient s'appliquer à d'autres tâches de modélisation générative (images, audio, vidéo). Une "mécanique statistique" sous-jacente pourrait dériver ces lois et leurs corrections.
