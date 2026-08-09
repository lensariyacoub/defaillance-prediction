"""
RiskVision AI - Page Explication IA.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import shap
import streamlit as st

from app_components.shap_explainer import (
    expliquer_observation,
)
from app_components.shap_formatter import (
    expliquer_facteur,
    qualifier_influence,
    traduire_effet,
    traduire_variable,
)
from app_components.styles import (
    afficher_footer,
    afficher_hero,
)


def afficher_explication_shap(
    observation,
) -> None:
    """
    Calcule et affiche l'explication SHAP
    de l'observation sélectionnée.
    """

    try:
        resultat_shap = expliquer_observation(
            observation.dataframe
        )

    except Exception as erreur:
        st.error(
            "Impossible de générer l'explication SHAP : "
            f"{erreur}"
        )
        return

    tableau = resultat_shap["tableau"]
    explication = resultat_shap["explication"]

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Facteurs principaux"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Variables ayant le plus influencé la décision"
    )

    top_facteurs = tableau.head(5)

    colonnes = st.columns(
        len(top_facteurs)
    )

    for colonne, (_, ligne) in zip(
        colonnes,
        top_facteurs.iterrows(),
    ):
        contribution = float(
            ligne["contribution_shap"]
        )

        variable_technique = str(
            ligne["variable"]
        )

        variable = traduire_variable(
            variable_technique
        )

        effet = str(
            ligne["effet"]
        )

        niveau_influence = qualifier_influence(
            contribution
        )

        effet_lisible = traduire_effet(
            effet
        )

        if effet == "AUGMENTE_LE_RISQUE":
            symbole = "↑"

        elif effet == "DIMINUE_LE_RISQUE":
            symbole = "↓"

        else:
            symbole = "•"

        with colonne:
            st.markdown(
                (
                    '<div class="riskvision-card">'
                    '<div class="riskvision-card-title">'
                    f"{symbole} Facteur"
                    "</div>"
                    '<div class="riskvision-card-value" '
                    'style="font-size:1.05rem;">'
                    f"{variable}"
                    "</div>"
                    '<div class="riskvision-card-description">'
                    f"{effet_lisible}<br>"
                    f"Influence : {niveau_influence}<br>"
                    f"<small>SHAP : {contribution:+.4f}</small>"
                    "</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

    st.write("")

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Lecture simplifiée"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Comment interpréter ces facteurs ?"
    )

    for _, ligne in top_facteurs.iterrows():
        
        explication_facteur = expliquer_facteur(
    nom_variable=str(
        ligne["variable"]
    ),
    contribution=float(
        ligne["contribution_shap"]
    ),
    valeur_transformee=float(
        ligne["valeur_transformee"]
    ),
 )

        st.markdown(
            f"- {explication_facteur}"
        )

    st.divider()

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Graphique local"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Waterfall SHAP"
    )

    st.caption(
        "Les contributions positives déplacent la sortie du modèle "
        "vers la classe RISQUE. Les contributions négatives "
        "la déplacent dans le sens opposé."
    )

    try:
        plt.figure(
            figsize=(11, 7)
        )

        shap.plots.waterfall(
            explication,
            max_display=12,
            show=False,
        )

        figure = plt.gcf()
        figure.tight_layout()

        st.pyplot(
            figure,
            use_container_width=True,
        )

        plt.close(
            figure
        )

    except Exception as erreur:
        st.warning(
            "Le calcul SHAP a réussi, mais le graphique "
            f"n'a pas pu être affiché : {erreur}"
        )

    st.divider()

    with st.expander(
        "Voir toutes les contributions SHAP"
    ):
        tableau_affichage = tableau[
            [
                "variable",
                "valeur_transformee",
                "contribution_shap",
                "effet",
            ]
        ].copy()

        tableau_affichage["variable"] = (
            tableau_affichage["variable"]
            .apply(
                traduire_variable
            )
        )

        tableau_affichage["effet"] = (
            tableau_affichage["effet"]
            .apply(
                traduire_effet
            )
        )

        tableau_affichage = (
            tableau_affichage.rename(
                columns={
                    "variable": "Variable",
                    "valeur_transformee":
                        "Valeur transformée",
                    "contribution_shap":
                        "Contribution SHAP",
                    "effet": "Effet",
                }
            )
        )

        tableau_affichage = (
            tableau_affichage
            .head(20)
        )

        st.dataframe(
            tableau_affichage,
            use_container_width=True,
            hide_index=True,
        )

    st.info(
        "Les valeurs SHAP expliquent le comportement du modèle. "
        "Elles ne prouvent pas une relation de causalité économique."
    )


def afficher_explication_ia() -> None:
    """
    Affiche les informations de la dernière analyse
    avant de générer l'explication SHAP.
    """

    afficher_hero(
        titre="Explication IA",
        sous_titre=(
            "Comprenez les facteurs qui ont influencé "
            "la décision du modèle pour la dernière entreprise analysée."
        ),
        badge="SHAP • EXPLAINABLE AI",
    )

    if "derniere_analyse" not in st.session_state:
        st.info(
            "Aucune analyse n'est encore disponible. "
            "Rendez-vous dans « Nouvelle analyse » "
            "pour analyser une entreprise."
        )

        afficher_footer()

        return

    derniere_analyse = st.session_state[
        "derniere_analyse"
    ]

    observation = derniere_analyse[
        "observation"
    ]

    resultat = derniere_analyse[
        "resultat"
    ]

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Dernière analyse"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        observation.nom_entreprise
    )

    colonne_1, colonne_2, colonne_3 = st.columns(
        3
    )

    with colonne_1:
        st.metric(
            "Greffe",
            observation.greffe,
        )

    with colonne_2:
        st.metric(
            "Activité",
            observation.activite_probable,
        )

    with colonne_3:
        st.metric(
            "Décision",
            resultat["decision"],
        )

    colonne_risque, colonne_non_risque = st.columns(
        2
    )

    with colonne_risque:
        st.metric(
            "Probabilité de risque",
            (
                f"{resultat['probabilite_risque'] * 100:.2f} %"
            ),
        )

    with colonne_non_risque:
        st.metric(
            "Probabilité de non-risque",
            (
                f"{resultat['probabilite_non_risque'] * 100:.2f} %"
            ),
        )

    st.divider()

    st.subheader(
        "Explication du modèle"
    )

    afficher_explication_shap(
        observation
    )

    with st.expander(
        "Voir les variables de l'observation"
    ):
        st.dataframe(
            observation.dataframe,
            use_container_width=True,
            hide_index=True,
        )

    afficher_footer()