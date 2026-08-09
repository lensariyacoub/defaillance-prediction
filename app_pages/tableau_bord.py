"""
RiskVision AI - Tableau de bord.
"""

from __future__ import annotations

import streamlit as st

from app_components.dashboard_cards import (
    afficher_kpi,
)

from app_components.dashboard_charts import (
    afficher_repartition_decisions,
)

from app_components.history_manager import (
    obtenir_statistiques_historique,
)

from app_components.model_loader import (
    charger_metriques,
    obtenir_informations_modele,
    obtenir_pipeline,
)
from app_components.styles import (
    afficher_hero,
)

def afficher_tableau_bord() -> None:
    """
    Affiche le tableau de bord principal.
    """

    metriques = charger_metriques()
    informations = obtenir_informations_modele()
    statistiques = obtenir_statistiques_historique()

    afficher_hero(
        titre="Tableau de bord",
        sous_titre=(
            "Vue d'ensemble des analyses réalisées "
            "par RiskVision AI."
        ),
        badge="STATISTIQUES • DASHBOARD",
    )

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Vue générale"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Indicateurs du modèle"
    )

    colonne_1, colonne_2, colonne_3, colonne_4 = st.columns(4)

    with colonne_1:
       afficher_kpi(
        titre="Accuracy",
        valeur=f"{metriques['accuracy'] * 100:.2f} %",
        description="Performance globale de classification.",
        icone="🎯",
    )

    with colonne_2:
        afficher_kpi(
        titre="F1-score",
        valeur=f"{metriques['f1_score'] * 100:.2f} %",
        description="Équilibre entre précision et rappel.",
        icone="⚖️",
    )

    with colonne_3:
        afficher_kpi(
        titre="ROC-AUC",
        valeur=f"{metriques['roc_auc'] * 100:.2f} %",
        description="Capacité du modèle à séparer les classes.",
        icone="📈",
    )

    with colonne_4:
       afficher_kpi(
        titre="Variables",
        valeur=informations["nombre_variables"],
        description="Variables utilisées avant encodage.",
        icone="🧩",
    )
       
    st.divider()

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Activité de l’application"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Analyses réalisées"
    )

    colonne_5, colonne_6, colonne_7, colonne_8 = st.columns(4)

    with colonne_5:
        afficher_kpi(
            titre="Analyses",
            valeur=statistiques["total"],
            description="Nombre total de prédictions enregistrées.",
            icone="📊",
        )

    with colonne_6:
        afficher_kpi(
            titre="Risque",
            valeur=statistiques["nombre_risque"],
            description="Analyses classées dans la catégorie risque.",
            icone="🔴",
        )

    with colonne_7:
        afficher_kpi(
            titre="Non risque",
            valeur=statistiques["nombre_non_risque"],
            description="Analyses classées dans la catégorie non risque.",
            icone="🟢",
        )

    with colonne_8:
        afficher_kpi(
            titre="Risque moyen",
            valeur=(
                f"{statistiques['probabilite_risque_moyenne'] * 100:.2f} %"
            ),
            description="Probabilité de risque moyenne des analyses.",
            icone="📈",
        )

    st.divider()

    colonne_graphique, colonne_texte = st.columns(
        [1.2, 0.8]
    )

    with colonne_graphique:
        afficher_repartition_decisions(
            nombre_risque=statistiques["nombre_risque"],
            nombre_non_risque=statistiques["nombre_non_risque"],
        )

    with colonne_texte:
        st.markdown(
            '<div class="riskvision-eyebrow">'
            "Synthèse"
            "</div>",
            unsafe_allow_html=True,
        )

        st.subheader(
            "Lecture des analyses"
        )

        if statistiques["total"] == 0:
            st.info(
                "Aucune analyse n’est encore enregistrée."
            )

        else:
            taux_risque = (
                statistiques["taux_risque"]
                * 100
            )

            st.markdown(
                (
                    '<div class="riskvision-card">'
                    '<div class="riskvision-card-title">'
                    "Taux de risque"
                    "</div>"
                    '<div class="riskvision-card-value">'
                    f"{taux_risque:.2f} %"
                    "</div>"
                    '<div class="riskvision-card-description">'
                    "Part des analyses classées RISQUE "
                    "dans l’historique de l’application."
                    "</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.write("")

            st.markdown(
                (
                    '<div class="riskvision-card">'
                    '<div class="riskvision-card-title">'
                    "Historique actuel"
                    "</div>"
                    '<div class="riskvision-card-value">'
                    f"{statistiques['total']}"
                    "</div>"
                    '<div class="riskvision-card-description">'
                    "Chaque nouvelle prédiction alimente "
                    "automatiquement ce tableau de bord."
                    "</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )