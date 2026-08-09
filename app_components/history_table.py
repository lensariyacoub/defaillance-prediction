"""
RiskVision AI - Tableau interactif de l'historique.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def preparer_historique_affichage(
    historique: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prépare l'historique pour un affichage lisible.
    """

    if historique.empty:
        return historique.copy()

    tableau = historique.copy()

    tableau["date_analyse"] = pd.to_datetime(
        tableau["date_analyse"],
        errors="coerce",
    )

    tableau["date_analyse"] = tableau[
        "date_analyse"
    ].dt.strftime(
        "%d/%m/%Y %H:%M"
    )

    tableau["probabilite_risque"] = (
        pd.to_numeric(
            tableau["probabilite_risque"],
            errors="coerce",
        )
        * 100
    ).round(2)

    tableau["probabilite_non_risque"] = (
        pd.to_numeric(
            tableau["probabilite_non_risque"],
            errors="coerce",
        )
        * 100
    ).round(2)

    tableau = tableau.rename(
        columns={
            "date_analyse": "Date",
            "nom_entreprise": "Entreprise",
            "departement": "Département",
            "greffe": "Greffe",
            "type_entite": "Type d’entité",
            "activite_probable": "Activité",
            "classe_predite": "Classe",
            "decision": "Décision",
            "probabilite_risque": "Risque (%)",
            "probabilite_non_risque": "Non-risque (%)",
        }
    )

    return tableau


def afficher_table_historique(
    historique: pd.DataFrame,
) -> None:
    """
    Affiche l'historique dans un tableau interactif.
    """

    if historique.empty:

        st.info(
            "Aucune analyse n'est encore enregistrée."
        )

        return

    tableau = preparer_historique_affichage(
        historique
    )

    st.dataframe(
        tableau,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Risque (%)": st.column_config.NumberColumn(
                format="%.2f %%"
            ),
            "Non-risque (%)": st.column_config.NumberColumn(
                format="%.2f %%"
            ),
        },
    )