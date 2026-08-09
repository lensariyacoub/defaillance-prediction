# scripts/analyse_shap.py

from __future__ import annotations

from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_PATH = Path("models/meilleur_modele_v2.joblib")
TEST_PATH = Path("data/processed/test.csv")

REPORTS_DIR = Path("reports/shap")

GLOBAL_CSV_PATH = REPORTS_DIR / "importance_shap_globale.csv"
GLOBAL_PNG_PATH = REPORTS_DIR / "importance_shap_globale.png"
WATERFALL_PNG_PATH = REPORTS_DIR / "explication_shap_locale.png"
LOCAL_CSV_PATH = REPORTS_DIR / "explication_shap_locale.csv"
REPORT_PATH = REPORTS_DIR / "rapport_shap.txt"
METADATA_PATH = REPORTS_DIR / "metadata_shap.json"

TARGET = "label_risque"

MAX_OBSERVATIONS_GLOBALES = 200
INDEX_OBSERVATION_LOCALE = 0
TOP_N_GLOBAL = 20
TOP_N_LOCAL = 15
RANDOM_STATE = 42


# ==================================================
# CHARGEMENT
# ==================================================

def charger_modele() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH.resolve()}"
        )

    objet_modele = joblib.load(MODEL_PATH)

    if not isinstance(objet_modele, dict):
        raise TypeError(
            "Le fichier modèle ne contient pas le dictionnaire attendu."
        )

    if "pipeline" not in objet_modele:
        raise KeyError(
            "La clé 'pipeline' est absente du fichier modèle."
        )

    return objet_modele


def charger_test() -> pd.DataFrame:
    if not TEST_PATH.exists():
        raise FileNotFoundError(
            f"Jeu de test introuvable : {TEST_PATH.resolve()}"
        )

    return pd.read_csv(
        TEST_PATH,
        encoding="utf-8-sig",
        dtype={
            "departement": "string",
            "greffe": "string",
            "type_entite": "string",
            "activite_probable": "string",
        },
    )


# ==================================================
# NOMS DES VARIABLES APRES ENCODAGE
# ==================================================

def extraire_noms_variables(
    pipeline,
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> list[str]:

    preprocesseur = pipeline.named_steps["preprocessing"]

    pipeline_categoriel = (
        preprocesseur
        .named_transformers_["categoriel"]
    )

    encodeur = pipeline_categoriel.named_steps["encodage"]

    noms_categorielles = (
        encodeur
        .get_feature_names_out(
            variables_categorielles
        )
        .tolist()
    )

    return noms_categorielles + list(
        variables_numeriques
    )


# ==================================================
# TRANSFORMATION
# ==================================================

def convertir_dense(matrice):
    if hasattr(matrice, "toarray"):
        return matrice.toarray()

    return np.asarray(matrice)


def preparer_donnees(
    objet_modele: dict,
    test_df: pd.DataFrame,
):
    pipeline = objet_modele["pipeline"]

    variables_categorielles = objet_modele[
        "variables_categorielles"
    ]
    variables_numeriques = objet_modele[
        "variables_numeriques"
    ]

    variables_modele = (
        variables_categorielles
        + variables_numeriques
    )

    X_test = test_df[
        variables_modele
    ].copy()

    y_test = (
        test_df[TARGET].astype(int)
        if TARGET in test_df.columns
        else None
    )

    preprocesseur = pipeline.named_steps[
        "preprocessing"
    ]

    X_transforme = preprocesseur.transform(
        X_test
    )

    X_dense = convertir_dense(
        X_transforme
    )

    noms_variables = extraire_noms_variables(
        pipeline,
        variables_categorielles,
        variables_numeriques,
    )

    if X_dense.shape[1] != len(noms_variables):
        raise ValueError(
            "Le nombre de colonnes transformées ne correspond pas "
            "au nombre de noms de variables."
        )

    return (
        X_test,
        y_test,
        X_dense,
        noms_variables,
    )


# ==================================================
# NORMALISATION DE LA SORTIE SHAP
# ==================================================

def selectionner_classe_positive(
    explication,
) -> shap.Explanation:
    """
    Gère les formats SHAP courants pour une classification binaire.

    Selon la version de SHAP, les valeurs peuvent être :
    - (observations, variables)
    - (observations, variables, classes)
    """

    valeurs = np.asarray(
        explication.values
    )

    base_values = np.asarray(
        explication.base_values
    )

    data = np.asarray(
        explication.data
    )

    if valeurs.ndim == 3:
        classe_positive = 1

        valeurs = valeurs[
            :,
            :,
            classe_positive,
        ]

        if base_values.ndim == 2:
            base_values = base_values[
                :,
                classe_positive,
            ]
        elif base_values.ndim == 1 and len(base_values) > 1:
            base_values = np.repeat(
                base_values[classe_positive],
                valeurs.shape[0],
            )

    elif valeurs.ndim != 2:
        raise ValueError(
            f"Format SHAP inattendu : {valeurs.shape}"
        )

    if base_values.ndim == 0:
        base_values = np.repeat(
            float(base_values),
            valeurs.shape[0],
        )

    if base_values.ndim == 1 and len(base_values) != valeurs.shape[0]:
        if len(base_values) == 2:
            base_values = np.repeat(
                base_values[1],
                valeurs.shape[0],
            )
        else:
            base_values = np.repeat(
                float(base_values.flat[0]),
                valeurs.shape[0],
            )

    return shap.Explanation(
        values=valeurs,
        base_values=base_values,
        data=data,
        feature_names=explication.feature_names,
    )


# ==================================================
# CALCUL SHAP
# ==================================================

def calculer_shap(
    objet_modele: dict,
    X_dense: np.ndarray,
    noms_variables: list[str],
) -> shap.Explanation:

    modele = objet_modele[
        "pipeline"
    ].named_steps["model"]

    nombre_observations = min(
        len(X_dense),
        MAX_OBSERVATIONS_GLOBALES,
    )

    generateur = np.random.default_rng(
        RANDOM_STATE
    )

    indices = generateur.choice(
        len(X_dense),
        size=nombre_observations,
        replace=False,
    )

    X_echantillon = X_dense[
        indices
    ]

    explainer = shap.TreeExplainer(
        modele
    )

    explication = explainer(
        X_echantillon,
        check_additivity=False,
    )

    explication.feature_names = noms_variables

    explication_positive = selectionner_classe_positive(
        explication
    )

    return explication_positive


# ==================================================
# IMPORTANCE GLOBALE
# ==================================================

def construire_importance_globale(
    explication: shap.Explanation,
) -> pd.DataFrame:

    importance_moyenne = np.mean(
        np.abs(explication.values),
        axis=0,
    )

    tableau = pd.DataFrame(
        {
            "variable": explication.feature_names,
            "importance_shap_moyenne": importance_moyenne,
        }
    )

    tableau = tableau.sort_values(
        by="importance_shap_moyenne",
        ascending=False,
    ).reset_index(drop=True)

    total = tableau[
        "importance_shap_moyenne"
    ].sum()

    if total > 0:
        tableau[
            "importance_shap_pourcentage"
        ] = (
            tableau["importance_shap_moyenne"]
            / total
            * 100
        )
    else:
        tableau[
            "importance_shap_pourcentage"
        ] = 0.0

    tableau.insert(
        0,
        "rang",
        range(
            1,
            len(tableau) + 1,
        ),
    )

    return tableau


def sauvegarder_graphique_global(
    explication: shap.Explanation,
) -> None:

    shap.plots.bar(
        explication,
        max_display=TOP_N_GLOBAL,
        show=False,
    )

    plt.title(
        "Importance globale des variables selon SHAP"
    )
    plt.tight_layout()

    plt.savefig(
        GLOBAL_PNG_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()


# ==================================================
# EXPLICATION LOCALE
# ==================================================

def construire_explication_locale(
    explication: shap.Explanation,
    index_observation: int,
) -> pd.DataFrame:

    if not 0 <= index_observation < len(
        explication.values
    ):
        raise IndexError(
            "INDEX_OBSERVATION_LOCALE est hors limites."
        )

    valeurs = explication.values[
        index_observation
    ]

    donnees = explication.data[
        index_observation
    ]

    tableau = pd.DataFrame(
        {
            "variable": explication.feature_names,
            "valeur_transformee": donnees,
            "contribution_shap": valeurs,
            "contribution_absolue": np.abs(valeurs),
        }
    )

    tableau["effet"] = np.where(
        tableau["contribution_shap"] > 0,
        "AUGMENTE_LA_SORTIE",
        np.where(
            tableau["contribution_shap"] < 0,
            "DIMINUE_LA_SORTIE",
            "NEUTRE",
        ),
    )

    tableau = tableau.sort_values(
        by="contribution_absolue",
        ascending=False,
    ).reset_index(drop=True)

    tableau.insert(
        0,
        "rang",
        range(
            1,
            len(tableau) + 1,
        ),
    )

    return tableau


def sauvegarder_waterfall(
    explication: shap.Explanation,
    index_observation: int,
) -> None:

    shap.plots.waterfall(
        explication[
            index_observation
        ],
        max_display=TOP_N_LOCAL,
        show=False,
    )

    plt.title(
        "Explication SHAP d'une prédiction individuelle"
    )
    plt.tight_layout()

    plt.savefig(
        WATERFALL_PNG_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()


# ==================================================
# RAPPORT
# ==================================================

def creer_rapport(
    tableau_global: pd.DataFrame,
    tableau_local: pd.DataFrame,
    objet_modele: dict,
    test_df: pd.DataFrame,
) -> str:

    lignes = []

    lignes.append("=" * 72)
    lignes.append("RAPPORT D'EXPLICABILITE SHAP")
    lignes.append("=" * 72)
    lignes.append("")

    lignes.append(
        f"Modèle : {objet_modele.get('nom_modele', 'inconnu')}"
    )
    lignes.append(
        f"Observations utilisées pour l'analyse globale : "
        f"{min(len(test_df), MAX_OBSERVATIONS_GLOBALES)}"
    )
    lignes.append(
        f"Observation locale analysée : "
        f"{INDEX_OBSERVATION_LOCALE}"
    )

    lignes.append("")
    lignes.append("TOP DES VARIABLES GLOBALES")
    lignes.append("-" * 72)

    for _, ligne in tableau_global.head(
        TOP_N_GLOBAL
    ).iterrows():
        lignes.append(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable']} : "
            f"{ligne['importance_shap_pourcentage']:.4f} %"
        )

    lignes.append("")
    lignes.append("PRINCIPALES CONTRIBUTIONS LOCALES")
    lignes.append("-" * 72)

    for _, ligne in tableau_local.head(
        TOP_N_LOCAL
    ).iterrows():
        lignes.append(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable']} | "
            f"SHAP={ligne['contribution_shap']:.6f} | "
            f"{ligne['effet']}"
        )

    lignes.append("")
    lignes.append("INTERPRETATION")
    lignes.append("-" * 72)
    lignes.append(
        "L'importance globale correspond à la moyenne des valeurs "
        "SHAP absolues sur l'échantillon."
    )
    lignes.append(
        "Une contribution SHAP positive déplace la sortie du modèle "
        "vers la classe positive ; une contribution négative la réduit."
    )
    lignes.append(
        "Les contributions décrivent le comportement du modèle, "
        "pas une relation de causalité économique."
    )

    lignes.append("")
    lignes.append("ATTENTION METHODOLOGIQUE")
    lignes.append("-" * 72)
    lignes.append(
        "Le label actuel est construit à partir du type d'annonce "
        "BODACC."
    )
    lignes.append(
        "Le modèle et ses explications restent exploratoires."
    )
    lignes.append(
        "La sortie ne doit pas être présentée comme une probabilité "
        "réelle et validée de défaillance future."
    )

    return "\n".join(lignes)


# ==================================================
# EXECUTION
# ==================================================

def main() -> None:

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    objet_modele = charger_modele()
    test_df = charger_test()

    (
        X_test,
        y_test,
        X_dense,
        noms_variables,
    ) = preparer_donnees(
        objet_modele,
        test_df,
    )

    explication = calculer_shap(
        objet_modele,
        X_dense,
        noms_variables,
    )

    tableau_global = construire_importance_globale(
        explication
    )

    tableau_local = construire_explication_locale(
        explication,
        INDEX_OBSERVATION_LOCALE,
    )

    tableau_global.to_csv(
        GLOBAL_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    tableau_local.to_csv(
        LOCAL_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    sauvegarder_graphique_global(
        explication
    )

    sauvegarder_waterfall(
        explication,
        INDEX_OBSERVATION_LOCALE,
    )

    rapport = creer_rapport(
        tableau_global,
        tableau_local,
        objet_modele,
        test_df,
    )

    REPORT_PATH.write_text(
        rapport,
        encoding="utf-8",
    )

    metadata = {
        "modele": objet_modele.get(
            "nom_modele",
            "inconnu",
        ),
        "nombre_observations_globales": int(
            len(explication.values)
        ),
        "nombre_variables": int(
            len(noms_variables)
        ),
        "index_observation_locale": (
            INDEX_OBSERVATION_LOCALE
        ),
        "classe_reelle_locale": (
            int(y_test.iloc[INDEX_OBSERVATION_LOCALE])
            if y_test is not None
            else None
        ),
    }

    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("ANALYSE SHAP TERMINEE")
    print("=" * 72)

    print("\nTop 10 variables globales :")

    for _, ligne in tableau_global.head(10).iterrows():
        print(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable']} "
            f"=> {ligne['importance_shap_pourcentage']:.4f} %"
        )

    print("\nTop contributions locales :")

    for _, ligne in tableau_local.head(10).iterrows():
        print(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable']} "
            f"=> {ligne['contribution_shap']:.6f} "
            f"({ligne['effet']})"
        )

    print("")
    print(f"CSV global : {GLOBAL_CSV_PATH}")
    print(f"Graphique global : {GLOBAL_PNG_PATH}")
    print(f"CSV local : {LOCAL_CSV_PATH}")
    print(f"Waterfall local : {WATERFALL_PNG_PATH}")
    print(f"Rapport : {REPORT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()