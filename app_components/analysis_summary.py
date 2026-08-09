"""
RiskVision AI - Résumé automatique d'une analyse.
"""

from __future__ import annotations

import streamlit as st


def aller_explication_ia() -> None:
    """
    Sélectionne directement la page Explication IA
    dans la navigation Streamlit.
    """

    st.session_state["navigation"] = "Explication IA"


def afficher_resume_analyse(
    observation,
    resultat: dict,
) -> None:
    """
    Affiche un résumé métier lisible
    à partir des résultats réels du modèle.
    """

    probabilite_risque = (
        resultat["probabilite_risque"]
        * 100
    )

    probabilite_non_risque = (
        resultat["probabilite_non_risque"]
        * 100
    )

    decision = resultat["decision"]

    st.markdown(
        '<div class="riskvision-eyebrow">'
        "Synthèse automatique"
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader(
        "Résumé de l’analyse"
    )

    texte = (
        f"L’entreprise **{observation.nom_entreprise}**, "
        f"rattachée au **greffe de {observation.greffe}** "
        f"et identifiée dans l’activité "
        f"**{observation.activite_probable}**, "
        f"est classée **{decision}** par le modèle. "
        f"La probabilité estimée de risque est de "
        f"**{probabilite_risque:.2f} %**, "
        f"contre **{probabilite_non_risque:.2f} %** "
        f"pour la classe non-risque. "
        "Pour comprendre les facteurs ayant influencé "
        "cette décision, consultez la rubrique "
        "**Explication IA**."
    )

    st.info(
        texte
    )

    st.button(
        "Voir l’explication IA",
        use_container_width=True,
        on_click=aller_explication_ia,
    )