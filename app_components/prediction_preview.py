"""
RiskVision AI - Aperçu intelligent avant prédiction.
"""

from __future__ import annotations

import streamlit as st

from scripts.utils_prediction import (
    detecter_activite,
    detecter_greffe,
)


def afficher_apercu_prediction(
    nom_entreprise: str,
    departement: str,
    type_entite: str,
) -> None:
    """
    Affiche les informations détectées automatiquement
    avant le lancement de la prédiction.
    """

    nom_nettoye = nom_entreprise.strip()

    departement_nettoye = departement.strip().upper()

    greffe = (
        detecter_greffe(departement_nettoye)
        if departement_nettoye
        else "En attente"
    )

    activite = (
        detecter_activite(nom_nettoye)
        if nom_nettoye
        else "En attente"
    )

    longueur_nom = len(nom_nettoye)

    nombre_mots = (
        len(nom_nettoye.split())
        if nom_nettoye
        else 0
    )

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Aperçu automatique"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Informations détectées"
    )

    colonne_greffe, colonne_activite = st.columns(2)

    with colonne_greffe:
        st.markdown(
            (
                '<div class="riskvision-card">'
                '<div class="riskvision-card-title">'
                "Greffe détecté"
                "</div>"
                '<div class="riskvision-card-value">'
                f"{greffe}"
                "</div>"
                '<div class="riskvision-card-description">'
                "Déduit automatiquement à partir "
                "du code du département."
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with colonne_activite:
        st.markdown(
            (
                '<div class="riskvision-card">'
                '<div class="riskvision-card-title">'
                "Activité probable"
                "</div>"
                '<div class="riskvision-card-value">'
                f"{activite}"
                "</div>"
                '<div class="riskvision-card-description">'
                "Déduite automatiquement à partir "
                "du nom de l’entreprise."
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    st.write("")

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Variables calculées"
        "</div>",
        unsafe_allow_html=True,
    )

    colonne_nom, colonne_mots, colonne_type = st.columns(3)

    with colonne_nom:
        st.metric(
            "Longueur du nom",
            longueur_nom,
        )

    with colonne_mots:
        st.metric(
            "Nombre de mots",
            nombre_mots,
        )

    with colonne_type:
        st.metric(
            "Type d’entité",
            type_entite,
        )