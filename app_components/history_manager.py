"""
RiskVision AI - Gestion persistante de l'historique.

Responsabilités :
- enregistrer chaque analyse réalisée ;
- charger l'historique ;
- calculer des statistiques simples ;
- supprimer l'historique à la demande.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


# ==========================================================
# CONFIGURATION
# ==========================================================

HISTORY_PATH = Path(
    "data/history/analyses.csv"
)

HISTORY_COLUMNS = [
    "date_analyse",
    "nom_entreprise",
    "departement",
    "greffe",
    "type_entite",
    "activite_probable",
    "classe_predite",
    "decision",
    "probabilite_risque",
    "probabilite_non_risque",
]


# ==========================================================
# INITIALISATION
# ==========================================================

def initialiser_historique() -> None:
    """
    Crée le dossier et le fichier d'historique
    s'ils n'existent pas encore.
    """

    HISTORY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not HISTORY_PATH.exists():

        historique_vide = pd.DataFrame(
            columns=HISTORY_COLUMNS
        )

        historique_vide.to_csv(
            HISTORY_PATH,
            index=False,
            encoding="utf-8-sig",
        )


# ==========================================================
# CHARGEMENT
# ==========================================================

def charger_historique() -> pd.DataFrame:
    """
    Charge l'historique des analyses.
    """

    initialiser_historique()

    try:

        historique = pd.read_csv(
            HISTORY_PATH,
            encoding="utf-8-sig",
        )

    except pd.errors.EmptyDataError:

        historique = pd.DataFrame(
            columns=HISTORY_COLUMNS
        )

    for colonne in HISTORY_COLUMNS:

        if colonne not in historique.columns:
            historique[colonne] = pd.NA

    return historique[
        HISTORY_COLUMNS
    ]


# ==========================================================
# ENREGISTREMENT
# ==========================================================

def enregistrer_analyse(
    observation: Any,
    resultat: dict[str, Any],
) -> None:
    """
    Enregistre une nouvelle analyse dans l'historique.
    """

    historique = charger_historique()

    nouvelle_ligne = {
        "date_analyse":
            datetime.now().isoformat(
                timespec="seconds"
            ),
        "nom_entreprise":
            observation.nom_entreprise,
        "departement":
            observation.departement,
        "greffe":
            observation.greffe,
        "type_entite":
            observation.type_entite,
        "activite_probable":
            observation.activite_probable,
        "classe_predite":
            resultat["classe_predite"],
        "decision":
            resultat["decision"],
        "probabilite_risque":
            resultat["probabilite_risque"],
        "probabilite_non_risque":
            resultat["probabilite_non_risque"],
    }

    historique = pd.concat(
        [
            historique,
            pd.DataFrame(
                [nouvelle_ligne]
            ),
        ],
        ignore_index=True,
    )

    historique.to_csv(
        HISTORY_PATH,
        index=False,
        encoding="utf-8-sig",
    )


# ==========================================================
# STATISTIQUES
# ==========================================================

def obtenir_statistiques_historique() -> dict[str, float | int]:
    """
    Calcule les statistiques principales de l'historique.
    """

    historique = charger_historique()

    total = len(
        historique
    )

    if total == 0:

        return {
            "total": 0,
            "nombre_risque": 0,
            "nombre_non_risque": 0,
            "taux_risque": 0.0,
            "probabilite_risque_moyenne": 0.0,
        }

    nombre_risque = int(
        (
            historique["decision"]
            == "RISQUE"
        ).sum()
    )

    nombre_non_risque = int(
        (
            historique["decision"]
            == "NON RISQUE"
        ).sum()
    )

    probabilites = pd.to_numeric(
        historique["probabilite_risque"],
        errors="coerce",
    )

    probabilite_risque_moyenne = float(
        probabilites.mean()
    )

    return {
        "total":
            total,
        "nombre_risque":
            nombre_risque,
        "nombre_non_risque":
            nombre_non_risque,
        "taux_risque":
            nombre_risque / total,
        "probabilite_risque_moyenne":
            probabilite_risque_moyenne,
    }


# ==========================================================
# SUPPRESSION
# ==========================================================

def supprimer_historique() -> None:
    """
    Supprime toutes les analyses enregistrées.
    """

    historique_vide = pd.DataFrame(
        columns=HISTORY_COLUMNS
    )

    HISTORY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    historique_vide.to_csv(
        HISTORY_PATH,
        index=False,
        encoding="utf-8-sig",
    )