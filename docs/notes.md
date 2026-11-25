# Notes du projet : décisions et observations
 
## 14 novembre 2026 : nettoyage et exploration terminés (étape 2)
 
Ce fichier garde la trace de **ce qui a été fait, pourquoi, et ce qu'on a observé**. Tous les chiffres viennent du notebook `notebooks/01_exploration.ipynb` (après suppression des doublons, sauf indication contraire).
 
---
 
## 1. Les données
 
- Fichier : `bank-additional-full.csv` (UCI Bank Marketing), séparateur `;`.
- 41 188 lignes, 21 colonnes (10 numériques, 11 texte dont la cible `y`).
- Aucune valeur nulle (`NaN`).
- Le fichier est trié par date, de mai 2008 à novembre 2010 (voir la section 5).
## 2. Qualité des données
 
### 2.1 Valeurs `unknown` (sur les 41 188 lignes d'origine)
 
Les valeurs manquantes sont codées par le texte `unknown`.
 
| Colonne | unknown | Part |
|---|---|---|
| default | 8 597 | 20,9 % |
| education | 1 731 | 4,2 % |
| housing | 990 | 2,4 % |
| loan | 990 | 2,4 % |
| job | 330 | 0,8 % |
| marital | 80 | 0,2 % |
 
**Décision :** conserver `unknown` comme une catégorie à part, sans supprimer de lignes.
**Pourquoi :** un client qui n'a pas répondu à une question n'est pas un client « moyen », et pour `default` on verra que cette catégorie se comporte différemment (section 3.6).
 
### 2.2 Doublons
 
- 12 lignes en double sur 41 188 (0,03 %), identiques sur toutes les colonnes.
- **Décision :** suppression avec `drop_duplicates()`, puis `reset_index(drop=True)`. Résultat : **41 176 lignes**.
- **Pourquoi :** un doublon compte deux fois la même information. `reset_index(drop=True)` renumérote les lignes sans changer leur ordre, ce qui est essentiel car l'ordre du fichier est l'ordre chronologique.
- La suppression se fait **avant** de retirer `duration`, pour comparer les lignes complètes.
### 2.3 La cible `y`
 
- no : 36 548 (88,73 %) ; yes : 4 640 (11,27 %).
- Le jeu est **déséquilibré** : un modèle qui répond toujours « no » aurait 88,7 % d'exactitude sans rien apprendre.
- **Décision :** ne pas utiliser l'accuracy seule. Métriques retenues : PR-AUC, rappel, précision, F1, lift.
---
 
## 3. Décisions de nettoyage et transformations
 
Résumé :
 
| Sujet | Décision | Pourquoi (en une phrase) |
|---|---|---|
| Doublons | supprimés (12) | information comptée deux fois |
| `duration` | retirée des variables du modèle | fuite de données |
| `pdays` | remplacée par `deja_contacte` et `pdays_jours` | 999 ne veut pas dire « jamais contacté » |
| `housing` / `loan` | `unknown` conservé | mêmes 990 lignes, peu informatives |
| `default` | `yes` fusionné avec `no` | 3 clients seulement |
| `education` | `illiterate` fusionné avec `basic.4y` | 18 clients seulement |
| `campaign` | conservée, avec une copie plafonnée à 20 | valeurs extrêmes réelles mais gênantes pour la régression logistique |
| `age` > 80 | conservés | cohérents (retraités), taux élevé |
| `y_num` | colonne 0/1 créée | pour calculer des taux |
 
### 3.1 `duration` : retirée (fuite de données)
 
- La durée de l'appel n'est connue qu'**après** l'appel. Au moment où l'on décide d'appeler un client, on ne peut pas la connaître.
- Une variable qui « contient la réponse » donnerait des scores excellents mais inutilisables en vrai : c'est une **fuite de données**.
- **Décision :** retirée du modèle de référence. Elle sera gardée à part pour l'**ablation** (comparer les performances avec et sans `duration`) : dans `02_preparation.ipynb`, on la laisse dans les fichiers sauvegardés mais on ne la met pas dans les variables d'entrée.
### 3.2 `y_num` : la cible en version numérique
 
- `y` contient du texte (« yes » / « no »), on ne peut pas calculer une moyenne dessus.
- `y_num` vaut 1 pour « yes » et 0 pour « no » : sa moyenne est directement le **taux de souscription**.
- C'est la cible : elle ne doit jamais être parmi les variables d'entrée.
### 3.3 `pdays`, `previous`, `poutcome` : ce qu'il faut bien comprendre
 
**Les trois colonnes :**
- `pdays` : nombre de jours depuis le dernier contact de la campagne précédente. La valeur 999 est un code qui veut dire « pas de valeur ».
- `previous` : nombre de contacts faits avec ce client avant la campagne actuelle.
- `poutcome` : résultat de la campagne précédente (`nonexistent`, `failure`, `success`).
**Constat :** `pdays = 999` concerne 96,3 % des lignes, mais seulement **86,3 %** des clients (35 551) sont réellement jamais contactés (`previous = 0`). Il y a **4 110 clients** avec `pdays = 999` mais `previous ≥ 1` : ils ont été contactés, seul le délai n'est pas renseigné.
 
**Vérification :** `previous > 0` et `poutcome != "nonexistent"` donnent exactement la même réponse sur les 41 176 lignes (aucune exception). Une seule des deux suffit pour définir « déjà contacté ». Le notebook contient un `assert` qui le contrôle à chaque exécution.
 
**Décision :** remplacer `pdays` par deux variables :
- `deja_contacte` = 1 si `previous > 0`, sinon 0 (5 625 clients à 1, 35 551 à 0) ;
- `pdays_jours` = le nombre de jours, et **-1** quand `pdays = 999`.
**Pourquoi -1 et pas 0 :** la valeur 0 existe vraiment dans les données (15 clients contactés le jour même de leur contact précédent).
 
**Attention :** `pdays_jours = -1` mélange deux situations :
 
| deja_contacte | pdays_jours | Signification | Clients |
|---|---|---|---|
| 0 | -1 | jamais contacté | 35 551 |
| 1 | -1 | contacté, délai inconnu | 4 110 |
| 1 | ≥ 0 | contacté, délai connu | 1 515 |
 
La combinaison des deux variables permet de distinguer ces trois cas.
 
**Correction d'une erreur précédente :** une première version définissait `deja_contacte` avec `pdays != 999`, ce qui classait à tort les 4 110 clients ci-dessus comme « jamais contactés ». C'est corrigé.
 
### 3.4 `housing` et `loan`
 
- Ils ont chacun 990 `unknown`, et la vérification montre que ce sont **exactement les mêmes clients**. Probablement un problème de collecte pour ces 990 clients.
- Le taux de souscription est presque identique pour toutes les modalités (≈ 11 %) : ces variables semblent peu informatives. On garde `unknown` comme catégorie et c'est le modèle qui tranchera.
### 3.5 `default` : une modalité trop rare
 
- Répartition : `no` 32 577, `unknown` 8 596, `yes` seulement **3**.
- **Décision :** fusionner `yes` avec `no`. **Pourquoi :** avec 3 clients (tous à `y = 0`, ce qui peut être dû au hasard), un modèle ne peut rien apprendre de fiable. La régression logistique donnerait un coefficient extrême et instable, et en split il est possible que les 3 lignes tombent toutes dans le test. L'effet sur les résultats est négligeable (3 lignes sur 41 176).
- **`unknown` est conservée :** 20,9 % des clients, taux de souscription de **5,2 %** contre **12,9 %** pour `no`. Cette catégorie porte de l'information : ce n'est pas un simple « manquant » à remplacer.
### 3.6 `education` : une modalité trop rare
 
- `illiterate` n'a que 18 clients (4 « yes », soit 22 %, mais trop peu pour conclure).
- **Décision :** fusionner avec `basic.4y` (le niveau le plus proche). `basic.4y` passe de 4 176 à 4 194 clients.
- `unknown` (1 730 clients) est conservée : son taux est de 14,5 %.
### 3.7 `campaign` : des valeurs extrêmes qui ne sont pas des erreurs
 
- Maximum : 56 contacts pour un même client ; 157 clients ont plus de 20 contacts.
- Taux de souscription par nombre de contacts :
| campaign | Taux |
|---|---|
| 1 | 13,0 % |
| 2 à 3 | 11,2 % |
| 4 à 5 | 8,7 % |
| 6 à 10 | 6,3 % |
| 11 à 20 | 3,7 % |
| plus de 20 | 0,6 % |
 
- Les valeurs élevées sont de vrais clients très sollicités qui ne souscrivent presque jamais. **On ne supprime aucune ligne.**
- **Décision :** garder `campaign` telle quelle (pour XGBoost) et créer `campaign_plafonnee` (valeurs > 20 ramenées à 20) pour la régression logistique, sensible aux valeurs extrêmes.
- Intérêt pour l'agent : au-delà de quelques contacts, relancer un client ne sert presque plus à rien.
### 3.8 Clients de plus de 80 ans
 
- 119 clients : 105 `retired`, 12 `housemaid`, 2 `unknown`. Cohérent, pas des erreurs de saisie.
- Taux de souscription : **49,6 %**, très au-dessus de la moyenne (11,3 %).
- **Décision :** les garder. Cette tranche d'âge sera probablement utile au modèle.
---
 
## 4. Exploration : chaque graphique, son rôle et ce qu'on y a lu
 
Deux questions guident l'exploration : *à quoi ressemblent les données ?* (distributions) et *qui souscrit le plus ?* (taux par catégorie). Dans les graphiques de taux, la ligne rouge est la moyenne globale (11,3 %) et `n` est l'effectif de chaque groupe (un taux calculé sur très peu de clients est peu fiable).
 
### 4.1 Répartition de la cible (diagramme en barres)
- **Pourquoi :** voir le déséquilibre entre « no » et « yes ».
- **Lecture :** 88,7 % de « no » contre 11,3 % de « yes ».
- **Conséquence :** utiliser PR-AUC, rappel, précision, F1, lift, pas l'accuracy seule.
### 4.2 Distribution des variables numériques (histogrammes)
- **Pourquoi :** voir la **forme** de chaque variable (symétrique, asymétrique, valeurs répétées) avant de choisir les transformations.
- **Lecture :** `campaign` et `previous` sont très asymétriques (beaucoup de petites valeurs, quelques grandes). Les variables macro-économiques (`emp.var.rate`, `euribor3m`, `nr.employed`…) forment des blocs de valeurs répétées : ce sont des indicateurs mensuels communs à tous les clients d'une période, pas des mesures propres à chaque client.
- **Conséquence :** plafonnement de `campaign` ; méfiance envers les variables macro (voir section 5).
- Pour `pdays_jours`, on retire les `-1` du graphique : c'est un code « inconnu », pas une vraie durée.
### 4.3 Distribution des variables catégorielles (barres triées)
- **Pourquoi :** repérer les **catégories rares** et les déséquilibres avant l'encodage.
- **Lecture :** `default = yes` et `illiterate` sont rares (d'où les fusions), `poutcome = success` ne concerne que 1 373 clients, `default = unknown` est très fréquent.
### 4.4 Taux de souscription par catégorie (barres horizontales + moyenne globale)
- **Pourquoi :** c'est le graphique le plus utile : il montre **quels groupes de clients souscrivent plus ou moins que la moyenne**, ce que l'agent devra savoir.
| Variable | Ce qu'on lit |
|---|---|
| `job` | `student` 31,4 %, `retired` 25,3 % ; `blue-collar` 6,9 % (le plus bas), `services` 8,1 % |
| `poutcome` | `success` 65,1 %, `failure` 14,2 %, `nonexistent` 8,8 % |
| `deja_contacte` | 26,6 % si déjà contacté contre 8,8 % sinon : un client qui a déjà été contacté souscrit environ trois fois plus |
| `contact` | `cellular` 14,7 % contre `telephone` 5,2 % |
| `education` | de 7,8 % (`basic.9y`) à 13,7 % (`university.degree`) : effet modéré |
| `day_of_week` | de 10,0 % à 12,1 % : **quasi plat, peu utile** |
| `month` | très variable (6,4 % en mai, près de 50 % en mars, septembre, octobre, décembre), **mais trompeur** : voir la section 5 |
 
- Pour `month`, on affiche les mois dans l'ordre du calendrier (il n'y a ni janvier ni février dans le fichier).
### 4.5 Taux par tranche d'âge
- **Pourquoi des tranches :** l'âge brut a 78 valeurs différentes, donc du bruit. Les tranches font apparaître la **forme** de la relation.
- **Lecture :** courbe en **U** : 24,0 % pour les 17-24 ans, un minimum de 7,9 % pour les 40-49 ans, puis 34,7 % (60-69), 46,4 % (70-80) et 49,6 % (plus de 80).
- **Conséquence :** la relation n'est pas linéaire. Utiliser des tranches ou un modèle d'arbres (XGBoost), et ne pas en déduire que l'âge est « inutile » à cause de sa faible corrélation.
### 4.6 Matrice de corrélation (carte de chaleur)
- **Pourquoi :** répondre à deux questions : (1) deux variables disent-elles la même chose ? (2) une variable numérique est-elle liée à la cible ?
- **Lecture, redondance :** `emp.var.rate`, `euribor3m` et `nr.employed` sont très corrélées entre elles (0,91 à 0,97). `cons.price.idx` l'est aussi (0,52 à 0,78).
- **Conséquence :** pour la régression logistique, n'en garder qu'une ou deux (par exemple `euribor3m`), sinon les coefficients deviennent instables (multicolinéarité). XGBoost n'est pas gêné.
- **Lecture, lien avec la cible :** `nr.employed` -0,35, `euribor3m` -0,31, `emp.var.rate` -0,30, `previous` +0,23, `deja_contacte` +0,19. Aucune corrélation écrasante.
- **Limite :** la corrélation ne détecte que les relations « en ligne droite ». L'âge a une corrélation de 0,03 avec la cible alors qu'il existe une vraie relation en U. Elle ne s'applique pas non plus aux variables catégorielles. `pdays_jours` est exclue du calcul car son code -1 fausserait le résultat.
---
 
## 5. L'ordre temporel (découverte principale)
 
### Comment on a reconstruit l'année
- Le fichier est trié par date (documentation UCI) mais ne contient que le **mois**.
- On convertit le mois en nombre ; chaque fois que ce nombre **diminue** d'une ligne à l'autre (décembre → mars), on est passé à l'année suivante. On part de 2008.
- On trouve exactement **deux** retours en arrière, ce qui est cohérent avec une période de mai 2008 à novembre 2010.
- **C'est une hypothèse** (fichier supposé trié). Les colonnes `annee` et `periode` sont gardées dans un tableau à part : ce ne sont pas des variables du modèle.
### Pourquoi le mois seul est trompeur
Le même mois apparaît trois fois, avec des situations très différentes : par exemple mai 2008 (7 762 clients, 3,1 %), mai 2009 (5 793 clients, 9,0 %) et mai 2010 (212 clients, 57,5 %). Regrouper « mai » donne 6,4 %, qui ne représente aucune des trois situations.
 
### Ce qu'on observe
 
| Année | Clients | Taux de souscription |
|---|---|---|
| 2008 | 27 682 | 4,8 % |
| 2009 | 11 436 | 19,5 % |
| 2010 | 2 058 | 52,1 % |
 
- Le nombre d'appels chute après 2008, mais le taux de souscription augmente fortement.
- `euribor3m` baisse de 4,9 (2008) à environ 0,7 (2009-2010) : cet indicateur suit le temps et peut servir de **substitut de la période**.
- Les mois « à fort taux » (mars, septembre, octobre, décembre : 44 % à 51 %) sont des mois peu appelés (182 à 717 clients) qui tombent presque tous en 2009 et 2010 : c'est un **effet d'année**, pas une saisonnalité.
- Anomalie notée : octobre 2008 ne compte que 67 clients (62,7 % de « yes »), décembre 2008 que 10.
### Conséquences pour la suite
1. **Split chronologique** (entraîner sur le passé, tester sur le futur), pas aléatoire.
2. **Dérive du taux de souscription** : le jeu de test aura un taux très différent de celui du train (voir section 6). Les métriques dépendantes du taux (PR-AUC) ne sont pas comparables d'un jeu à l'autre : comparer chaque modèle à la baseline **sur le même jeu**.
3. **Variables macro** : risque que le modèle apprenne « période = 2010 ⇒ oui » plutôt qu'un comportement client. À garder en tête dans l'interprétation (SHAP) et à discuter dans le rapport.
---
 
## 6. Décisions pour la préparation (étape 2, suite)
 
- **Découpage chronologique 70 % / 15 % / 15 %** dans l'ordre du fichier, sans mélange (`train_test_split(..., shuffle=False)` appelé deux fois, dans une fonction `split_chronologique`).
- Tailles attendues : train 28 823, validation 6 176, test 6 177.
- Taux de souscription attendus : train 5,6 %, validation 10,6 %, test 38,4 % (dérive voulue par la chronologie, pas un bug).
- Répartition par année : le train contient 2008 et le début d'avril 2009 ; la validation, avril-mai 2009 ; le test, mai 2009 à novembre 2010 (toutes les lignes de 2010 sont dans le test).
- **Rôle des jeux :** train pour apprendre, validation pour comparer les modèles et régler les paramètres, test utilisé **une seule fois** à la fin.
- **Validation croisée :** pas utilisée à ce stade (un tirage aléatoire mélangerait passé et futur). Amélioration possible plus tard avec `TimeSeriesSplit`.
- Encodage et normalisation : dans un `Pipeline`, **ajusté uniquement sur le train** (à l'étape 3).
- Sauvegarde dans `data/processed/` (`train.csv`, `val.csv`, `test.csv`) : plus de fichier de nettoyage complet dans `data/clean/`, la préparation se rejoue à partir du fichier brut dans `02_preparation.ipynb`.
- `duration` conservée dans ces fichiers pour l'ablation, mais **exclue** des variables d'entrée du modèle de référence.
- Hypothèse à tester (ne pas supposer) : l'effet du délai depuis le dernier contact (`pdays_jours`) sur la souscription.
- Pour la comparaison dans le rapport : envisager aussi un split aléatoire stratifié (taux de 11,3 % dans chaque jeu) afin de montrer l'écart de performance avec le split chronologique.
---
 
## 7. Problèmes techniques rencontrés
 
- **Kernel Jupyter qui plante au premier graphique** (code de sortie `3228369023`, erreur Windows de DLL). Cause probable : bibliothèques de graphiques mélangées entre plusieurs canaux conda, et environnement non activé par VS Code (`Failed to get activated conda env vars`).
- **Piste de correction :** environnement recréé avec un seul canal (`conda-forge`) ; `environment.yml` mis à jour avec `seaborn` ; ne plus utiliser `pip install` dans cet environnement ; si besoin, lancer VS Code depuis un terminal où l'environnement est activé (`code .`) ou travailler dans `jupyter lab`.
- `requirements.txt` contient des chemins locaux (`file:///D:/bld/...`) : non réutilisable, `environment.yml` est la seule source de vérité.
---
 
## À faire
 
- [x] Relancer le notebook dans l'ordre et vérifier 41 176 lignes après doublons.
- [x] Analyser `unknown` (housing/loan, default) et les graphiques par métier, âge, `poutcome`.
- [x] Vérifier si le fichier est ordonné dans le temps (documentation UCI) : oui, deux retours en arrière de mois.
- [x] Créer `notebooks/02_preparation.ipynb` : charger le brut, rejouer le nettoyage, `split_chronologique`, vérifications, sauvegarde dans `data/processed/`.
- [x] Vérifier qu'aucune ligne de 2010 n'est dans le train (contrôle par l'année reconstruite).
- [ ] Déplacer le nettoyage et la fonction de split dans `src/`, avec un test (41 176 lignes, 0 doublon, somme des trois jeux = total).
- [ ] Étape 3 : baseline Dummy, régression logistique, XGBoost, SHAP, ablation `duration`.
 