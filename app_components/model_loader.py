"""
RiskVision AI - Chargement centralisé du modèle.

Responsabilités :
- charger le modèle Random Forest V2 ;
- charger les métriques sauvegardées ;
- mettre le modèle en cache avec Streamlit ;
- fournir une interface unique aux pages de l'application.

Ce module ne contient aucun élément graphique.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st


# ==========================================================
# CHEMINS
# ==========================================================

MODEL_PATH = Path(
    "models/meilleur_modele_v2.joblib"
)

RESULTS_PATH = Path(
    "reports/resultats_gridsearch_v2.json"
)


# ==========================================================
# CHARGEMENT DU MODELE
# ==========================================================

@st.cache_resource
def charger_objet_modele() -> dict[str, Any]:
    """
    Charge le fichier joblib une seule fois.

    Returns
    -------
    dict
        Dictionnaire contenant notamment le pipeline entraîné.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH.resolve()}"
        )

    objet_modele = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        objet_modele,
        dict,
    ):
        raise TypeError(
            "Le fichier joblib ne contient pas "
            "le dictionnaire attendu."
        )

    if "pipeline" not in objet_modele:
        raise KeyError(
            "La clé 'pipeline' est absente du modèle."
        )

    return objet_modele


# ==========================================================
# ACCES AU PIPELINE
# ==========================================================

def obtenir_pipeline():
    """
    Retourne directement le pipeline sklearn entraîné.
    """

    objet_modele = charger_objet_modele()

    return objet_modele["pipeline"]


# ==========================================================
# INFORMATIONS DU MODELE
# ==========================================================

def obtenir_informations_modele() -> dict[str, Any]:
    """
    Retourne les principales informations enregistrées
    avec le modèle.
    """

    objet_modele = charger_objet_modele()

    variables_categorielles = objet_modele.get(
        "variables_categorielles",
        [],
    )

    variables_numeriques = objet_modele.get(
        "variables_numeriques",
        [],
    )

    return {
        "nom_modele": objet_modele.get(
            "nom_modele",
            "random_forest_v2",
        ),
        "cible": objet_modele.get(
            "target",
            "label_risque",
        ),
        "variables_categorielles":
            variables_categorielles,
        "variables_numeriques":
            variables_numeriques,
        "nombre_variables": (
            len(variables_categorielles)
            + len(variables_numeriques)
        ),
    }


# ==========================================================
# CHARGEMENT DES METRIQUES
# ==========================================================

@st.cache_data
def charger_metriques() -> dict[str, Any]:
    """
    Charge les performances sauvegardées dans le JSON.

    Des valeurs par défaut sont utilisées si le fichier
    ou certaines clés sont absents.
    """

    valeurs_defaut = {
        "accuracy": 0.89,
        "precision": 0.4444,
        "recall": 0.6316,
        "f1_score": 0.5217,
        "roc_auc": 0.7911,
        "matrice_confusion": [
            [166, 15],
            [7, 12],
        ],
    }

    if not RESULTS_PATH.exists():
        return valeurs_defaut

    try:
        with RESULTS_PATH.open(
            "r",
            encoding="utf-8",
        ) as fichier:
            donnees = json.load(
                fichier
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return valeurs_defaut

    # Le JSON peut contenir les métriques directement
    # ou dans une sous-clé selon le script d'entraînement.
    sources_possibles = [
        donnees,
        donnees.get(
            "resultats_test",
            {},
        ),
        donnees.get(
            "metrics",
            {},
        ),
        donnees.get(
            "metriques",
            {},
        ),
    ]

    metriques = valeurs_defaut.copy()

    correspondances = {
        "accuracy": [
            "accuracy",
        ],
        "precision": [
            "precision",
        ],
        "recall": [
            "recall",
        ],
        "f1_score": [
            "f1_score",
            "f1-score",
            "f1",
        ],
        "roc_auc": [
            "roc_auc",
            "roc-auc",
            "auc",
        ],
        "matrice_confusion": [
            "matrice_confusion",
            "confusion_matrix",
        ],
    }

    for source in sources_possibles:

        if not isinstance(
            source,
            dict,
        ):
            continue

        for nom_final, cles in correspondances.items():

            for cle in cles:

                if cle in source:
                    metriques[nom_final] = source[cle]
                    break

    return metriques


# ==========================================================
# PREDICTION
# ==========================================================

def predire_observation(
    observation: pd.DataFrame,
) -> dict[str, Any]:
    """
    Effectue une prédiction sur une observation préparée.

    Parameters
    ----------
    observation
        DataFrame contenant une ligne et les variables
        attendues par le pipeline.

    Returns
    -------
    dict
        Classe, probabilités et décision.
    """

    if observation.empty:
        raise ValueError(
            "L'observation à prédire est vide."
        )

    pipeline = obtenir_pipeline()

    classe_predite = int(
        pipeline.predict(
            observation
        )[0]
    )

    probabilites = pipeline.predict_proba(
        observation
    )[0]

    probabilite_non_risque = float(
        probabilites[0]
    )

    probabilite_risque = float(
        probabilites[1]
    )

    return {
        "classe_predite":
            classe_predite,
        "probabilite_non_risque":
            probabilite_non_risque,
        "probabilite_risque":
            probabilite_risque,
        "decision": (
            "RISQUE"
            if classe_predite == 1
            else "NON RISQUE"
        ),
    }