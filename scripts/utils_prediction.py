"""
Fonctions utilitaires pour la prédiction.

Toutes les fonctions de préparation des données
sont regroupées ici afin d'éviter d'alourdir
predict.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


# ==================================================
# CLASSE METIER
# ==================================================

@dataclass(slots=True)
class ObservationEntreprise:
    """
    Représente une entreprise prête
    à être analysée par le modèle.
    """

    nom_entreprise: str

    departement: str

    type_entite: str

    greffe: str

    activite_probable: str

    dataframe: pd.DataFrame

# ==================================================
# GREFFES PAR DEPARTEMENT
# ==================================================

GREFFES = {
    "01": "Bourg-en-Bresse",
    "02": "Saint-Quentin",
    "03": "Cusset",
    "06": "Grasse",
    "13": "Marseille",
    "26": "Romans",
    "31": "Toulouse",
    "33": "Bordeaux",
    "35": "Rennes",
    "44": "Nantes",
    "49": "Angers",
    "51": "Reims",
    "59": "Lille",
    "69": "Lyon",
    "74": "Annecy",
    "75": "Paris",
    "78": "Versailles",
    "92": "Nanterre",
    "974": "Saint Denis de La Réunion",
}
# ==================================================
# DETECTION DU GREFFE
# ==================================================

def detecter_greffe(departement: str) -> str:
    """
    Retourne automatiquement le greffe correspondant
    à un département.

    Si le département est inconnu,
    on retourne 'Inconnu'.
    """

    departement = departement.strip().upper()

    return GREFFES.get(
        departement,
        "Inconnu"
    )

# ==================================================
# MOTS-CLES PAR ACTIVITE
# ==================================================

ACTIVITES = {
    "IMMOBILIER": [
        "IMMOBILIER",
        "IMMO",
        "SCI",
        "FONCIER",
        "HABITAT",
    ],

    "RESTAURATION": [
        "RESTAURANT",
        "BISTROT",
        "BRASSERIE",
        "PIZZA",
        "PIZZERIA",
        "SNACK",
        "KEBAB",
        "CAFE",
        "CAFÉ",
        "BAR",
        "BOULANGERIE",
        "PATISSERIE",
        "PÂTISSERIE",
        "TRAITEUR",
        "BURGER",
        "FOOD",
    ],

    "AUTOMOBILE": [
        "AUTO",
        "AUTOMOBILE",
        "GARAGE",
        "MOTO",
        "SCOOTER",
        "SCOOT",
        "CARROSSERIE",
        "VEHICULE",
        "VÉHICULE",
    ],

    "BATIMENT": [
        "BATIMENT",
        "BÂTIMENT",
        "BTP",
        "CONSTRUCTION",
        "RENOVATION",
        "RÉNOVATION",
        "MACONNERIE",
        "MAÇONNERIE",
        "FACADE",
        "FAÇADE",
        "TOITURE",
        "MENUISERIE",
        "PLOMBERIE",
        "PEINTURE",
    ],

    "CONSEIL": [
        "CONSEIL",
        "CONSULTING",
        "EXPERTISE",
        "AUDIT",
    ],

    "INFORMATIQUE": [
        "INFORMATIQUE",
        "DIGITAL",
        "SOFTWARE",
        "WEB",
        "DATA",
        "TECH",
        "CLOUD",
        "TELECOM",
        "TÉLÉCOM",
    ],

    "SANTE": [
        "SANTE",
        "SANTÉ",
        "MEDICAL",
        "MÉDICAL",
        "PHARMA",
        "CLINIQUE",
        "DENTAIRE",
        "OPTIQUE",
    ],

    "TRANSPORT": [
        "TRANSPORT",
        "LOGISTIQUE",
        "LIVRAISON",
        "MESSAGERIE",
    ],

    "FINANCE": [
        "FINANCE",
        "BANQUE",
        "CREDIT",
        "CRÉDIT",
        "ASSURANCE",
        "CAPITAL",
        "INVEST",
        "HOLDING",
    ],

    "COMMERCE": [
        "COMMERCE",
        "BOUTIQUE",
        "SHOP",
        "DISTRIBUTION",
        "NEGOCE",
        "NÉGOCE",
    ],

    "AGRICULTURE": [
        "AGRICULTURE",
        "AGRICOLE",
        "GAEC",
        "EARL",
        "SCEA",
        "ELEVAGE",
        "ÉLEVAGE",
    ],

    "INDUSTRIE": [
        "INDUSTRIE",
        "INDUSTRIEL",
        "FABRICATION",
        "MANUFACTURE",
    ],
}


# ==================================================
# DETECTION DE L'ACTIVITE
# ==================================================

def detecter_activite(nom_entreprise: str) -> str:
    """
    Détecte une activité probable à partir du nom de l'entreprise.

    Si aucun mot-clé n'est trouvé, retourne 'AUTRE'.
    """

    nom_normalise = nom_entreprise.strip().upper()

    for activite, mots_cles in ACTIVITES.items():

        for mot_cle in mots_cles:

            if mot_cle in nom_normalise:

                return activite

    return "AUTRE"


# ==================================================
# CONSTRUCTION DE L'OBSERVATION
# ==================================================

def construire_observation(
    nom_entreprise: str,
    departement: str,
    type_entite: str,
) -> ObservationEntreprise:
    """
    Prépare toutes les informations nécessaires
    à l'analyse d'une entreprise.
    """

    nom_nettoye = nom_entreprise.strip()

    departement_nettoye = (
        departement
        .strip()
        .upper()
    )

    type_entite_nettoye = (
        type_entite
        .strip()
        .upper()
    )

    if not nom_nettoye:
        raise ValueError(
            "Le nom de l'entreprise ne peut pas être vide."
        )

    if not departement_nettoye:
        raise ValueError(
            "Le département ne peut pas être vide."
        )

    types_autorises = {
        "ENTREPRISE",
        "PERSONNE_PHYSIQUE",
    }

    if type_entite_nettoye not in types_autorises:
        raise ValueError(
            "Le type d'entité doit être ENTREPRISE "
            "ou PERSONNE_PHYSIQUE."
        )

    greffe = detecter_greffe(
        departement_nettoye
    )

    activite_probable = detecter_activite(
        nom_nettoye
    )

    maintenant = datetime.now()

    donnees = {
        "departement": departement_nettoye,
        "greffe": greffe,
        "type_entite": type_entite_nettoye,
        "activite_probable": activite_probable,
        "longueur_nom": len(
            nom_nettoye
        ),
        "nombre_mots_nom": len(
            nom_nettoye.split()
        ),
        "annee_publication": maintenant.year,
        "mois_publication": maintenant.month,
        "jour_semaine_publication": maintenant.weekday(),
    }

    dataframe = pd.DataFrame(
        [donnees]
    )

    return ObservationEntreprise(
        nom_entreprise=nom_nettoye,
        departement=departement_nettoye,
        type_entite=type_entite_nettoye,
        greffe=greffe,
        activite_probable=activite_probable,
        dataframe=dataframe,
    )

# ==================================================
# TESTS
# ==================================================
if __name__ == "__main__":

    print("=" * 60)
    print("TEST DE detecter_greffe()")
    print("=" * 60)

    tests_departements = [
        "49",
        "75",
        "13",
        "92",
        "35",
        "999",
    ]

    for departement in tests_departements:

        print(
            f"{departement} -> "
            f"{detecter_greffe(departement)}"
        )

    print("\n" + "=" * 60)
    print("TEST DE detecter_activite()")
    print("=" * 60)

    tests_entreprises = [
        "LE BISTROT DES REMPARTS",
        "GARAGE DUPONT",
        "LENSARI DATA CONSEIL",
        "ABC BATIMENT",
        "SCI LES OLIVIERS",
        "TECH SOLUTIONS",
        "MARTIN JEAN",
    ]

    for nom in tests_entreprises:

        print(
            f"{nom} -> "
            f"{detecter_activite(nom)}"
        )

    print("\n" + "=" * 60)
    print("TEST DE construire_observation()")
    print("=" * 60)

    observation = construire_observation(
        nom_entreprise="LENSARI DATA CONSEIL",
        departement="49",
        type_entite="entreprise",
    )

    print(
        f"Nom : {observation.nom_entreprise}"
    )

    print(
        f"Département : {observation.departement}"
    )

    print(
        f"Greffe : {observation.greffe}"
    )

    print(
        f"Activité : {observation.activite_probable}"
    )

    print(
        observation.dataframe.to_string(
            index=False
        )
    )