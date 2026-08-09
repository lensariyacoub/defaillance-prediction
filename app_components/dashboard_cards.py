"""
RiskVision AI - Cartes KPI réutilisables.
"""

from __future__ import annotations

import streamlit as st


def afficher_kpi(
    titre: str,
    valeur: str | int | float,
    description: str = "",
    icone: str = "📊",
) -> None:
    """
    Affiche une carte KPI personnalisée.
    """

    html_carte = (
        '<div class="riskvision-kpi-card">'
        '<div class="riskvision-kpi-header">'
        f'<div class="riskvision-kpi-icon">{icone}</div>'
        f'<div class="riskvision-kpi-title">{titre}</div>'
        '</div>'
        f'<div class="riskvision-kpi-value">{valeur}</div>'
        f'<div class="riskvision-kpi-description">{description}</div>'
        '</div>'
    )

    st.markdown(
        html_carte,
        unsafe_allow_html=True,
    )
    