"""
RiskVision AI - Mise en forme des variables SHAP.

Traduit les noms techniques issus du One-Hot Encoding
en libellés compréhensibles par l'utilisateur.
"""

from __future__ import annotations


def traduire_variable(nom: str) -> str:
    """
    Transforme un nom de variable technique
    en texte lisible.
    """

    if nom.startswith("type_entite_"):
        valeur = nom.replace(
            "type_entite_",
            "",
        ).replace(
            "_",
            " ",
        ).title()

        return f"Type d'entité : {valeur}"

    if nom.startswith("activite_probable_"):
        valeur = nom.replace(
            "activite_probable_",
            "",
        ).replace(
            "_",
            " ",
        ).title()

        return f"Activité : {valeur}"

    if nom.startswith("departement_"):
        valeur = nom.replace(
            "departement_",
            "",
        )

        return f"Département : {valeur}"

    if nom.startswith("greffe_"):
        valeur = nom.replace(
            "greffe_",
            "",
        ).replace(
            "_",
            " ",
        )

        return f"Greffe : {valeur}"

    if nom == "longueur_nom":
        return "Longueur du nom"

    if nom == "nombre_mots_nom":
        return "Nombre de mots"

    if nom == "annee_publication":
        return "Année de publication"

    if nom == "mois_publication":
        return "Mois de publication"

    if nom == "jour_semaine_publication":
        return "Jour de publication"

    return nom.replace(
        "_",
        " ",
    ).title()


def qualifier_influence(
    contribution: float,
) -> str:
    """
    Traduit l'intensité d'une contribution SHAP
    en niveau compréhensible.
    """

    valeur_absolue = abs(
        contribution
    )

    if valeur_absolue >= 0.04:
        return "Très forte"

    if valeur_absolue >= 0.02:
        return "Forte"

    if valeur_absolue >= 0.01:
        return "Moyenne"

    if valeur_absolue >= 0.005:
        return "Faible"

    return "Très faible"


def traduire_effet(
    effet: str,
) -> str:
    """
    Traduit un effet technique SHAP
    en libellé lisible.
    """

    if effet == "AUGMENTE_LE_RISQUE":
        return "🔴 Augmente le risque"

    if effet == "DIMINUE_LE_RISQUE":
        return "🟢 Réduit le risque"

    return "🟠 Effet neutre"


def expliquer_facteur(
    nom_variable: str,
    contribution: float,
    valeur_transformee: float,
) -> str:
    """
    Génère une interprétation lisible d'un facteur SHAP
    en tenant compte de la valeur réellement transmise
    au modèle.
    """

    variable_lisible = traduire_variable(
        nom_variable
    )

    niveau = qualifier_influence(
        contribution
    ).lower()

    if contribution > 0:
        direction = "augmente"

    elif contribution < 0:
        direction = "réduit"

    else:
        direction = "ne modifie pratiquement pas"

    est_variable_categorielle = (
        nom_variable.startswith("type_entite_")
        or nom_variable.startswith("activite_probable_")
        or nom_variable.startswith("departement_")
        or nom_variable.startswith("greffe_")
    )

    if est_variable_categorielle:

        if valeur_transformee == 1:
            return (
                f"**{variable_lisible}** — "
                f"cette modalité est présente et {direction} "
                f"le niveau de risque estimé par le modèle, "
                f"avec une influence {niveau}."
            )

        if valeur_transformee == 0:
            return (
                f"**{variable_lisible}** — "
                f"cette modalité est absente et son absence "
                f"{direction} le niveau de risque estimé "
                f"par le modèle, avec une influence {niveau}."
            )

        return (
            f"**{variable_lisible}** — "
            f"cette modalité prend la valeur "
            f"{valeur_transformee:g} et {direction} "
            f"le niveau de risque estimé par le modèle, "
            f"avec une influence {niveau}."
        )

    return (
        f"**{variable_lisible}** — "
        f"cette caractéristique {direction} le niveau de risque "
        f"estimé par le modèle, avec une influence "
        f"{niveau}."
    )
