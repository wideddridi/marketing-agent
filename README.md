# Intelligent Marketing Campaign Agent
 
Projet de fin d'année (Master Data Science et IA, 2e année) : un agent intelligent
d'aide aux campagnes marketing bancaires.
 
## Objectif
Prédire quels clients sont susceptibles de souscrire à un dépôt à terme, puis répondre
à des questions métier avec des chiffres vérifiés et des documents de référence.
 
## Architecture prévue
- **Modèle prédictif** : comparaison d'une baseline (Dummy), d'une régression
  logistique et de XGBoost ; interprétation avec SHAP.
- **Outils de l'agent** : requêtes SQL (calculs exacts), modèle de prédiction,
  explications SHAP, recherche documentaire (RAG).
- **Trois agents** : planificateur, analyste, critique (LangGraph).
- **Évaluation** : LLM seul, LLM avec outils, système complet.
- **Déploiement** : FastAPI, Streamlit, Docker. MLOps seulement si le temps le permet.
## État d'avancement
- [x] Étape 1 : cadrage, environnement, récupération des données
- [x] Étape 2 : exploration, nettoyage et préparation des données
- [ ] Étape 3 : modélisation (en cours)
- [ ] Étape 4 : outils (SQL, RAG)
- [ ] Étape 5 : agents
- [ ] Étape 6 : évaluation
- [ ] Étape 7 : application et déploiement
## Installation
```bash
conda env create -f environment.yml
conda activate marketing-agent
```
Pour mettre à jour un environnement existant après une modification de `environment.yml` :
```bash
conda env update -f environment.yml --prune
```
 
## Données
Les données ne sont pas incluses dans le dépôt. Télécharge le jeu **Bank Marketing**
sur l'UCI Machine Learning Repository (<https://archive.ics.uci.edu/dataset/222/bank+marketing>)
et place le fichier `bank-additional-full.csv` dans `data/raw/`.
 
Source : S. Moro, P. Cortez, P. Rita, *A Data-Driven Approach to Predict the Success of
Bank Telemarketing*, Decision Support Systems, 62:22-31, 2014.
 
## Notebooks (à exécuter dans l'ordre)
| Notebook | Rôle |
|---|---|
| `01_exploration.ipynb` | exploration, décisions de nettoyage, graphiques, analyse temporelle |
| `02_preparation.ipynb` | découpage train / validation / test (chronologique et aléatoire) |
| `03_modelisation.ipynb` | prétraitement, baseline, régression logistique, XGBoost (en cours) |
 
Les décisions et leur justification sont détaillées dans [`docs/notes.md`](docs/notes.md).
 
## Principaux constats (exploration)
- **Cible déséquilibrée** : 11,3 % de « yes ». L'exactitude (accuracy) seule serait trompeuse ;
  on utilise PR-AUC, rappel, précision, F1 et lift.
- **`duration` exclue des variables du modèle** : la durée de l'appel n'est connue qu'après
  l'appel (fuite de données). Elle est conservée pour une expérience d'ablation (avec / sans).
- **Dérive temporelle** : le fichier est trié par date (mai 2008 à novembre 2010) et le taux de
  souscription passe de 4,8 % (2008) à 52,1 % (2010). Les variables macro-économiques
  (`euribor3m`…) suivent le temps et peuvent servir de substitut à la période.
- **Découpage principal chronologique** (70 % / 15 % / 15 %) : l'agent devra prédire pour des
  clients futurs. Un découpage aléatoire stratifié sert de comparaison pour mesurer la
  dépendance à l'époque.
## Limites connues
- L'année est **reconstruite** à partir de l'ordre des lignes (le fichier ne contient que le mois).
- Le taux de « yes » diffère fortement entre les jeux chronologiques (train 5,6 %, val 10,6 %,
  test 38,4 %) : les métriques dépendant du taux (PR-AUC) se comparent à la baseline du **même** jeu.
- L'exploration a été faite sur l'ensemble des lignes, y compris celles du futur jeu de test.
## Structure du dépôt
```
data/        données brutes (raw) et préparées (clean), ignorées par Git
notebooks/   exploration, préparation, modélisation
src/         code final
tests/       tests
docs/        notes et décisions
```
 
## Tests
Depuis la racine du projet :
```bash
python -m pytest
```