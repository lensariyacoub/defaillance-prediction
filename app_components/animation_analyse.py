"""
RiskVision AI - Animation intelligente de l'analyse.
"""

from __future__ import annotations

import time

import streamlit as st


def jouer_animation_analyse(
    observation,
) -> None:
    """
    Affiche les différentes étapes réelles de préparation
    d'une entreprise avant la prédiction.
    """

    barre = st.progress(0)

    statut = st.empty()

    etapes = [
        (
            "🔍 Analyse du nom de l’entreprise",
            f"✓ {observation.nom_entreprise}",
            15,
        ),
        (
            "📍 Vérification du département",
            f"✓ Département {observation.departement}",
            30,
        ),
        (
            "🏛️ Détection du greffe",
            f"✓ {observation.greffe}",
            45,
        ),
        (
            "🏢 Identification de l’activité",
            f"✓ {observation.activite_probable}",
            60,
        ),
        (
            "🧠 Préparation des variables",
            (
                f"✓ {len(observation.nom_entreprise)} caractères • "
                f"{len(observation.nom_entreprise.split())} mots • "
                f"{observation.type_entite}"
            ),
            80,
        ),
        (
            "🌲 Préparation du modèle Random Forest",
            "✓ Variables prêtes pour la prédiction",
            100,
        ),
    ]

    historique_etapes = []

    for titre, resultat, progression in etapes:

        historique_etapes.append(
            f"**{titre}**  \n{resultat}"
        )

        statut.markdown(
            "\n\n".join(
                historique_etapes
            )
        )

        barre.progress(
            progression
        )

        time.sleep(
            0.30
        )

    statut.success(
        "✅ Préparation terminée. Calcul de la prédiction..."
    )