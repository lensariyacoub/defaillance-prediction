# RiskVision AI — Prédiction du risque de défaillance d'entreprises

**RiskVision AI** est une application de Machine Learning développée avec Python et Streamlit permettant d'estimer et d'expliquer le risque de défaillance d'une entreprise à partir de caractéristiques issues des données disponibles.

Le projet couvre l'ensemble de la chaîne Data Science : préparation des données, feature engineering, entraînement et évaluation d'un modèle de classification, prédiction, explicabilité avec SHAP et déploiement d'une application web interactive.

---

## Objectif du projet

L'objectif est de construire un système capable de :

- analyser les caractéristiques d'une entreprise ;
- transformer automatiquement les informations en variables exploitables par le modèle ;
- estimer une probabilité de risque ;
- classer l'observation en **RISQUE** ou **NON RISQUE** ;
- expliquer les facteurs ayant influencé la prédiction ;
- conserver un historique des analyses ;
- générer un rapport PDF exploitable par l'utilisateur.

> RiskVision AI est un projet analytique et exploratoire. Les prédictions produites ne constituent pas une notation financière officielle.

---

## Fonctionnalités

### Analyse d'une entreprise

L'utilisateur renseigne notamment :

- le nom de l'entreprise ;
- le département ;
- le type d'entité.

RiskVision AI construit ensuite automatiquement l'observation nécessaire au modèle et affiche :

- le greffe identifié ;
- l'activité probable ;
- les variables transmises au modèle ;
- la classe prédite ;
- la probabilité de risque ;
- la probabilité de non-risque.

### Machine Learning

Le moteur de prédiction repose sur un modèle **Random Forest Classifier** entraîné avec `scikit-learn`.

L'application charge directement le pipeline entraîné afin d'appliquer les mêmes transformations lors de l'inférence que pendant l'entraînement.

### Explicabilité avec SHAP

RiskVision AI intègre **SHAP (SHapley Additive exPlanations)** afin d'expliquer localement les prédictions du modèle.

L'application permet notamment de visualiser :

- les principaux facteurs influençant une décision ;
- le sens de leur contribution au risque ;
- l'intensité de leur influence ;
- un graphique Waterfall SHAP ;
- les contributions détaillées des variables.

Une couche d'interprétation transforme également les variables techniques issues du modèle en explications plus compréhensibles pour l'utilisateur.

### Tableau de bord

Un tableau de bord permet de suivre :

- le nombre d'analyses réalisées ;
- le nombre d'observations classées à risque ;
- le nombre d'observations classées non à risque ;
- le taux de risque ;
- la probabilité moyenne observée ;
- les principales métriques du modèle.

### Historique

Les prédictions réalisées peuvent être enregistrées afin de suivre les analyses précédentes.

### Rapport PDF

L'utilisateur peut générer et télécharger un rapport contenant notamment :

- les informations de l'entreprise ;
- la décision du modèle ;
- les probabilités estimées ;
- une synthèse de l'analyse ;
- les principaux facteurs SHAP ;
- un avertissement méthodologique.

---

## Technologies utilisées

| Technologie | Utilisation |
| --- | --- |
| Python 3.11 | Développement principal |
| Streamlit | Application web interactive |
| pandas | Manipulation et préparation des données |
| NumPy | Calcul numérique |
| scikit-learn | Pipeline Machine Learning et Random Forest |
| SHAP | Explicabilité des prédictions |
| Matplotlib | Visualisations |
| Joblib | Sérialisation et chargement du modèle |
| ReportLab | Génération des rapports PDF |
| Git / GitHub | Versionnement et publication du projet |

---

## Architecture du projet

```text
defaillance/
│
├── app.py
│
├── app_components/
│   ├── analysis_summary.py
│   ├── animation_analyse.py
│   ├── dashboard_cards.py
│   ├── dashboard_charts.py
│   ├── history_manager.py
│   ├── history_table.py
│   ├── model_loader.py
│   ├── pdf_report.py
│   ├── prediction_preview.py
│   ├── shap_explainer.py
│   ├── shap_formatter.py
│   ├── sidebar.py
│   ├── styles.py
│   └── theme.py
│
├── app_pages/
│   ├── accueil.py
│   ├── analyse_modele.py
│   ├── explication_ia.py
│   ├── historique.py
│   ├── nouvelle_analyse.py
│   └── tableau_bord.py
│
├── data/
│   └── entreprises.csv
│
├── models/
│   ├── meilleur_modele.joblib
│   └── meilleur_modele_v2.joblib
│
├── scripts/
│   ├── analyse_dataset.py
│   ├── analyse_importance.py
│   ├── analyse_shap.py
│   ├── predict.py
│   ├── preprocessing.py
│   ├── train_model.py
│   ├── train_model_v2.py
│   ├── utils_prediction.py
│   └── webscraping.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/lensariyacoub/defaillance-prediction.git
cd defaillance-prediction
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

Sous Windows :

```powershell
venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
streamlit run app.py
```

L'application est ensuite accessible localement depuis l'adresse indiquée par Streamlit.

---

## Pipeline Machine Learning

Le workflow général du projet suit les étapes suivantes :

```text
Données
   ↓
Prétraitement
   ↓
Feature engineering
   ↓
Entraînement
   ↓
Random Forest
   ↓
Évaluation
   ↓
Sauvegarde du modèle
   ↓
Application Streamlit
   ↓
Prédiction
   ↓
Explication SHAP
   ↓
Rapport PDF
```

---

## Explicabilité du modèle

L'objectif du projet n'est pas uniquement de produire une classe.

RiskVision AI cherche également à répondre à la question :

**« Pourquoi le modèle a-t-il produit cette prédiction ? »**

SHAP permet d'identifier les variables qui déplacent la sortie du modèle vers une classe ou dans le sens opposé.

Les contributions SHAP expliquent le comportement du modèle et ne doivent pas être interprétées comme des relations de causalité économique.

---

## Auteur

**Lensari Yaakoub**

Master 2 — Ingénierie des Données et Évaluations Économétriques  
Université d'Angers

Compétences mobilisées dans le projet :

`Python` • `pandas` • `scikit-learn` • `Machine Learning` • `Random Forest` • `SHAP` • `Streamlit` • `Data Visualization` • `Git`

---

## Statut

Le projet est en développement actif.

La version actuelle permet déjà d'effectuer des prédictions, d'expliquer les résultats du modèle avec SHAP, de suivre les analyses et de générer des rapports PDF.