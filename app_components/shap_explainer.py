"""
RiskVision AI - Explication locale avec SHAP.

Responsabilités :
- récupérer le pipeline entraîné ;
- transformer une observation ;
- calculer les contributions SHAP ;
- produire un tableau d'explication locale.

Ce module ne contient aucun affichage Streamlit.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import shap
import streamlit as st

from app_components.model_loader import (
    charger_objet_modele,
)


# ==========================================================
# EXPLAINER SHAP
# ==========================================================

@st.cache_resource
def charger_explainer_shap():
    """
    Crée et met en cache l'explainer SHAP
    du modèle Random Forest.
    """

    objet_modele = charger_objet_modele()

    pipeline = objet_modele["pipeline"]

    modele = pipeline.named_steps["model"]

    return shap.TreeExplainer(
        modele
    )


# ==========================================================
# NOMS DES VARIABLES APRES ENCODAGE
# ==========================================================

def obtenir_noms_variables_transformees() -> list[str]:
    """
    Retourne les noms des variables après
    le prétraitement et le One-Hot Encoding.
    """

    objet_modele = charger_objet_modele()

    pipeline = objet_modele["pipeline"]

    variables_categorielles = objet_modele[
        "variables_categorielles"
    ]

    variables_numeriques = objet_modele[
        "variables_numeriques"
    ]

    preprocesseur = pipeline.named_steps[
        "preprocessing"
    ]

    pipeline_categoriel = (
        preprocesseur
        .named_transformers_["categoriel"]
    )

    encodeur = pipeline_categoriel.named_steps[
        "encodage"
    ]

    noms_categorielles = (
        encodeur
        .get_feature_names_out(
            variables_categorielles
        )
        .tolist()
    )

    return (
        noms_categorielles
        + list(variables_numeriques)
    )


# ==========================================================
# TRANSFORMATION
# ==========================================================

def transformer_observation(
    observation: pd.DataFrame,
) -> np.ndarray:
    """
    Applique uniquement le prétraitement du pipeline.
    """

    objet_modele = charger_objet_modele()

    pipeline = objet_modele["pipeline"]

    preprocesseur = pipeline.named_steps[
        "preprocessing"
    ]

    matrice = preprocesseur.transform(
        observation
    )

    if hasattr(
        matrice,
        "toarray",
    ):
        matrice = matrice.toarray()

    return np.asarray(
        matrice
    )


# ==========================================================
# SELECTION DE LA CLASSE POSITIVE
# ==========================================================

def selectionner_classe_positive(
    explication: shap.Explanation,
) -> shap.Explanation:
    """
    Sélectionne les contributions associées
    à la classe positive RISQUE.
    """

    valeurs = np.asarray(
        explication.values
    )

    bases = np.asarray(
        explication.base_values
    )

    donnees = np.asarray(
        explication.data
    )

    if valeurs.ndim == 3:

        valeurs = valeurs[
            :,
            :,
            1,
        ]

        if bases.ndim == 2:

            bases = bases[
                :,
                1,
            ]

        elif bases.ndim == 1 and len(bases) == 2:

            bases = np.repeat(
                bases[1],
                valeurs.shape[0],
            )

    elif valeurs.ndim != 2:

        raise ValueError(
            f"Format SHAP inattendu : {valeurs.shape}"
        )

    if bases.ndim == 0:

        bases = np.repeat(
            float(bases),
            valeurs.shape[0],
        )

    return shap.Explanation(
        values=valeurs,
        base_values=bases,
        data=donnees,
        feature_names=(
            explication.feature_names
        ),
    )


# ==========================================================
# EXPLICATION LOCALE
# ==========================================================

def expliquer_observation(
    observation: pd.DataFrame,
) -> dict[str, Any]:
    """
    Calcule l'explication SHAP d'une observation.

    Returns
    -------
    dict
        Explication SHAP complète et tableau trié
        des principales contributions.
    """

    matrice = transformer_observation(
        observation
    )

    noms_variables = (
        obtenir_noms_variables_transformees()
    )

    explainer = charger_explainer_shap()

    explication = explainer(
        matrice,
        check_additivity=False,
    )

    explication.feature_names = (
        noms_variables
    )

    explication_positive = (
        selectionner_classe_positive(
            explication
        )
    )

    valeurs = explication_positive.values[0]

    valeurs_observation = (
        explication_positive.data[0]
    )

    tableau = pd.DataFrame(
        {
            "variable": noms_variables,
            "valeur_transformee":
                valeurs_observation,
            "contribution_shap":
                valeurs,
            "contribution_absolue":
                np.abs(valeurs),
        }
    )

    tableau["effet"] = np.where(
        tableau["contribution_shap"] > 0,
        "AUGMENTE_LE_RISQUE",
        np.where(
            tableau["contribution_shap"] < 0,
            "DIMINUE_LE_RISQUE",
            "NEUTRE",
        ),
    )

    tableau = tableau.sort_values(
        by="contribution_absolue",
        ascending=False,
    ).reset_index(
        drop=True
    )

    return {
        "explication":
            explication_positive[0],
        "tableau":
            tableau,
    }