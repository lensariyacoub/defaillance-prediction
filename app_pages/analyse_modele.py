"""
RiskVision AI - Page Analyse du modèle.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from app_components.model_loader import (
    charger_metriques,
    obtenir_informations_modele,
    obtenir_pipeline,
)
from app_components.styles import (
    afficher_footer,
    afficher_hero,
)


def afficher_matrice_confusion(
    matrice: list[list[int]],
) -> None:
    """
    Affiche la matrice de confusion du modèle.
    """

    matrice_numpy = np.asarray(
        matrice,
        dtype=int,
    )

    figure, axe = plt.subplots(
        figsize=(7, 5)
    )

    image = axe.imshow(
        matrice_numpy,
        interpolation="nearest",
    )

    axe.set_title(
        "Matrice de confusion"
    )

    axe.set_xlabel(
        "Classe prédite"
    )

    axe.set_ylabel(
        "Classe réelle"
    )

    axe.set_xticks(
        [0, 1],
        labels=[
            "Non-risque",
            "Risque",
        ],
    )

    axe.set_yticks(
        [0, 1],
        labels=[
            "Non-risque",
            "Risque",
        ],
    )

    seuil = matrice_numpy.max() / 2

    for ligne in range(
        matrice_numpy.shape[0]
    ):

        for colonne in range(
            matrice_numpy.shape[1]
        ):

            valeur = matrice_numpy[
                ligne,
                colonne,
            ]

            axe.text(
                colonne,
                ligne,
                str(valeur),
                horizontalalignment="center",
                verticalalignment="center",
                color=(
                    "white"
                    if valeur > seuil
                    else "black"
                ),
                fontsize=16,
                fontweight="bold",
            )

    figure.colorbar(
        image,
        ax=axe,
        fraction=0.046,
        pad=0.04,
    )

    figure.tight_layout()

    st.pyplot(
        figure,
        use_container_width=True,
    )

    plt.close(
        figure
    )


def afficher_analyse_modele() -> None:
    """
    Affiche les performances et les informations
    techniques du modèle entraîné.
    """

    metriques = charger_metriques()

    informations = obtenir_informations_modele()

    pipeline = obtenir_pipeline()

    nom_modele = informations[
        "nom_modele"
    ].replace(
        "_",
        " ",
    ).title()

    afficher_hero(
        titre="Analyse du modèle",
        sous_titre=(
            "Explorez les performances, les erreurs "
            "et l’architecture du modèle utilisé "
            "par RiskVision AI."
        ),
        badge="ÉVALUATION • RANDOM FOREST • GRIDSEARCHCV",
    )

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Performances"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Indicateurs principaux"
    )

    colonne_1, colonne_2, colonne_3 = st.columns(
        3
    )

    with colonne_1:

        st.metric(
            "Accuracy",
            f"{metriques['accuracy'] * 100:.2f} %",
        )

    with colonne_2:

        st.metric(
            "F1-score",
            f"{metriques['f1_score'] * 100:.2f} %",
        )

    with colonne_3:

        st.metric(
            "ROC-AUC",
            f"{metriques['roc_auc'] * 100:.2f} %",
        )

    colonne_4, colonne_5 = st.columns(
        2
    )

    with colonne_4:

        st.metric(
            "Précision",
            f"{metriques['precision'] * 100:.2f} %",
        )

    with colonne_5:

        st.metric(
            "Rappel",
            f"{metriques['recall'] * 100:.2f} %",
        )

    st.divider()

    colonne_graphique, colonne_interpretation = st.columns(
        [1.15, 0.85]
    )

    with colonne_graphique:

        st.markdown(
            '<div class="riskvision-eyebrow">'
            "Classification"
            "</div>",
            unsafe_allow_html=True,
        )

        st.subheader(
            "Matrice de confusion"
        )

        afficher_matrice_confusion(
            metriques[
                "matrice_confusion"
            ]
        )

    with colonne_interpretation:

        matrice = metriques[
            "matrice_confusion"
        ]

        vrais_negatifs = int(
            matrice[0][0]
        )

        faux_positifs = int(
            matrice[0][1]
        )

        faux_negatifs = int(
            matrice[1][0]
        )

        vrais_positifs = int(
            matrice[1][1]
        )

        st.markdown(
            '<div class="riskvision-eyebrow">'
            "Lecture"
            "</div>",
            unsafe_allow_html=True,
        )

        st.subheader(
            "Interprétation des résultats"
        )

        st.markdown(
            (
                '<div class="riskvision-card">'
                '<div class="riskvision-card-title">'
                "Vrais négatifs"
                "</div>"
                '<div class="riskvision-card-value">'
                f"{vrais_negatifs}"
                "</div>"
                '<div class="riskvision-card-description">'
                "Observations non-risque correctement classées."
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
                "Vrais positifs"
                "</div>"
                '<div class="riskvision-card-value">'
                f"{vrais_positifs}"
                "</div>"
                '<div class="riskvision-card-description">'
                "Observations risque correctement détectées."
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.write("")

        st.warning(
            f"Faux positifs : {faux_positifs}"
        )

        st.error(
            f"Faux négatifs : {faux_negatifs}"
        )

    st.divider()

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Architecture"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Informations techniques"
    )

    colonne_modele, colonne_variables = st.columns(
        2
    )

    with colonne_modele:

        st.markdown(
            (
                '<div class="riskvision-card">'
                '<div class="riskvision-card-title">'
                "Modèle"
                "</div>"
                '<div class="riskvision-card-value">'
                f"{nom_modele}"
                "</div>"
                '<div class="riskvision-card-description">'
                f"Pipeline sklearn : {type(pipeline).__name__}"
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with colonne_variables:

        st.markdown(
            (
                '<div class="riskvision-card">'
                '<div class="riskvision-card-title">'
                "Variables d’entrée"
                "</div>"
                '<div class="riskvision-card-value">'
                f"{informations['nombre_variables']}"
                "</div>"
                '<div class="riskvision-card-description">'
                "Variables catégorielles et numériques "
                "préparées avant encodage."
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with st.expander(
        "Voir les variables utilisées"
    ):

        st.markdown(
            "### Variables catégorielles"
        )

        st.write(
            informations[
                "variables_categorielles"
            ]
        )

        st.markdown(
            "### Variables numériques"
        )

        st.write(
            informations[
                "variables_numeriques"
            ]
        )

    st.info(
        "Les performances présentées correspondent "
        "au jeu de test utilisé lors de l’entraînement "
        "du modèle Random Forest V2."
    )

    afficher_footer()