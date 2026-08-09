"""
RiskVision AI - Barre latérale de navigation.
"""

from __future__ import annotations

import streamlit as st

from app_components.model_loader import (
    charger_metriques,
    obtenir_informations_modele,
)
from app_components.theme import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    ICON_AI,
)


# ==========================================================
# MENU
# ==========================================================

MENU = [
    {
        "icone": "🏠",
        "nom": "Accueil",
    },
    {
        "icone": "🔍",
        "nom": "Nouvelle analyse",
    },
    {
        "icone": "📊",
        "nom": "Tableau de bord",
    },
    {
        "icone": "🧠",
        "nom": "Explication IA",
    },
    {
        "icone": "📈",
        "nom": "Analyse du modèle",
    },
    {
        "icone": "📂",
        "nom": "Historique",
    },
    {
        "icone": "ℹ️",
        "nom": "À propos",
    },
]


# ==========================================================
# EN-TÊTE
# ==========================================================

def afficher_entete() -> None:
    """
    Affiche l'identité de RiskVision AI.
    """

    html_entete = (
        '<div class="riskvision-sidebar-brand">'
        f'<div class="riskvision-sidebar-logo">{ICON_AI}</div>'
        f'<div class="riskvision-sidebar-name">{APP_NAME}</div>'
        f'<div class="riskvision-sidebar-subtitle">{APP_SUBTITLE}</div>'
        '</div>'
    )

    st.sidebar.markdown(
        html_entete,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()


# ==========================================================
# NAVIGATION
# ==========================================================

def obtenir_icone_page(
    nom_page: str,
) -> str:
    """
    Retourne l'icône correspondant à une page.
    """

    for element in MENU:

        if element["nom"] == nom_page:
            return element["icone"]

    return "•"


def formater_page_navigation(
    nom_page: str,
) -> str:
    """
    Ajoute l'icône au nom de la page uniquement
    pour son affichage dans la sidebar.
    """

    icone = obtenir_icone_page(
        nom_page
    )

    return f"{icone}  {nom_page}"


def afficher_navigation() -> str:
    """
    Affiche le menu et retourne la page sélectionnée.
    """

    options = [
        element["nom"]
        for element in MENU
    ]

    # Sécurité si une ancienne valeur incompatible
    # existe encore dans la session Streamlit.
    if (
        "navigation" in st.session_state
        and st.session_state["navigation"] not in options
    ):
        st.session_state["navigation"] = "Accueil"

    
    choix = st.sidebar.radio(
        "Navigation",
        options=options,
        index=0,
        format_func=formater_page_navigation,
        label_visibility="collapsed",
        key="navigation",
    )
    return choix


# ==========================================================
# INFORMATIONS DU MODÈLE
# ==========================================================

def afficher_infos_modele() -> None:
    """
    Affiche les informations réelles du modèle.
    """

    metriques = charger_metriques()

    informations = obtenir_informations_modele()

    nom_modele = informations[
        "nom_modele"
    ].replace(
        "_",
        " ",
    ).title()

    st.sidebar.divider()

    html_modele = (
        '<div class="riskvision-model-card">'
        '<div class="riskvision-model-status">'
        '<span class="riskvision-status-dot"></span>'
        'Modèle opérationnel'
        '</div>'
        f'<div class="riskvision-model-title">{nom_modele}</div>'
        '<div class="riskvision-model-grid">'
        '<div>'
        '<span>F1-score</span>'
        f'<strong>{metriques["f1_score"] * 100:.2f} %</strong>'
        '</div>'
        '<div>'
        '<span>ROC-AUC</span>'
        f'<strong>{metriques["roc_auc"] * 100:.2f} %</strong>'
        '</div>'
        '<div>'
        '<span>Accuracy</span>'
        f'<strong>{metriques["accuracy"] * 100:.2f} %</strong>'
        '</div>'
        '<div>'
        '<span>Variables</span>'
        f'<strong>{informations["nombre_variables"]}</strong>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.sidebar.markdown(
        html_modele,
        unsafe_allow_html=True,
    )

    html_version = (
        '<div class="riskvision-sidebar-version">'
        f'RiskVision AI • Version {APP_VERSION}'
        '</div>'
    )

    st.sidebar.markdown(
        html_version,
        unsafe_allow_html=True,
    )


# ==========================================================
# COMPOSANT PUBLIC
# ==========================================================

def afficher_sidebar() -> str:
    """
    Construit la barre latérale complète.
    """

    afficher_entete()

    page_selectionnee = afficher_navigation()

    afficher_infos_modele()

    return page_selectionnee