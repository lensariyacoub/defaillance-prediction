"""
RiskVision AI - Page d'accueil.
"""

from __future__ import annotations

import streamlit as st

from app_components.model_loader import (
    charger_metriques,
    obtenir_informations_modele,
)

from app_components.styles import (
    afficher_footer,
    afficher_hero,
)


def afficher_accueil() -> None:
    """
    Affiche la page d'accueil de RiskVision AI.
    """
    metriques = charger_metriques()

    informations = obtenir_informations_modele()
    nom_modele = informations["nom_modele"].replace(
    "_",
    " ",
).title()
    afficher_hero(
        titre="RiskVision AI",
        sous_titre=(
            "Une plateforme d’analyse exploratoire du risque "
            "de défaillance des entreprises, construite à partir "
            "des annonces BODACC, du Machine Learning et de SHAP."
        ),
        badge="BODACC • Random Forest • Explainable AI",
    )

    st.markdown(
        '<div class="riskvision-eyebrow">Vue d’ensemble</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Le système en quelques chiffres")

    colonne_1, colonne_2, colonne_3, colonne_4 = st.columns(4)

    with colonne_1:
        st.metric(
            "Observations",
            "999",
        )

    with colonne_2:
        st.metric(
        "Accuracy",
        f"{metriques['accuracy'] * 100:.2f} %",
    )

    with colonne_3:
        st.metric(
        "F1-score",
        f"{metriques['f1_score'] * 100:.2f} %",
    )

    with colonne_4:
        st.metric(
        "ROC-AUC",
        f"{metriques['roc_auc'] * 100:.2f} %",
    )

    st.divider()

    colonne_gauche, colonne_droite = st.columns(
        [1.15, 0.85]
    )

    with colonne_gauche:

        st.markdown(
            '<div class="riskvision-eyebrow">'
            "Fonctionnement"
            "</div>",
            unsafe_allow_html=True,
        )

        st.subheader(
            "Une chaîne complète d’analyse"
        )

        st.markdown(
            """
            RiskVision AI transforme des données issues du BODACC
            en une analyse exploitable grâce à plusieurs étapes :

            1. **Collecte automatisée** des annonces commerciales.
            2. **Nettoyage et préparation** des variables.
            3. **Classification** avec une Random Forest optimisée.
            4. **Calcul d’une sortie de risque exploratoire**.
            5. **Explication des décisions** grâce à SHAP.
            """
        )

    with colonne_droite:

        st.markdown(
            (
        '<div class="riskvision-card">'
        '<div class="riskvision-card-title">'
        "Modèle actuel"
        "</div>"
        '<div class="riskvision-card-value">'
        f"{nom_modele}"
        "</div>"
        '<div class="riskvision-card-description">'
        "Modèle optimisé par GridSearchCV avec validation "
        "croisée stratifiée à cinq plis."
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
        'Explicabilité'
        '</div>'
        '<div class="riskvision-card-value">'
        'SHAP'
        '</div>'
        '<div class="riskvision-card-description">'
        'Analyse globale des variables et explication '
        'individuelle des prédictions.'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

    st.divider()

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Parcours d’analyse"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "De l’entreprise à la décision"
    )

    etape_1, etape_2, etape_3, etape_4 = st.columns(4)

    with etape_1:
        st.markdown(
            """
            <div class="riskvision-card">
                <div class="riskvision-card-title">01</div>
                <div class="riskvision-card-value">Saisie</div>
                <div class="riskvision-card-description">
                    Nom, département et type d’entité.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with etape_2:
        st.markdown(
            """
            <div class="riskvision-card">
                <div class="riskvision-card-title">02</div>
                <div class="riskvision-card-value">Détection</div>
                <div class="riskvision-card-description">
                    Greffe et activité probable détectés automatiquement.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with etape_3:
        st.markdown(
            """
            <div class="riskvision-card">
                <div class="riskvision-card-title">03</div>
                <div class="riskvision-card-value">Prédiction</div>
                <div class="riskvision-card-description">
                    Calcul de la classe et des probabilités du modèle.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with etape_4:
        st.markdown(
            """
            <div class="riskvision-card">
                <div class="riskvision-card-title">04</div>
                <div class="riskvision-card-value">Explication</div>
                <div class="riskvision-card-description">
                    Identification des facteurs influençant la décision.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.warning(
        "RiskVision AI est actuellement un outil exploratoire. "
        "Le label est construit à partir du type d’annonce BODACC. "
        "Le résultat ne constitue pas une notation financière officielle "
        "ni une probabilité validée de défaillance future."
    )

    afficher_footer()