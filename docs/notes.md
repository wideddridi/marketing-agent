# Notes du projet : décisions et observations

## 1er novembre 2026 : exploration et préparation (étape 2, en cours)

### Données
- Fichier : `bank-additional-full.csv` (UCI Bank Marketing), séparateur `;`.
- 41 188 lignes, 21 colonnes (10 numériques, 11 texte dont la cible `y`).
- Aucune valeur nulle (`NaN`) ; les valeurs manquantes sont codées `unknown`.

### Cible `y`
- no : 36 548 (88,73 %) ; yes : 4 640 (11,27 %).
- Jeu **déséquilibré** : l'exactitude (accuracy) seule serait trompeuse.
  Métriques retenues : PR-AUC, rappel, précision, F1, lift.

### Doublons
- 12 lignes en double sur 41 188 (0,03 %), identiques sur toutes les colonnes.
- Décision : suppression avec `drop_duplicates()`, **avant** de retirer `duration`.
- Attendu après suppression : 41 176 lignes. [à confirmer après relance du notebook]

### Valeurs `unknown` (sur les 41 188 lignes d'origine)
| Colonne | unknown | Part |
|---|---|---|
| default | 8 597 | 20,9 % |
| education | 1 731 | 4,2 % |
| housing | 990 | 2,4 % |
| loan | 990 | 2,4 % |
| job | 330 | 0,8 % |
| marital | 80 | 0,2 % |

- Décision : conserver `unknown` comme une catégorie à part (aucune suppression).
- À vérifier : `housing` et `loan` ont le même nombre (990), sont-ils manquants sur les mêmes lignes ?

### Variable `duration` (durée de l'appel)
- Connue seulement après l'appel : elle crée une fuite de données.
- Décision : retirée du modèle de référence. Conservée dans `df` pour l'ablation
  (comparer les performances avec et sans `duration`).

### Variable `pdays`
- 999 = client jamais contacté auparavant (≈ 96,3 % des clients).
- Décision : remplacée par deux variables :
  - `deja_contacte` (0/1) ;
  - `pdays_jours` : nombre de jours, **-1** si jamais contacté.
- Pourquoi -1 et non 0 : la valeur 0 existe réellement dans les données
  (contact le jour même).
- Vérification : nombre de -1 = nombre de `deja_contacte == 0` (True).
- Hypothèse à tester (ne pas supposer) : l'effet du délai depuis le dernier contact
  sur la souscription.

### Autres observations
- `age` : minimum 17, maximum 98 ; valeurs plausibles (clients retraités), conservées.
  [à vérifier : les plus de 80 ans sont-ils surtout `retired` ?]
- `campaign` : maximum 56 contacts pour un même client, valeur extrême à examiner.

## À faire
- [ ] Relancer le notebook dans l'ordre et vérifier 41 176 lignes après doublons.
- [ ] Analyser `unknown` (housing/loan, default) et les graphiques par métier, âge, `poutcome`.
- [ ] Vérifier si le fichier est ordonné dans le temps (documentation UCI).
- [ ] Séparer en train / validation / test et sauvegarder dans `data/processed/`.