import pandas as pd

# Chargement du dataset
df = pd.read_csv("data/entreprises.csv", encoding="utf-8-sig")

print("=" * 60)
print("ANALYSE DU DATASET BODACC")
print("=" * 60)

print("\nNombre de lignes :", len(df))
print("Nombre de colonnes :", len(df.columns))

print("\nColonnes :")
print(df.columns.tolist())

print("\nValeurs manquantes :")
print(df.isnull().sum())

print("\nRépartition des labels :")
print(df["label_risque"].value_counts())

print("\nRépartition des types d'annonces :")
print(df["type_annonce"].value_counts())

print("\nRépartition des activités :")
print(df["activite_probable"].value_counts())

print("\nTop 10 des greffes :")
print(df["greffe"].value_counts().head(10))

print("\nTop 10 des départements :")
print(df["departement"].value_counts().head(10))

print("\nStatistiques numériques :")
print(df.describe(include="all"))

print("\nAperçu des 5 premières lignes :")
print(df.head())