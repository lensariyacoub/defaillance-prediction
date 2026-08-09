"""
RiskVision AI - Graphiques réutilisables du tableau de bord.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st


def afficher_repartition_decisions(
    nombre_risque: int,
    nombre_non_risque: int,
) -> None:
    """
    Affiche un diagramme en anneau représentant
    la répartition entre RISQUE et NON RISQUE.
    """

    total = nombre_risque + nombre_non_risque

    if total == 0:

        st.info(
            "Aucune analyse n'est encore disponible."
        )

        return

    valeurs = [
        nombre_non_risque,
        nombre_risque,
    ]

    libelles = [
        "Non risque",
        "Risque",
    ]

    figure, axe = plt.subplots(
        figsize=(7, 5)
    )

    axe.pie(
        valeurs,
        labels=libelles,
        autopct="%1.1f %%",
        startangle=90,
        wedgeprops={
            "width": 0.38,
            "edgecolor": "white",
        },
        textprops={
            "fontsize": 11,
        },
    )

    axe.text(
        0,
        0.08,
        str(total),
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=26,
        fontweight="bold",
    )

    axe.text(
        0,
        -0.14,
        "analyses",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=11,
    )

    axe.set_title(
        "Répartition des décisions",
        fontsize=15,
        fontweight="bold",
        pad=18,
    )

    axe.axis(
        "equal"
    )

    figure.tight_layout()

    st.pyplot(
        figure,
        use_container_width=True,
    )

    plt.close(
        figure
    )