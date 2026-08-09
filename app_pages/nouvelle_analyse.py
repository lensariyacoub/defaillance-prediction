"""
RiskVision AI - Nouvelle analyse.
"""

from __future__ import annotations

import streamlit as st

from app_components.animation_analyse import (
    jouer_animation_analyse,
)


from app_components.history_manager import (
    enregistrer_analyse,
)
from app_components.model_loader import (
    predire_observation,
)
from app_components.prediction_preview import (
    afficher_apercu_prediction,
)
from app_components.styles import (
    afficher_hero,
)
from scripts.utils_prediction import (
    construire_observation,
)
from app_components.analysis_summary import (
    afficher_resume_analyse,
)

from app_components.pdf_report import (
    generer_rapport_pdf,
)


def afficher_nouvelle_analyse() -> None:
    """
    Affiche la page de prédiction.
    """

    afficher_hero(
        titre="Nouvelle analyse",
        sous_titre=(
            "Analysez une entreprise en utilisant "
            "le modèle Random Forest."
        ),
        badge="PRÉDICTION • MACHINE LEARNING",
    )

    with st.form(
        "formulaire_nouvelle_analyse"
    ):

        st.subheader(
            "Informations sur l’entreprise"
        )

        nom_entreprise = st.text_input(
            "Nom de l’entreprise",
            placeholder="Exemple : LENSARI DATA CONSEIL",
        )

        departement = st.text_input(
            "Code du département",
            placeholder="Exemple : 49",
            max_chars=3,
        )

        type_entite = st.selectbox(
            "Type d’entité",
            options=[
                "ENTREPRISE",
                "PERSONNE_PHYSIQUE",
            ],
        )

        bouton_analyser = st.form_submit_button(
            "Analyser l’entreprise",
            use_container_width=True,
        )

        afficher_apercu_prediction(
            nom_entreprise=nom_entreprise,
            departement=departement,
            type_entite=type_entite,
    )

    if bouton_analyser:

        try:

            observation = construire_observation(
                nom_entreprise=nom_entreprise,
                departement=departement,
                type_entite=type_entite,
            )

            jouer_animation_analyse(
               observation
            )

            resultat = predire_observation(
                observation.dataframe
            )

            enregistrer_analyse(
                observation,
                resultat,
            )
            st.session_state["derniere_analyse"] = {
                "observation": observation,
                "resultat": resultat,
            }

        except ValueError as erreur:

            st.error(
                str(erreur)
            )

            return

        

        st.markdown(
            '<div id="resultat-analyse"></div>',
            unsafe_allow_html=True,
       )

        st.divider()

        st.subheader(
             f"Résultat pour {observation.nom_entreprise}"
      )

        colonne_1, colonne_2, colonne_3 = st.columns(
            3
        )

        with colonne_1:

            st.metric(
                "Greffe détecté",
                observation.greffe,
            )

        with colonne_2:

            st.metric(
                "Activité détectée",
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

        st.progress(
            resultat["probabilite_risque"],
            text=(
                "Sortie du modèle pour la classe risque : "
                f"{resultat['probabilite_risque'] * 100:.2f} %"
            ),
        )

        if resultat["classe_predite"] == 1:

            st.error(
                "Le modèle classe cette observation "
                "dans la catégorie RISQUE."
            )

        else:

            st.success(
                "Le modèle classe cette observation "
                "dans la catégorie NON RISQUE."
            )

        with st.expander(
            "Voir les variables transmises au modèle"
        ):

            st.dataframe(
                observation.dataframe,
                use_container_width=True,
                hide_index=True,
            )

    if "derniere_analyse" in st.session_state:

     analyse_courante = st.session_state[
        "derniere_analyse"
     ]

     observation_courante = analyse_courante[
        "observation"
     ]

     resultat_courant = analyse_courante[
        "resultat"
     ]

     afficher_resume_analyse(
        observation_courante,
        resultat_courant,
     )

     rapport_pdf = generer_rapport_pdf(
        observation_courante,
        resultat_courant,
     )

     st.download_button(
        label="Télécharger le rapport PDF",
        data=rapport_pdf,
        file_name=(
            f"rapport_"
            f"{observation_courante.nom_entreprise.lower().replace(' ', '_')}"
            f".pdf"
        ),
        mime="application/pdf",
        use_container_width=True,
     )

     st.warning(
        "Cette sortie est exploratoire et ne constitue "
        "pas une notation financière officielle."
     )

     st.components.v1.html(
        """
        <script>
            const element = window.parent.document.getElementById(
                "resultat-analyse"
            );

            if (element) {
                element.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        </script>
        """,
        height=0,
     )