# ==================================================
# PREDICTION DE RISQUE D'UNE ENTREPRISE
# ==================================================

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from datetime import datetime
from utils_prediction import (
    detecter_activite,
    detecter_greffe,
)

# ==================================================
# CONFIGURATION
# ==================================================

MODEL_PATH = Path("models/meilleur_modele_v2.joblib")


# ==================================================
# CHARGEMENT DU MODELE
# ==================================================

def charger_modele():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(

            f"Modèle introuvable : {MODEL_PATH.resolve()}"

        )

    objet = joblib.load(MODEL_PATH)

    print("=" * 60)
    print("MODELE CHARGE AVEC SUCCES")
    print("=" * 60)

    print(f"Nom du modèle : {objet['nom_modele']}")

    print(f"Cible : {objet['target']}")

    return objet


# ==================================================
# EXECUTION
# ==================================================

def main():

    objet_modele = charger_modele()

    nom_entreprise, dataframe = (
        creer_entreprise_test()
    )

    predire_risque(
        objet_modele,
        nom_entreprise,
        dataframe,
    )
    
    # ==================================================
# PREDICTION
# ==================================================

def predire_risque(
    objet_modele,
    nom_entreprise,
    dataframe,
):

    pipeline = objet_modele["pipeline"]

    classe_predite = int(
        pipeline.predict(dataframe)[0]
    )

    probabilites = pipeline.predict_proba(
        dataframe
    )[0]

    probabilite_non_risque = float(
        probabilites[0]
    )

    probabilite_risque = float(
        probabilites[1]
    )

    decision = (
        "RISQUE"
        if classe_predite == 1
        else "NON RISQUE"
    )

    print("\n" + "=" * 60)
    print("RESULTAT DE LA PREDICTION")
    print("=" * 60)

    print(
        f"Entreprise : {nom_entreprise}"
    )

    print(
        "Probabilité non risque : "
        f"{probabilite_non_risque * 100:.2f} %"
    )

    print(
        "Probabilité risque     : "
        f"{probabilite_risque * 100:.2f} %"
    )

    print(
        f"Classe prédite : {classe_predite}"
    )

    print(
        f"Décision : {decision}"
    )

    print("=" * 60)

    return {
        "entreprise": nom_entreprise,
        "classe_predite": classe_predite,
        "probabilite_non_risque": probabilite_non_risque,
        "probabilite_risque": probabilite_risque,
        "decision": decision,
    }


# ==================================================
# VALIDATION DES CHOIX UTILISATEUR
# ==================================================

def demander_choix(message, valeurs_autorisees):

    while True:

        valeur = input(
            message
        ).strip().upper()

        if valeur in valeurs_autorisees:

            return valeur

        print(
            "Valeur incorrecte."
        )

        print(
            "Valeurs autorisées : "
            + ", ".join(valeurs_autorisees)
        )


# ==================================================
# CREATION D'UNE ENTREPRISE A TESTER
# ==================================================

def creer_entreprise_test():

    print("\n" + "=" * 60)
    print("SAISIE D'UNE NOUVELLE ENTREPRISE")
    print("=" * 60)

    nom_entreprise = input(
        "Nom de l'entreprise : "
    ).strip()

    while not nom_entreprise:

        print(
            "Le nom ne peut pas être vide."
        )

        nom_entreprise = input(
            "Nom de l'entreprise : "
        ).strip()

    departement = input(
        "Département, par exemple 49 : "
    ).strip().upper()

    while not departement:

        print(
            "Le département ne peut pas être vide."
        )

        departement = input(
            "Département : "
        ).strip().upper()

    greffe = detecter_greffe(
        departement
    )

    print(
        f"Greffe détecté automatiquement : {greffe}"
    )

    type_entite = demander_choix(
        (
            "Type d'entité "
            "(ENTREPRISE ou PERSONNE_PHYSIQUE) : "
        ),
        [
            "ENTREPRISE",
            "PERSONNE_PHYSIQUE",
        ],
    )

    activite_probable = detecter_activite(
        nom_entreprise
    )

    print(
        "Activité détectée automatiquement : "
        f"{activite_probable}"
    )

    maintenant = datetime.now()

    entreprise = {
        "departement": departement,
        "greffe": greffe,
        "type_entite": type_entite,
        "activite_probable": activite_probable,
        "longueur_nom": len(
            nom_entreprise
        ),
        "nombre_mots_nom": len(
            nom_entreprise.split()
        ),
        "annee_publication": maintenant.year,
        "mois_publication": maintenant.month,
        "jour_semaine_publication": maintenant.weekday(),
    }

    dataframe = pd.DataFrame(
        [entreprise]
    )

    print("\nEntreprise préparée :")

    print(
        dataframe.to_string(
            index=False
        )
    )

    return nom_entreprise, dataframe

if __name__ == "__main__":

    main()