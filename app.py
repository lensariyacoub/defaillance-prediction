"""
RiskVision AI - Application principale.
"""

from __future__ import annotations

import streamlit as st

from app_pages.accueil import (
    afficher_accueil,
)
from app_pages.analyse_modele import (
    afficher_analyse_modele,
)
from app_pages.explication_ia import (
    afficher_explication_ia,
)
from app_pages.historique import (
    afficher_historique,
)
from app_pages.nouvelle_analyse import (
    afficher_nouvelle_analyse,
)
from app_pages.tableau_bord import (
    afficher_tableau_bord,
)

from app_components.sidebar import (
    afficher_sidebar,
)
from app_components.styles import (
    appliquer_styles_globaux,
)
from app_components.theme import (
    APP_NAME,
)


def main() -> None:
    """
    Lance l'application RiskVision AI.
    """

    st.set_page_config(
        page_title=APP_NAME,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    appliquer_styles_globaux()

    page_selectionnee = afficher_sidebar()

    if page_selectionnee == "Accueil":

        afficher_accueil()

    elif page_selectionnee == "Nouvelle analyse":

        afficher_nouvelle_analyse()

    elif page_selectionnee == "Tableau de bord":

        afficher_tableau_bord()

    elif page_selectionnee == "Explication IA":

        afficher_explication_ia()

    elif page_selectionnee == "Analyse du modèle":

        afficher_analyse_modele()

    elif page_selectionnee == "Historique":

        afficher_historique()

    else:

        st.title(
            page_selectionnee
        )

        st.info(
            f"Page sélectionnée : {page_selectionnee}"
        )


if __name__ == "__main__":
    main()