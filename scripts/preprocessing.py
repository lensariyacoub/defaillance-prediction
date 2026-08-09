# scripts/preprocessing.py

from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
from sklearn.model_selection import train_test_split


# ==================================================
# CONFIGURATION
# ==================================================

INPUT_PATH = Path("data/entreprises.csv")
OUTPUT_DIR = Path("data/processed")

DATASET_MODEL_PATH = OUTPUT_DIR / "dataset_model.csv"
TRAIN_PATH = OUTPUT_DIR / "train.csv"
TEST_PATH = OUTPUT_DIR / "test.csv"
REPORT_PATH = OUTPUT_DIR / "rapport_preprocessing.txt"
METADATA_PATH = OUTPUT_DIR / "metadata.json"

TEST_SIZE = 0.20
RANDOM_STATE = 42

TARGET = "label_risque"

VARIABLES_EXCLUES = [
    "id_annonce",
    "siren",
    "entreprise",
    "type_annonce",
    "score_risque",
    "type_risque",
    "source",
    "date_scraping",
]

VARIABLES_CATEGORIELLES = [
    "departement",
    "greffe",
    "type_entite",
    "activite_probable",
]

VARIABLES_NUMERIQUES = [
    "longueur_nom",
    "nombre_mots_nom",
    "annee_publication",
    "mois_publication",
    "jour_semaine_publication",
]


# ==================================================
# CHARGEMENT
# ==================================================

def charger_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {path.resolve()}"
        )

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={
            "siren": "string",
            "departement": "string",
        },
    )

    return df


# ==================================================
# NETTOYAGE
# ==================================================

def supprimer_lignes_parasites(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "type_annonce" not in df.columns:
        return df

    masque_parasite = (
        df["type_annonce"]
        .astype("string")
        .str.contains(
            (
                "VENTES ET CESSIONS IMMATRICULATIONS "
                "CRÉATIONS PROCÉDURES COLLECTIVES"
            ),
            case=False,
            na=False,
        )
    )

    nombre_parasites = int(masque_parasite.sum())

    if nombre_parasites > 0:
        print(
            f"{nombre_parasites} ligne(s) parasite(s) supprimée(s)."
        )

    return df.loc[~masque_parasite].copy()


def nettoyer_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    colonnes_texte = [
        "departement",
        "greffe",
        "type_entite",
        "activite_probable",
    ]

    for colonne in colonnes_texte:
        if colonne in df.columns:
            df[colonne] = (
                df[colonne]
                .astype("string")
                .str.strip()
                .fillna("INCONNU")
            )

    colonnes_numeriques = [
        "longueur_nom",
        "nombre_mots_nom",
        "label_risque",
    ]

    for colonne in colonnes_numeriques:
        if colonne in df.columns:
            df[colonne] = pd.to_numeric(
                df[colonne],
                errors="coerce",
            )

    return df


# ==================================================
# FEATURE ENGINEERING
# ==================================================

def creer_variables_temporelles(
    df: pd.DataFrame,
) -> pd.DataFrame:
    df = df.copy()

    if "date_publication" not in df.columns:
        raise KeyError(
            "La colonne date_publication est absente."
        )

    date_publication = pd.to_datetime(
        df["date_publication"],
        format="%d/%m/%Y",
        errors="coerce",
    )

    df["annee_publication"] = date_publication.dt.year
    df["mois_publication"] = date_publication.dt.month
    df["jour_semaine_publication"] = (
        date_publication.dt.dayofweek
    )

    return df


# ==================================================
# VALIDATION
# ==================================================

def verifier_colonnes(df: pd.DataFrame) -> None:
    colonnes_requises = (
        VARIABLES_CATEGORIELLES
        + VARIABLES_NUMERIQUES
        + [TARGET]
    )

    colonnes_absentes = [
        colonne
        for colonne in colonnes_requises
        if colonne not in df.columns
    ]

    if colonnes_absentes:
        raise KeyError(
            "Colonnes absentes : "
            + ", ".join(colonnes_absentes)
        )


def nettoyer_valeurs_manquantes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    df = df.copy()

    for colonne in VARIABLES_CATEGORIELLES:
        df[colonne] = (
            df[colonne]
            .astype("string")
            .fillna("INCONNU")
        )

    for colonne in VARIABLES_NUMERIQUES:
        mediane = df[colonne].median()

        if pd.isna(mediane):
            mediane = 0

        df[colonne] = df[colonne].fillna(mediane)

    df = df[df[TARGET].isin([0, 1])].copy()
    df[TARGET] = df[TARGET].astype(int)

    return df


# ==================================================
# PREPARATION
# ==================================================

def preparer_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = supprimer_lignes_parasites(df)
    df = nettoyer_types(df)
    df = creer_variables_temporelles(df)

    verifier_colonnes(df)

    colonnes_modele = (
        VARIABLES_CATEGORIELLES
        + VARIABLES_NUMERIQUES
        + [TARGET]
    )

    dataset_model = df[colonnes_modele].copy()
    dataset_model = nettoyer_valeurs_manquantes(
        dataset_model
    )

    return dataset_model.reset_index(drop=True)


# ==================================================
# SEPARATION TRAIN / TEST
# ==================================================

def separer_train_test(
    dataset_model: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df, test_df = train_test_split(
        dataset_model,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=dataset_model[TARGET],
    )

    return (
        train_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


# ==================================================
# RAPPORT
# ==================================================

def creer_rapport(
    dataset_initial: pd.DataFrame,
    dataset_model: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> str:
    lignes = []

    lignes.append("=" * 60)
    lignes.append("RAPPORT DE PREPROCESSING")
    lignes.append("=" * 60)
    lignes.append("")

    lignes.append(
        f"Lignes du dataset initial : {len(dataset_initial)}"
    )
    lignes.append(
        f"Lignes du dataset modèle : {len(dataset_model)}"
    )
    lignes.append(
        f"Lignes du train : {len(train_df)}"
    )
    lignes.append(
        f"Lignes du test : {len(test_df)}"
    )
    lignes.append("")

    lignes.append("Variables utilisées :")

    for colonne in (
        VARIABLES_CATEGORIELLES
        + VARIABLES_NUMERIQUES
    ):
        lignes.append(f"- {colonne}")

    lignes.append("")
    lignes.append("Variable cible :")
    lignes.append(f"- {TARGET}")
    lignes.append("")

    lignes.append("Variables exclues :")

    for colonne in VARIABLES_EXCLUES:
        lignes.append(f"- {colonne}")

    lignes.append("")
    lignes.append("Répartition du label dans le dataset complet :")

    repartition_complete = (
        dataset_model[TARGET]
        .value_counts()
        .sort_index()
    )

    for label, nombre in repartition_complete.items():
        proportion = nombre / len(dataset_model) * 100
        lignes.append(
            f"- label {label} : "
            f"{nombre} ({proportion:.2f} %)"
        )

    lignes.append("")
    lignes.append("Répartition du label dans le train :")

    repartition_train = (
        train_df[TARGET]
        .value_counts()
        .sort_index()
    )

    for label, nombre in repartition_train.items():
        proportion = nombre / len(train_df) * 100
        lignes.append(
            f"- label {label} : "
            f"{nombre} ({proportion:.2f} %)"
        )

    lignes.append("")
    lignes.append("Répartition du label dans le test :")

    repartition_test = (
        test_df[TARGET]
        .value_counts()
        .sort_index()
    )

    for label, nombre in repartition_test.items():
        proportion = nombre / len(test_df) * 100
        lignes.append(
            f"- label {label} : "
            f"{nombre} ({proportion:.2f} %)"
        )

    lignes.append("")
    lignes.append("ATTENTION")
    lignes.append("-" * 60)
    lignes.append(
        "Le label actuel est construit à partir du type "
        "d'annonce BODACC."
    )
    lignes.append(
        "Le modèle obtenu sera exploratoire et ne constituera "
        "pas encore une véritable prédiction de défaillance future."
    )

    return "\n".join(lignes)


# ==================================================
# EXECUTION
# ==================================================

def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset_initial = charger_dataset(INPUT_PATH)
    dataset_model = preparer_dataset(dataset_initial)

    train_df, test_df = separer_train_test(
        dataset_model
    )

    dataset_model.to_csv(
        DATASET_MODEL_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    train_df.to_csv(
        TRAIN_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    test_df.to_csv(
        TEST_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    rapport = creer_rapport(
        dataset_initial,
        dataset_model,
        train_df,
        test_df,
    )

    REPORT_PATH.write_text(
        rapport,
        encoding="utf-8",
    )

    metadata = {
        "target": TARGET,
        "variables_categorielles": VARIABLES_CATEGORIELLES,
        "variables_numeriques": VARIABLES_NUMERIQUES,
        "variables_exclues": VARIABLES_EXCLUES,
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "nombre_lignes": len(dataset_model),
        "nombre_train": len(train_df),
        "nombre_test": len(test_df),
    }

    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n==============================")
    print("PREPROCESSING TERMINE")
    print("==============================")
    print(
        f"Dataset modèle : {DATASET_MODEL_PATH}"
    )
    print(f"Train : {TRAIN_PATH}")
    print(f"Test : {TEST_PATH}")
    print(f"Rapport : {REPORT_PATH}")
    print(f"Métadonnées : {METADATA_PATH}")
    print("")
    print(
        f"Nombre total : {len(dataset_model)}"
    )
    print(f"Train : {len(train_df)}")
    print(f"Test : {len(test_df)}")
    print("==============================")


if __name__ == "__main__":
    main()