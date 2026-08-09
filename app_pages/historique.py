"""
RiskVision AI - Page Historique.
"""

from __future__ import annotations

import streamlit as st

from app_components.history_manager import (
    charger_historique,
    supprimer_historique,
)
from app_components.history_table import (
    afficher_table_historique,
)
from app_components.styles import (
    afficher_footer,
    afficher_hero,
)


def afficher_historique() -> None:
    """
    Affiche, filtre et exporte l'historique
    des analyses réalisées.
    """

    historique = charger_historique()

    afficher_hero(
        titre="Historique",
        sous_titre=(
            "Consultez, recherchez et exportez "
            "les analyses réalisées dans RiskVision AI."
        ),
        badge="ARCHIVES • FILTRES • EXPORT",
    )

    if historique.empty:
        st.info(
            "Aucune analyse n'est encore enregistrée."
        )

        afficher_footer()

        return

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Recherche et filtres"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Explorer les analyses"
    )

    colonne_recherche, colonne_decision = st.columns(
        [1.3, 0.7]
    )

    with colonne_recherche:
        recherche = st.text_input(
            "Rechercher une entreprise",
            placeholder="Exemple : LENSARI DATA CONSEIL",
        )

    with colonne_decision:
        decisions_disponibles = sorted(
            historique["decision"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        filtre_decision = st.selectbox(
            "Décision",
            options=[
                "TOUTES",
                *decisions_disponibles,
            ],
        )

    colonne_activite, colonne_departement = st.columns(
        2
    )

    with colonne_activite:
        activites_disponibles = sorted(
            historique["activite_probable"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        filtre_activite = st.selectbox(
            "Activité",
            options=[
                "TOUTES",
                *activites_disponibles,
            ],
        )

    with colonne_departement:
        departements_disponibles = sorted(
            historique["departement"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        filtre_departement = st.selectbox(
            "Département",
            options=[
                "TOUS",
                *departements_disponibles,
            ],
        )

    historique_filtre = historique.copy()

    if recherche.strip():
        historique_filtre = historique_filtre[
            historique_filtre["nom_entreprise"]
            .astype(str)
            .str.contains(
                recherche.strip(),
                case=False,
                na=False,
            )
        ]

    if filtre_decision != "TOUTES":
        historique_filtre = historique_filtre[
            historique_filtre["decision"]
            == filtre_decision
        ]

    if filtre_activite != "TOUTES":
        historique_filtre = historique_filtre[
            historique_filtre["activite_probable"]
            == filtre_activite
        ]

    if filtre_departement != "TOUS":
        historique_filtre = historique_filtre[
            historique_filtre["departement"]
            .astype(str)
            == filtre_departement
        ]

    st.divider()

    colonne_total, colonne_resultats = st.columns(
        2
    )

    with colonne_total:
        st.metric(
            "Analyses enregistrées",
            len(historique),
        )

    with colonne_resultats:
        st.metric(
            "Résultats affichés",
            len(historique_filtre),
        )

    afficher_table_historique(
        historique_filtre
    )

    st.divider()

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Actions"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Exporter ou supprimer"
    )

    colonne_export, colonne_suppression = st.columns(
        2
    )

    with colonne_export:
        csv_export = historique_filtre.to_csv(
            index=False,
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            label="Télécharger l'historique filtré",
            data=csv_export,
            file_name="historique_riskvision.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with colonne_suppression:
        confirmation = st.checkbox(
            "Je confirme vouloir vider tout l'historique"
        )

        if st.button(
            "Vider l'historique",
            disabled=not confirmation,
            use_container_width=True,
        ):
            supprimer_historique()

            st.success(
                "L'historique a été supprimé."
            )

            st.rerun()

    afficher_footer()