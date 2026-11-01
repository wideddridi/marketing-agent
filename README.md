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
- [ ] Étape 2 : exploration et préparation des données (en cours)
- [ ] Étape 3 : modélisation
- [ ] Étape 4 : outils (SQL, RAG)
- [ ] Étape 5 : agents
- [ ] Étape 6 : évaluation
- [ ] Étape 7 : application et déploiement

## Installation
```bash
conda env create -f environment.yml
conda activate marketing-agent
```

## Données
Les données ne sont pas incluses dans le dépôt. Télécharge le jeu **UCI Bank Marketing**
sur le site de l'UCI Machine Learning Repository et place le fichier
`bank-additional-full.csv` dans `data/raw/`.

## Structure du dépôt
```
data/        données brutes (raw) et préparées (processed), ignorées par Git
notebooks/   exploration et expérimentations
src/         code final
tests/       tests
docs/        notes et décisions
```