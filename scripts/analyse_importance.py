# scripts/analyse_importance.py

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_PATH = Path("models/meilleur_modele_v2.joblib")

REPORTS_DIR = Path("reports")

CSV_PATH = REPORTS_DIR / "importance_variables.csv"
PNG_PATH = REPORTS_DIR / "importance_variables.png"
TXT_PATH = REPORTS_DIR / "rapport_importance.txt"

TOP_N = 20


# ==================================================
# CHARGEMENT DU MODELE
# ==================================================

def charger_modele(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {path.resolve()}"
        )

    objet = joblib.load(path)

    if not isinstance(objet, dict):
        raise TypeError(
            "Le fichier du modèle ne contient pas le dictionnaire attendu."
        )

    if "pipeline" not in objet:
        raise KeyError(
            "La clé 'pipeline' est absente du fichier modèle."
        )

    return objet


# ==================================================
# EXTRACTION DES NOMS DE VARIABLES
# ==================================================

def extraire_noms_variables(
    pipeline,
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> list[str]:

    preprocesseur = pipeline.named_steps[
        "preprocessing"
    ]

    transformateur_categoriel = (
        preprocesseur
        .named_transformers_["categoriel"]
    )

    encodeur = (
        transformateur_categoriel
        .named_steps["encodage"]
    )

    noms_categorielles = (
        encodeur.get_feature_names_out(
            variables_categorielles
        )
        .tolist()
    )

    noms_numeriques = list(
        variables_numeriques
    )

    return (
        noms_categorielles
        + noms_numeriques
    )


# ==================================================
# EXTRACTION DES IMPORTANCES
# ==================================================

def construire_table_importance(
    objet_modele: dict,
) -> pd.DataFrame:

    pipeline = objet_modele["pipeline"]

    variables_categorielles = objet_modele[
        "variables_categorielles"
    ]

    variables_numeriques = objet_modele[
        "variables_numeriques"
    ]

    modele = pipeline.named_steps[
        "model"
    ]

    if not hasattr(
        modele,
        "feature_importances_",
    ):
        raise AttributeError(
            "Le modèle chargé ne fournit pas feature_importances_."
        )

    noms_variables = extraire_noms_variables(
        pipeline,
        variables_categorielles,
        variables_numeriques,
    )

    importances = modele.feature_importances_

    if len(noms_variables) != len(importances):
        raise ValueError(
            "Le nombre de noms de variables ne correspond pas "
            "au nombre d'importances."
        )

    tableau = pd.DataFrame(
        {
            "variable": noms_variables,
            "importance": importances,
        }
    )

    tableau["importance_pourcentage"] = (
        tableau["importance"] * 100
    )

    tableau = tableau.sort_values(
        by="importance",
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


# ==================================================
# AGREGER PAR VARIABLE D'ORIGINE
# ==================================================

def identifier_variable_origine(
    nom_variable: str,
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> str:

    if nom_variable in variables_numeriques:
        return nom_variable

    for variable in sorted(
        variables_categorielles,
        key=len,
        reverse=True,
    ):
        prefixe = f"{variable}_"

        if nom_variable.startswith(prefixe):
            return variable

    return "autre"


def construire_table_agregee(
    tableau_detaille: pd.DataFrame,
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> pd.DataFrame:

    tableau = tableau_detaille.copy()

    tableau["variable_origine"] = (
        tableau["variable"]
        .apply(
            lambda valeur: identifier_variable_origine(
                valeur,
                variables_categorielles,
                variables_numeriques,
            )
        )
    )

    tableau_agrege = (
        tableau
        .groupby(
            "variable_origine",
            as_index=False,
        )["importance"]
        .sum()
        .sort_values(
            by="importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    tableau_agrege[
        "importance_pourcentage"
    ] = (
        tableau_agrege["importance"] * 100
    )

    tableau_agrege.insert(
        0,
        "rang",
        range(
            1,
            len(tableau_agrege) + 1,
        ),
    )

    return tableau_agrege


# ==================================================
# GRAPHIQUE
# ==================================================

def sauvegarder_graphique(
    tableau: pd.DataFrame,
    top_n: int = TOP_N,
) -> None:

    top = (
        tableau
        .head(top_n)
        .sort_values(
            by="importance",
            ascending=True,
        )
    )

    figure, axe = plt.subplots(
        figsize=(10, 8)
    )

    axe.barh(
        top["variable"],
        top["importance_pourcentage"],
    )

    axe.set_title(
        f"Top {min(top_n, len(top))} des variables les plus importantes"
    )
    axe.set_xlabel(
        "Importance (%)"
    )
    axe.set_ylabel(
        "Variable"
    )

    for index, valeur in enumerate(
        top["importance_pourcentage"]
    ):
        axe.text(
            valeur,
            index,
            f" {valeur:.2f} %",
            va="center",
        )

    figure.tight_layout()

    figure.savefig(
        PNG_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(figure)


# ==================================================
# RAPPORT TEXTE
# ==================================================

def creer_rapport(
    tableau_detaille: pd.DataFrame,
    tableau_agrege: pd.DataFrame,
    objet_modele: dict,
) -> str:

    lignes = []

    lignes.append("=" * 70)
    lignes.append("RAPPORT D'IMPORTANCE DES VARIABLES")
    lignes.append("=" * 70)
    lignes.append("")

    lignes.append(
        f"Modèle analysé : "
        f"{objet_modele.get('nom_modele', 'inconnu')}"
    )

    lignes.append(
        f"Nombre total de variables après encodage : "
        f"{len(tableau_detaille)}"
    )

    lignes.append("")
    lignes.append("TOP 20 DES VARIABLES DETAILLEES")
    lignes.append("-" * 70)

    for _, ligne in tableau_detaille.head(20).iterrows():
        lignes.append(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable']} : "
            f"{ligne['importance_pourcentage']:.4f} %"
        )

    lignes.append("")
    lignes.append("IMPORTANCE AGREGEE PAR VARIABLE D'ORIGINE")
    lignes.append("-" * 70)

    for _, ligne in tableau_agrege.iterrows():
        lignes.append(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable_origine']} : "
            f"{ligne['importance_pourcentage']:.4f} %"
        )

    lignes.append("")
    lignes.append("INTERPRETATION")
    lignes.append("-" * 70)

    lignes.append(
        "Les importances indiquent la contribution relative des "
        "variables aux décisions de la Random Forest."
    )

    lignes.append(
        "Une importance élevée signifie que la variable est souvent "
        "utilisée dans les divisions des arbres."
    )

    lignes.append(
        "Elle ne prouve pas une relation causale entre la variable "
        "et le risque."
    )

    lignes.append(
        "Les variables catégorielles possédant de nombreuses modalités "
        "peuvent obtenir une importance totale élevée après encodage."
    )

    lignes.append("")
    lignes.append("ATTENTION METHODOLOGIQUE")
    lignes.append("-" * 70)

    lignes.append(
        "Le label actuel est dérivé du type d'annonce BODACC."
    )

    lignes.append(
        "Le modèle reste exploratoire et ne constitue pas encore "
        "une véritable prédiction de défaillance future."
    )

    lignes.append(
        "Les résultats doivent être interprétés comme des associations "
        "dans le dataset, et non comme des causes économiques."
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

    objet_modele = charger_modele(
        MODEL_PATH
    )

    tableau_detaille = (
        construire_table_importance(
            objet_modele
        )
    )

    tableau_agrege = (
        construire_table_agregee(
            tableau_detaille,
            objet_modele[
                "variables_categorielles"
            ],
            objet_modele[
                "variables_numeriques"
            ],
        )
    )

    tableau_detaille.to_csv(
        CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    chemin_agrege = (
        REPORTS_DIR
        / "importance_variables_agregee.csv"
    )

    tableau_agrege.to_csv(
        chemin_agrege,
        index=False,
        encoding="utf-8-sig",
    )

    sauvegarder_graphique(
        tableau_detaille
    )

    rapport = creer_rapport(
        tableau_detaille,
        tableau_agrege,
        objet_modele,
    )

    TXT_PATH.write_text(
        rapport,
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("ANALYSE DES IMPORTANCES TERMINEE")
    print("=" * 70)

    print("\nTop 10 variables détaillées :")

    for _, ligne in tableau_detaille.head(10).iterrows():
        print(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable']} "
            f"=> {ligne['importance_pourcentage']:.4f} %"
        )

    print("\nImportance agrégée :")

    for _, ligne in tableau_agrege.iterrows():
        print(
            f"{int(ligne['rang']):>2}. "
            f"{ligne['variable_origine']} "
            f"=> {ligne['importance_pourcentage']:.4f} %"
        )

    print("")
    print(f"CSV détaillé : {CSV_PATH}")
    print(f"CSV agrégé : {chemin_agrege}")
    print(f"Graphique : {PNG_PATH}")
    print(f"Rapport : {TXT_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()