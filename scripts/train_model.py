# scripts/train_model.py

from __future__ import annotations

from pathlib import Path
import json
import time

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    RocCurveDisplay,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ==================================================
# CONFIGURATION
# ==================================================

TRAIN_PATH = Path("data/processed/train.csv")
TEST_PATH = Path("data/processed/test.csv")
METADATA_PATH = Path("data/processed/metadata.json")

MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")

BEST_MODEL_PATH = MODELS_DIR / "meilleur_modele.joblib"
RESULTS_JSON_PATH = REPORTS_DIR / "resultats_modeles.json"
REPORT_TEXT_PATH = REPORTS_DIR / "rapport_modeles.txt"

TARGET = "label_risque"


# ==================================================
# CHARGEMENT
# ==================================================

def charger_donnees() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    if not TRAIN_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {TRAIN_PATH.resolve()}"
        )

    if not TEST_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {TEST_PATH.resolve()}"
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {METADATA_PATH.resolve()}"
        )

    train_df = pd.read_csv(
        TRAIN_PATH,
        encoding="utf-8-sig",
        dtype={
            "departement": "string",
            "greffe": "string",
            "type_entite": "string",
            "activite_probable": "string",
        },
    )

    test_df = pd.read_csv(
        TEST_PATH,
        encoding="utf-8-sig",
        dtype={
            "departement": "string",
            "greffe": "string",
            "type_entite": "string",
            "activite_probable": "string",
        },
    )

    metadata = json.loads(
        METADATA_PATH.read_text(
            encoding="utf-8"
        )
    )

    return train_df, test_df, metadata


# ==================================================
# PREPROCESSING SKLEARN
# ==================================================

def construire_preprocesseur(
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> ColumnTransformer:

    pipeline_categoriel = Pipeline(
        steps=[
            (
                "imputation",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "encodage",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
            ),
        ]
    )

    pipeline_numerique = Pipeline(
        steps=[
            (
                "imputation",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "standardisation",
                StandardScaler(),
            ),
        ]
    )

    preprocesseur = ColumnTransformer(
        transformers=[
            (
                "categoriel",
                pipeline_categoriel,
                variables_categorielles,
            ),
            (
                "numerique",
                pipeline_numerique,
                variables_numeriques,
            ),
        ],
        remainder="drop",
    )

    return preprocesseur


# ==================================================
# MODELES
# ==================================================

def construire_modeles(
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> dict[str, Pipeline]:

    modele_logistique = Pipeline(
        steps=[
            (
                "preprocessing",
                construire_preprocesseur(
                    variables_categorielles,
                    variables_numeriques,
                ),
            ),
            (
                "model",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    modele_random_forest = Pipeline(
        steps=[
            (
                "preprocessing",
                construire_preprocesseur(
                    variables_categorielles,
                    variables_numeriques,
                ),
            ),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=500,
                    max_depth=None,
                    min_samples_split=4,
                    min_samples_leaf=2,
                    class_weight="balanced_subsample",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    return {
        "regression_logistique": modele_logistique,
        "random_forest": modele_random_forest,
    }


# ==================================================
# EVALUATION
# ==================================================

def evaluer_modele(
    nom_modele: str,
    pipeline: Pipeline,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:

    debut = time.perf_counter()

    pipeline.fit(
        X_train,
        y_train,
    )

    duree = time.perf_counter() - debut

    predictions = pipeline.predict(
        X_test
    )

    probabilites = pipeline.predict_proba(
        X_test
    )[:, 1]

    matrice = confusion_matrix(
        y_test,
        predictions,
    )

    resultats = {
        "nom_modele": nom_modele,
        "accuracy": float(
            accuracy_score(
                y_test,
                predictions,
            )
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "f1_score": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_test,
                probabilites,
            )
        ),
        "temps_entrainement_secondes": float(duree),
        "matrice_confusion": matrice.tolist(),
        "rapport_classification": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
    }

    sauvegarder_matrice_confusion(
        nom_modele,
        matrice,
    )

    sauvegarder_courbe_roc(
        nom_modele,
        y_test,
        probabilites,
    )

    return resultats


# ==================================================
# GRAPHIQUES
# ==================================================

def sauvegarder_matrice_confusion(
    nom_modele: str,
    matrice,
) -> None:

    figure, axe = plt.subplots()

    image = axe.imshow(
        matrice,
    )

    figure.colorbar(
        image,
        ax=axe,
    )

    axe.set_title(
        f"Matrice de confusion - {nom_modele}"
    )
    axe.set_xlabel(
        "Classe prédite"
    )
    axe.set_ylabel(
        "Classe réelle"
    )
    axe.set_xticks([0, 1])
    axe.set_yticks([0, 1])

    for ligne in range(matrice.shape[0]):
        for colonne in range(matrice.shape[1]):
            axe.text(
                colonne,
                ligne,
                str(matrice[ligne, colonne]),
                ha="center",
                va="center",
            )

    figure.tight_layout()

    chemin = (
        REPORTS_DIR
        / f"matrice_confusion_{nom_modele}.png"
    )

    figure.savefig(
        chemin,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)


def sauvegarder_courbe_roc(
    nom_modele: str,
    y_test: pd.Series,
    probabilites,
) -> None:

    figure, axe = plt.subplots()

    RocCurveDisplay.from_predictions(
        y_test,
        probabilites,
        ax=axe,
        name=nom_modele,
    )

    axe.set_title(
        f"Courbe ROC - {nom_modele}"
    )

    figure.tight_layout()

    chemin = (
        REPORTS_DIR
        / f"courbe_roc_{nom_modele}.png"
    )

    figure.savefig(
        chemin,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)


# ==================================================
# RAPPORT
# ==================================================

def creer_rapport_texte(
    resultats_modeles: dict[str, dict],
    meilleur_nom: str,
) -> str:

    lignes = []

    lignes.append("=" * 65)
    lignes.append("RAPPORT D'ENTRAINEMENT DES MODELES")
    lignes.append("=" * 65)
    lignes.append("")

    for nom_modele, resultat in resultats_modeles.items():

        lignes.append(
            f"MODELE : {nom_modele}"
        )
        lignes.append("-" * 65)

        lignes.append(
            f"Accuracy : {resultat['accuracy']:.4f}"
        )
        lignes.append(
            f"Precision : {resultat['precision']:.4f}"
        )
        lignes.append(
            f"Recall : {resultat['recall']:.4f}"
        )
        lignes.append(
            f"F1-score : {resultat['f1_score']:.4f}"
        )
        lignes.append(
            f"ROC-AUC : {resultat['roc_auc']:.4f}"
        )
        lignes.append(
            "Temps d'entrainement : "
            f"{resultat['temps_entrainement_secondes']:.3f} s"
        )

        matrice = resultat["matrice_confusion"]

        lignes.append("")
        lignes.append("Matrice de confusion :")
        lignes.append(
            f"TN={matrice[0][0]} | "
            f"FP={matrice[0][1]} | "
            f"FN={matrice[1][0]} | "
            f"TP={matrice[1][1]}"
        )
        lignes.append("")

    lignes.append("=" * 65)
    lignes.append(
        f"MEILLEUR MODELE : {meilleur_nom}"
    )
    lignes.append(
        "Critère de sélection principal : "
        "F1-score sur la classe positive."
    )
    lignes.append("=" * 65)
    lignes.append("")

    lignes.append("ATTENTION METHODOLOGIQUE")
    lignes.append("-" * 65)
    lignes.append(
        "Le label actuel est construit à partir du type "
        "d'annonce BODACC."
    )
    lignes.append(
        "Le modèle est exploratoire et ne constitue pas encore "
        "une véritable prédiction de défaillance future."
    )
    lignes.append(
        "Les résultats ne doivent pas être interprétés comme "
        "une probabilité économique réelle de défaut."
    )

    return "\n".join(lignes)


# ==================================================
# EXECUTION
# ==================================================

def main() -> None:

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_df, test_df, metadata = charger_donnees()

    variables_categorielles = metadata[
        "variables_categorielles"
    ]
    variables_numeriques = metadata[
        "variables_numeriques"
    ]

    X_train = train_df[
        variables_categorielles
        + variables_numeriques
    ].copy()

    y_train = train_df[
        TARGET
    ].astype(int)

    X_test = test_df[
        variables_categorielles
        + variables_numeriques
    ].copy()

    y_test = test_df[
        TARGET
    ].astype(int)

    modeles = construire_modeles(
        variables_categorielles,
        variables_numeriques,
    )

    resultats_modeles = {}
    pipelines_entraines = {}

    for nom_modele, pipeline in modeles.items():

        print("\n" + "=" * 60)
        print(
            f"ENTRAINEMENT : {nom_modele}"
        )
        print("=" * 60)

        resultats = evaluer_modele(
            nom_modele,
            pipeline,
            X_train,
            y_train,
            X_test,
            y_test,
        )

        resultats_modeles[
            nom_modele
        ] = resultats

        pipelines_entraines[
            nom_modele
        ] = pipeline

        print(
            f"Accuracy : {resultats['accuracy']:.4f}"
        )
        print(
            f"Precision : {resultats['precision']:.4f}"
        )
        print(
            f"Recall : {resultats['recall']:.4f}"
        )
        print(
            f"F1-score : {resultats['f1_score']:.4f}"
        )
        print(
            f"ROC-AUC : {resultats['roc_auc']:.4f}"
        )
        print(
            "Matrice de confusion : "
            f"{resultats['matrice_confusion']}"
        )

    meilleur_nom = max(
        resultats_modeles,
        key=lambda nom: (
            resultats_modeles[nom]["f1_score"],
            resultats_modeles[nom]["roc_auc"],
        ),
    )

    meilleur_pipeline = pipelines_entraines[
        meilleur_nom
    ]

    objet_sauvegarde = {
        "pipeline": meilleur_pipeline,
        "nom_modele": meilleur_nom,
        "variables_categorielles": variables_categorielles,
        "variables_numeriques": variables_numeriques,
        "target": TARGET,
        "resultats": resultats_modeles[
            meilleur_nom
        ],
        "avertissement": (
            "Modèle exploratoire. "
            "Le label dépend du type d'annonce BODACC."
        ),
    }

    joblib.dump(
        objet_sauvegarde,
        BEST_MODEL_PATH,
    )

    RESULTS_JSON_PATH.write_text(
        json.dumps(
            resultats_modeles,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    rapport = creer_rapport_texte(
        resultats_modeles,
        meilleur_nom,
    )

    REPORT_TEXT_PATH.write_text(
        rapport,
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("ENTRAINEMENT TERMINE")
    print("=" * 60)
    print(
        f"Meilleur modèle : {meilleur_nom}"
    )
    print(
        "F1-score : "
        f"{resultats_modeles[meilleur_nom]['f1_score']:.4f}"
    )
    print(
        "ROC-AUC : "
        f"{resultats_modeles[meilleur_nom]['roc_auc']:.4f}"
    )
    print(
        f"Modèle sauvegardé : {BEST_MODEL_PATH}"
    )
    print(
        f"Rapport : {REPORT_TEXT_PATH}"
    )
    print(
        f"Résultats JSON : {RESULTS_JSON_PATH}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()


    