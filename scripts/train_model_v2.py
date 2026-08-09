# scripts/train_model_v2.py

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
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TRAIN_PATH = Path("data/processed/train.csv")
TEST_PATH = Path("data/processed/test.csv")
METADATA_PATH = Path("data/processed/metadata.json")

MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")

MODEL_PATH = MODELS_DIR / "meilleur_modele_v2.joblib"
REPORT_PATH = REPORTS_DIR / "rapport_modele_v2.txt"
RESULTS_PATH = REPORTS_DIR / "resultats_gridsearch_v2.json"
GRID_CSV_PATH = REPORTS_DIR / "gridsearch_resultats_v2.csv"
CONFUSION_PATH = REPORTS_DIR / "matrice_confusion_v2.png"
ROC_PATH = REPORTS_DIR / "courbe_roc_v2.png"

TARGET = "label_risque"
RANDOM_STATE = 42
N_SPLITS = 5


def charger_donnees() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    for path in (TRAIN_PATH, TEST_PATH, METADATA_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {path.resolve()}")

    dtypes = {
        "departement": "string",
        "greffe": "string",
        "type_entite": "string",
        "activite_probable": "string",
    }

    train_df = pd.read_csv(TRAIN_PATH, encoding="utf-8-sig", dtype=dtypes)
    test_df = pd.read_csv(TEST_PATH, encoding="utf-8-sig", dtype=dtypes)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    return train_df, test_df, metadata


def construire_preprocesseur(
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> ColumnTransformer:
    pipeline_categoriel = Pipeline(
        steps=[
            ("imputation", SimpleImputer(strategy="most_frequent")),
            (
                "encodage",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
            ),
        ]
    )

    pipeline_numerique = Pipeline(
        steps=[
            ("imputation", SimpleImputer(strategy="median")),
            ("standardisation", StandardScaler()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("categoriel", pipeline_categoriel, variables_categorielles),
            ("numerique", pipeline_numerique, variables_numeriques),
        ],
        remainder="drop",
    )


def construire_pipeline(
    variables_categorielles: list[str],
    variables_numeriques: list[str],
) -> Pipeline:
    return Pipeline(
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
                    class_weight="balanced_subsample",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def obtenir_grille_parametres() -> dict:
    return {
        "model__n_estimators": [200, 500, 800],
        "model__max_depth": [10, 20, None],
        "model__min_samples_split": [2, 5],
        "model__min_samples_leaf": [1, 2, 4],
        "model__max_features": ["sqrt", "log2"],
    }


def evaluer_modele(
    meilleur_modele: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    predictions = meilleur_modele.predict(X_test)
    probabilites = meilleur_modele.predict_proba(X_test)[:, 1]
    matrice = confusion_matrix(y_test, predictions)

    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilites)),
        "matrice_confusion": matrice.tolist(),
        "rapport_classification": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
    }


def sauvegarder_matrice_confusion(matrice) -> None:
    figure, axe = plt.subplots()
    image = axe.imshow(matrice)
    figure.colorbar(image, ax=axe)

    axe.set_title("Matrice de confusion - Random Forest V2")
    axe.set_xlabel("Classe prédite")
    axe.set_ylabel("Classe réelle")
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
    figure.savefig(CONFUSION_PATH, dpi=160, bbox_inches="tight")
    plt.close(figure)


def sauvegarder_courbe_roc(y_test: pd.Series, probabilites) -> None:
    figure, axe = plt.subplots()
    RocCurveDisplay.from_predictions(
        y_test,
        probabilites,
        ax=axe,
        name="Random Forest V2",
    )
    axe.set_title("Courbe ROC - Random Forest V2")
    figure.tight_layout()
    figure.savefig(ROC_PATH, dpi=160, bbox_inches="tight")
    plt.close(figure)


def creer_rapport(
    resultats: dict,
    meilleurs_parametres: dict,
    meilleur_score_cv: float,
    temps_total: float,
) -> str:
    matrice = resultats["matrice_confusion"]

    lignes = [
        "=" * 65,
        "RAPPORT RANDOM FOREST V2 - GRIDSEARCHCV",
        "=" * 65,
        "",
        f"Meilleur F1 moyen en validation croisée : {meilleur_score_cv:.4f}",
        "",
        "Meilleurs hyperparamètres :",
    ]

    for nom, valeur in meilleurs_parametres.items():
        lignes.append(f"- {nom} : {valeur}")

    lignes.extend(
        [
            "",
            "Résultats sur le jeu de test :",
            f"- Accuracy : {resultats['accuracy']:.4f}",
            f"- Precision : {resultats['precision']:.4f}",
            f"- Recall : {resultats['recall']:.4f}",
            f"- F1-score : {resultats['f1_score']:.4f}",
            f"- ROC-AUC : {resultats['roc_auc']:.4f}",
            "",
            "Matrice de confusion :",
            (
                f"- TN={matrice[0][0]} | FP={matrice[0][1]} | "
                f"FN={matrice[1][0]} | TP={matrice[1][1]}"
            ),
            "",
            f"Temps total GridSearchCV : {temps_total:.2f} secondes",
            "",
            "ATTENTION METHODOLOGIQUE",
            "-" * 65,
            "Le label actuel est construit à partir du type d'annonce BODACC.",
            (
                "Ce modèle reste exploratoire et ne représente pas encore "
                "une véritable prédiction de défaillance future."
            ),
        ]
    )

    return "\n".join(lignes)


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, metadata = charger_donnees()

    variables_categorielles = metadata["variables_categorielles"]
    variables_numeriques = metadata["variables_numeriques"]
    variables_modele = variables_categorielles + variables_numeriques

    X_train = train_df[variables_modele].copy()
    y_train = train_df[TARGET].astype(int)
    X_test = test_df[variables_modele].copy()
    y_test = test_df[TARGET].astype(int)

    pipeline = construire_pipeline(
        variables_categorielles,
        variables_numeriques,
    )
    grille = obtenir_grille_parametres()

    validation_croisee = StratifiedKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=grille,
        scoring="f1",
        cv=validation_croisee,
        n_jobs=-1,
        verbose=2,
        return_train_score=True,
        refit=True,
    )

    nombre_combinaisons = 1
    for valeurs in grille.values():
        nombre_combinaisons *= len(valeurs)

    print("=" * 65)
    print("ENTRAINEMENT RANDOM FOREST V2")
    print("=" * 65)
    print(f"Combinaisons testées : {nombre_combinaisons}")
    print(f"Validation croisée : {N_SPLITS} plis")
    print(
        f"Nombre total d'entraînements : {nombre_combinaisons * N_SPLITS}"
    )
    print("=" * 65)

    debut = time.perf_counter()
    grid_search.fit(X_train, y_train)
    temps_total = time.perf_counter() - debut

    meilleur_modele = grid_search.best_estimator_
    resultats = evaluer_modele(meilleur_modele, X_test, y_test)

    predictions = meilleur_modele.predict(X_test)
    probabilites = meilleur_modele.predict_proba(X_test)[:, 1]
    matrice = confusion_matrix(y_test, predictions)

    sauvegarder_matrice_confusion(matrice)
    sauvegarder_courbe_roc(y_test, probabilites)

    joblib.dump(
        {
            "pipeline": meilleur_modele,
            "nom_modele": "random_forest_v2",
            "meilleurs_parametres": grid_search.best_params_,
            "meilleur_score_cv": float(grid_search.best_score_),
            "variables_categorielles": variables_categorielles,
            "variables_numeriques": variables_numeriques,
            "target": TARGET,
            "resultats_test": resultats,
            "avertissement": (
                "Modèle exploratoire fondé sur un label dérivé "
                "du type d'annonce BODACC."
            ),
        },
        MODEL_PATH,
    )

    pd.DataFrame(grid_search.cv_results_).to_csv(
        GRID_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    RESULTS_PATH.write_text(
        json.dumps(
            {
                "meilleurs_parametres": grid_search.best_params_,
                "meilleur_score_cv": float(grid_search.best_score_),
                "resultats_test": resultats,
                "temps_total_secondes": float(temps_total),
                "nombre_combinaisons": nombre_combinaisons,
                "nombre_plis": N_SPLITS,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    REPORT_PATH.write_text(
        creer_rapport(
            resultats,
            grid_search.best_params_,
            float(grid_search.best_score_),
            temps_total,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 65)
    print("GRIDSEARCHCV TERMINE")
    print("=" * 65)
    print(f"Meilleur F1 CV : {grid_search.best_score_:.4f}")
    print("Meilleurs paramètres :")
    for nom, valeur in grid_search.best_params_.items():
        print(f"- {nom} : {valeur}")

    print("\nRésultats sur le test :")
    print(f"Accuracy : {resultats['accuracy']:.4f}")
    print(f"Precision : {resultats['precision']:.4f}")
    print(f"Recall : {resultats['recall']:.4f}")
    print(f"F1-score : {resultats['f1_score']:.4f}")
    print(f"ROC-AUC : {resultats['roc_auc']:.4f}")
    print(f"Matrice de confusion : {resultats['matrice_confusion']}")
    print(f"\nModèle sauvegardé : {MODEL_PATH}")
    print(f"Rapport : {REPORT_PATH}")
    print(f"Résultats JSON : {RESULTS_PATH}")
    print(f"Résultats complets : {GRID_CSV_PATH}")
    print("=" * 65)


if __name__ == "__main__":
    main()