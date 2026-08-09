# scripts/webscraping.py

from __future__ import annotations

import csv
import hashlib
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


print("VERSION SCRAPER BODACC V8.2 - PAGINATION PAR CLIC + CONTROLE")


# ==================================================
# CONFIGURATION
# ==================================================

URL_BODACC = (
    "https://www.bodacc.fr/pages/annonces-commerciales-recherche/"
    "?disjunctive.typeavis"
    "&disjunctive.familleavis"
    "&disjunctive.publicationavis"
    "&disjunctive.region_min"
    "&disjunctive.nom_dep_min"
    "&disjunctive.numerodepartement"
    "&sort=dateparution"
    "&refine.familleavis=vente"
    "&refine.familleavis=immatriculation"
    "&refine.familleavis=creation"
    "&refine.familleavis=collective"
    "&refine.familleavis=conciliation"
    "&refine.familleavis=retablissement_professionnel"
    "&refine.familleavis=modification"
    "&refine.familleavis=radiation"
    "&refine.familleavis=dpc"
    "&refine.familleavis=divers"
    "&start=0"
)

RESULTATS_PAR_PAGE = 10
ATTENTE_PAGE_MS = 5000
MAX_TENTATIVES_PAGE = 3

COLONNES_CSV = [
    "id_annonce",
    "type_annonce",
    "entreprise",
    "siren",
    "greffe",
    "departement",
    "date_publication",
    "date_scraping",
    "type_entite",
    "longueur_nom",
    "nombre_mots_nom",
    "activite_probable",
    "label_risque",
    "score_risque",
    "type_risque",
    "source",
]

TYPES_ANNONCES = [
    "JUGEMENT D'OUVERTURE",
    "JUGEMENT DE CLÔTURE",
    "LIQUIDATION JUDICIAIRE",
    "REDRESSEMENT JUDICIAIRE",
    "PROCÉDURE COLLECTIVE",
    "RADIATIONS",
    "CRÉATIONS",
    "CRÉATIONS D'ÉTABLISSEMENTS",
    "IMMATRICULATIONS",
    "MODIFICATIONS",
    "MODIFICATIONS ET MUTATIONS DIVERSES",
    "VENTES ET CESSIONS",
    "AVIS DE DÉPÔT",
    "DÉPÔTS DES COMPTES",
    "DÉPÔTS DES COMPTES DES SOCIÉTÉS",
    "PROCÉDURE DE CONCILIATION",
    "RÉTABLISSEMENT PROFESSIONNEL",
    "ANNONCES DIVERSES",
]


# ==================================================
# OUTILS
# ==================================================

def nettoyer_texte(texte: str) -> str:
    return re.sub(r"\s+", " ", texte or "").strip()


def normaliser_type_annonce(texte: str) -> str:
    return nettoyer_texte(texte).upper()


def est_titre_annonce(ligne: str) -> bool:
    ligne_normalisee = normaliser_type_annonce(ligne)
    return any(
        ligne_normalisee == titre
        or ligne_normalisee.startswith(titre + " ")
        for titre in TYPES_ANNONCES
    )


def construire_url_page(start: int) -> str:
    morceaux = urlsplit(URL_BODACC)
    params = parse_qsl(morceaux.query, keep_blank_values=True)

    nouveaux_params = []
    start_remplace = False

    for cle, valeur in params:
        if cle == "start":
            nouveaux_params.append(("start", str(start)))
            start_remplace = True
        else:
            nouveaux_params.append((cle, valeur))

    if not start_remplace:
        nouveaux_params.append(("start", str(start)))

    return urlunsplit(
        (
            morceaux.scheme,
            morceaux.netloc,
            morceaux.path,
            urlencode(nouveaux_params, doseq=True),
            morceaux.fragment,
        )
    )


def nettoyer_nom(nom: str) -> str:
    nom = nettoyer_texte(nom)
    nom = re.sub(r"\bANNONCE\b.*$", "", nom, flags=re.IGNORECASE)
    return nettoyer_texte(nom)


def nettoyer_greffe(greffe: str) -> str:
    greffe = re.sub(r"\bANNONCE\b.*$", "", greffe, flags=re.IGNORECASE)
    greffe = re.sub(r"\bDÉPOSÉE?\b.*$", "", greffe, flags=re.IGNORECASE)
    greffe = re.sub(r"\bDÉPARTEMENT\b.*$", "", greffe, flags=re.IGNORECASE)
    greffe = re.sub(r"\bVOIR\b.*$", "", greffe, flags=re.IGNORECASE)
    return nettoyer_texte(greffe)


# ==================================================
# DETECTION ACTIVITE
# ==================================================

def detecter_activite(nom: str) -> str:
    texte = nom.lower()

    categories = {
        "FINANCE": [
            "capital", "finance", "holding", "invest", "credit",
            "crédit", "mutuel", "banque", "assurance",
        ],
        "IMMOBILIER": [
            "immobilier", "immo", "sci", "foncier", "habitat",
        ],
        "AUTOMOBILE": [
            "auto", "garage", "moto", "scoot", "automobile",
            "véhicule", "car service",
        ],
        "RESTAURATION": [
            "restaurant", "bistrot", "brasserie", "pizza", "food",
            "café", "bar", "traiteur", "boulangerie", "patisserie",
            "pâtisserie", "fournil", "snack", "burger",
        ],
        "BATIMENT": [
            "btp", "construction", "bâtiment", "batiment", "rénovation",
            "facades", "façades", "toiture", "menuiserie", "bois",
            "maçonnerie", "plomberie", "peinture",
        ],
        "CONSEIL": [
            "consulting", "conseil", "expertise", "audit",
        ],
        "INFORMATIQUE": [
            "informatique", "digital", "software", "web", "data",
            "tech", "telecom", "télécom", "cloud",
        ],
        "SANTE": [
            "medical", "médical", "clinique", "pharma", "dent",
            "optique", "santé", "sante", "orl",
        ],
        "TRANSPORT": [
            "transport", "livraison", "logistique", "messagerie",
        ],
        "AGRICULTURE": [
            "agricole", "agriculture", "scea", "gaec", "earl",
            "élevage", "elevage",
        ],
        "INDUSTRIE": [
            "industrie", "industriel", "manufacture", "fabrication",
            "coopérative industrielle", "cooperative industrielle",
        ],
        "COMMERCE": [
            "commerce", "boutique", "shop", "distribution", "diffusion",
            "négoce", "negoce",
        ],
    }

    for categorie, mots in categories.items():
        if any(mot in texte for mot in mots):
            return categorie

    return "AUTRE"


# ==================================================
# EXTRACTIONS
# ==================================================

def extraire_nom(details: str) -> Tuple[str, str]:
    patterns = [
        (
            r"DÉNOMINATION SOCIALE\s*:\s*(.*?)(?=\s+N°\s*RCS\b|$)",
            "ENTREPRISE",
        ),
        (
            r"NOM,\s*PRÉNOM\s*:\s*(.*?)(?=\s+N°\s*RCS\b|\s+N°\s*RM\b|$)",
            "PERSONNE_PHYSIQUE",
        ),
    ]

    for pattern, type_entite in patterns:
        resultat = re.search(pattern, details, flags=re.IGNORECASE)
        if resultat:
            return nettoyer_nom(resultat.group(1)), type_entite

    return "", "INCONNU"


def extraire_siren(details: str) -> str:
    resultat = re.search(
        r"N°\s*RCS\s*:\s*(\d{3}\s?\d{3}\s?\d{3})",
        details,
        flags=re.IGNORECASE,
    )
    if not resultat:
        return ""

    siren = re.sub(r"\D", "", resultat.group(1))
    return siren if len(siren) == 9 else ""


def extraire_greffe(details: str) -> str:
    resultat = re.search(
        r"N°\s*RCS\s*:\s*\d{3}\s?\d{3}\s?\d{3}\s+RCS\s+"
        r"(.+?)(?=\s+N°\s*RM\b|\s+ANNONCE\b|\s+DÉPARTEMENT\b|\s+Voir\b|$)",
        details,
        flags=re.IGNORECASE,
    )
    return nettoyer_greffe(resultat.group(1)) if resultat else ""


def extraire_departement(details: str) -> str:
    resultat = re.search(
        r"DÉPARTEMENT\s*:\s*([0-9]{2,3}|2A|2B)",
        details,
        flags=re.IGNORECASE,
    )
    if resultat:
        return resultat.group(1).upper()

    resultat_rm = re.search(r"\bRM\s+(2A|2B|\d{2,3})\b", details, flags=re.IGNORECASE)
    return resultat_rm.group(1).upper() if resultat_rm else ""


def extraire_date(details: str) -> str:
    resultat = re.search(
        r"Publié le\s*(\d{2}/\d{2}/\d{4})",
        details,
        flags=re.IGNORECASE,
    )
    return resultat.group(1) if resultat else ""


# ==================================================
# RISQUE
# ==================================================

def calculer_score_risque(titre: str) -> Tuple[int, str]:
    titre_normalise = normaliser_type_annonce(titre)

    regles = [
        ("LIQUIDATION JUDICIAIRE", 100, "LIQUIDATION_JUDICIAIRE"),
        ("JUGEMENT D'OUVERTURE", 90, "OUVERTURE_PROCEDURE"),
        ("REDRESSEMENT JUDICIAIRE", 80, "REDRESSEMENT_JUDICIAIRE"),
        ("PROCÉDURE COLLECTIVE", 80, "PROCEDURE_COLLECTIVE"),
        ("JUGEMENT DE CLÔTURE", 70, "CLOTURE_PROCEDURE"),
        ("RÉTABLISSEMENT PROFESSIONNEL", 70, "RETABLISSEMENT_PROFESSIONNEL"),
        ("RADIATIONS", 50, "RADIATION"),
        ("MODIFICATIONS", 20, "MODIFICATION"),
        ("AVIS DE DÉPÔT", 15, "AVIS_DEPOT"),
        ("DÉPÔTS DES COMPTES", 10, "DEPOT_COMPTES"),
        ("CRÉATIONS", 5, "CREATION"),
        ("IMMATRICULATIONS", 5, "IMMATRICULATION"),
    ]

    for mot, score, type_risque in regles:
        if mot in titre_normalise:
            return score, type_risque

    return 0, "AUCUN"


# ==================================================
# DECOUPAGE DES ANNONCES
# ==================================================

def decouper_annonces(lignes: List[str]) -> List[Tuple[str, str]]:
    positions = [
        index
        for index, ligne in enumerate(lignes)
        if est_titre_annonce(ligne)
    ]

    blocs: List[Tuple[str, str]] = []

    for position_index, debut in enumerate(positions):
        fin = positions[position_index + 1] if position_index + 1 < len(positions) else len(lignes)
        titre = lignes[debut]
        contenu = lignes[debut:fin]

        # On coupe avant le pied de page si nécessaire.
        for marqueur in (
            "Aide et contact",
            "Conditions générales d'utilisation",
            "Sites de la DILA",
        ):
            if marqueur in contenu:
                contenu = contenu[:contenu.index(marqueur)]

        details = nettoyer_texte(" ".join(contenu))

        # Un vrai bloc doit contenir au minimum un numéro RCS.
        if re.search(r"N°\s*RCS\s*:", details, flags=re.IGNORECASE):
            blocs.append((titre, details))

    return blocs


# ==================================================
# CONSTRUCTION D'UNE LIGNE
# ==================================================

def construire_annonce(titre: str, details: str) -> Dict[str, object]:
    entreprise, type_entite = extraire_nom(details)
    siren = extraire_siren(details)
    greffe = extraire_greffe(details)
    departement = extraire_departement(details)
    date_publication = extraire_date(details)
    score_risque, type_risque = calculer_score_risque(titre)

    identifiant_source = "|".join(
        [siren, normaliser_type_annonce(titre), entreprise, date_publication]
    )
    id_annonce = hashlib.sha256(
        identifiant_source.encode("utf-8")
    ).hexdigest()

    return {
        "id_annonce": id_annonce,
        "type_annonce": normaliser_type_annonce(titre),
        "entreprise": entreprise,
        "siren": siren,
        "greffe": greffe,
        "departement": departement,
        "date_publication": date_publication,
        "date_scraping": datetime.now().strftime("%d/%m/%Y"),
        "type_entite": type_entite,
        "longueur_nom": len(entreprise),
        "nombre_mots_nom": len(entreprise.split()),
        "activite_probable": detecter_activite(entreprise),
        "label_risque": 1 if score_risque >= 50 else 0,
        "score_risque": score_risque,
        "type_risque": type_risque,
        "source": "BODACC",
    }


# ==================================================
# SAUVEGARDE
# ==================================================

def sauvegarder_csv(annonces: List[Dict[str, object]], output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    chemin_final = output_path

    try:
        fichier = open(
            chemin_final,
            "w",
            newline="",
            encoding="utf-8-sig",
        )
    except PermissionError:
        base, extension = os.path.splitext(output_path)
        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
        chemin_final = f"{base}_{horodatage}{extension or '.csv'}"
        print(f"Fichier principal verrouillé. Sauvegarde dans : {chemin_final}")
        fichier = open(
            chemin_final,
            "w",
            newline="",
            encoding="utf-8-sig",
        )

    with fichier:
        writer = csv.DictWriter(fichier, fieldnames=COLONNES_CSV)
        writer.writeheader()
        writer.writerows(annonces)

    return chemin_final


# ==================================================
# PAGINATION DU SITE
# ==================================================

def empreinte_page(texte: str) -> Tuple[str, ...]:
    """
    Construit une empreinte avec les premiers SIREN visibles.
    Elle permet de vérifier que la page a réellement changé.
    """
    sirens = re.findall(
        r"N°\s*RCS\s*:\s*(\d{3}\s?\d{3}\s?\d{3})",
        texte,
        flags=re.IGNORECASE,
    )
    return tuple(
        re.sub(r"\D", "", siren)
        for siren in sirens[:5]
    )


def trouver_lien_page_suivante(
    page: Page,
    start_actuel: int,
):
    """
    Retourne le locator du plus petit start supérieur au start actuel,
    ainsi que la valeur de ce prochain start.

    Important : le lien sera cliqué dans la page. On ne navigue pas
    directement vers son href, car BODACC conserve une partie de l'état
    de recherche dans JavaScript.
    """
    liens = page.locator("a[href]")
    candidats = []

    for index in range(liens.count()):
        lien = liens.nth(index)
        href = lien.get_attribute("href")

        if not href:
            continue

        correspondance = re.search(
            r"([?&])start=(\d+)",
            href,
        )

        if not correspondance:
            continue

        start_candidat = int(correspondance.group(2))

        if start_candidat > start_actuel:
            candidats.append(
                (start_candidat, index)
            )

    if not candidats:
        return None, None

    candidats.sort(key=lambda element: element[0])
    prochain_start, index_lien = candidats[0]

    return liens.nth(index_lien), prochain_start


def cliquer_page_suivante(
    page: Page,
    start_actuel: int,
    empreinte_actuelle: Tuple[str, ...],
) -> Tuple[bool, int, str]:
    """
    Clique réellement sur le lien de pagination et attend que les
    premiers SIREN changent.
    """
    lien, prochain_start = trouver_lien_page_suivante(
        page,
        start_actuel,
    )

    if lien is None or prochain_start is None:
        return False, start_actuel, ""

    print(
        f"Clic sur la pagination BODACC : "
        f"start={prochain_start}"
    )

    try:
        lien.scroll_into_view_if_needed()
        lien.click(force=True, timeout=15000)
    except Exception as erreur:
        print(
            f"Échec du clic sur la page suivante : {erreur}"
        )
        return False, start_actuel, ""

    # BODACC peut conserver une URL peu informative. On contrôle donc
    # le contenu réellement affiché plutôt que l'URL seule.
    for tentative in range(1, 11):
        page.wait_for_timeout(1500)

        try:
            texte = page.locator("body").inner_text(
                timeout=30000
            )
        except PlaywrightTimeoutError:
            continue

        nouvelle_empreinte = empreinte_page(texte)

        print(
            f"Contrôle pagination {tentative}/10 : "
            f"{nouvelle_empreinte}"
        )

        if (
            nouvelle_empreinte
            and nouvelle_empreinte != empreinte_actuelle
            and "N° RCS" in texte
            and "Publié le" in texte
        ):
            print(
                "Page réellement modifiée. "
                f"URL actuelle : {page.url}"
            )
            return True, prochain_start, texte

    print(
        "Le clic n'a pas modifié les annonces affichées."
    )
    return False, start_actuel, ""


# ==================================================
# CHARGEMENT D'UNE PAGE
# ==================================================

def charger_premiere_page(page: Page) -> str:
    url_page = construire_url_page(0)

    for tentative in range(1, MAX_TENTATIVES_PAGE + 1):
        try:
            page.goto(
                url_page,
                wait_until="domcontentloaded",
                timeout=60000,
            )
            page.wait_for_timeout(ATTENTE_PAGE_MS)

            texte = page.locator("body").inner_text(
                timeout=30000
            )

            print(f"URL initiale obtenue : {page.url}")

            if "N° RCS" in texte and "Publié le" in texte:
                return texte

            print(
                "Première page chargée sans annonces "
                f"(tentative {tentative}/"
                f"{MAX_TENTATIVES_PAGE})."
            )

        except PlaywrightTimeoutError:
            print(
                "Timeout sur la première page "
                f"(tentative {tentative}/"
                f"{MAX_TENTATIVES_PAGE})."
            )

        if tentative < MAX_TENTATIVES_PAGE:
            time.sleep(2)

    return ""


# ==================================================
# SCRAPER PRINCIPAL
# ==================================================

def scrape_bodacc(
    limit: int = 1000,
    output_path: str = "data/entreprises.csv",
    headless: bool = False,
) -> None:
    if limit <= 0:
        raise ValueError("limit doit être supérieur à 0.")

    annonces: List[Dict[str, object]] = []
    ids_connus = set()
    numero_page = 1
    start_actuel = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            locale="fr-FR",
        )
        page = context.new_page()

        try:
            texte_courant = charger_premiere_page(page)

            if not texte_courant:
                print(
                    "Impossible de charger la première page "
                    "de résultats."
                )
                return

            while len(annonces) < limit:
                print(
                    f"\nPage {numero_page} | "
                    f"{len(annonces)}/{limit} "
                    f"annonces collectées"
                )

                empreinte_courante = empreinte_page(
                    texte_courant
                )
                print(
                    "Empreinte SIREN de la page :",
                    empreinte_courante,
                )

                lignes = [
                    nettoyer_texte(ligne)
                    for ligne in texte_courant.splitlines()
                    if nettoyer_texte(ligne)
                ]
                blocs = decouper_annonces(lignes)

                print(
                    f"{len(blocs)} bloc(s) brut(s) détecté(s)."
                )

                nouvelles_annonces = 0

                for titre, details in blocs:
                    annonce = construire_annonce(
                        titre,
                        details,
                    )

                    if (
                        not annonce["entreprise"]
                        or not annonce["siren"]
                    ):
                        continue

                    id_annonce = annonce["id_annonce"]

                    if id_annonce in ids_connus:
                        continue

                    ids_connus.add(id_annonce)
                    annonces.append(annonce)
                    nouvelles_annonces += 1

                    if len(annonces) >= limit:
                        break

                print(
                    f"{nouvelles_annonces} nouvelle(s) "
                    f"annonce(s) ajoutée(s)."
                )

                if len(annonces) >= limit:
                    break

                succes, prochain_start, nouveau_texte = (
                    cliquer_page_suivante(
                        page,
                        start_actuel,
                        empreinte_courante,
                    )
                )

                if not succes:
                    print(
                        "Arrêt : impossible de confirmer "
                        "le passage à la page suivante."
                    )
                    break

                start_actuel = prochain_start
                texte_courant = nouveau_texte
                numero_page += 1

            if not annonces:
                print("Aucune annonce exploitable trouvée.")
                return

            annonces.sort(
                key=lambda annonce: (
                    annonce["date_publication"],
                    annonce["score_risque"],
                ),
                reverse=True,
            )

            chemin_final = sauvegarder_csv(
                annonces,
                output_path,
            )

            nombre_risque = sum(
                int(annonce["label_risque"])
                for annonce in annonces
            )

            print("\n==================================")
            print(f"{len(annonces)} annonces sauvegardées")
            print(
                f"{nombre_risque} annonces "
                f"avec label_risque = 1"
            )
            print(f"Fichier : {chemin_final}")
            print("Top 5 risques :")

            for annonce in sorted(
                annonces,
                key=lambda item: int(
                    item["score_risque"]
                ),
                reverse=True,
            )[:5]:
                print(
                    f"- {annonce['entreprise']} "
                    f"=> {annonce['score_risque']} "
                    f"({annonce['type_risque']})"
                )

            print("==================================")

        finally:
            context.close()
            browser.close()


# ==================================================
# EXECUTION
# ==================================================

if __name__ == "__main__":
    scrape_bodacc(
        limit=1000,
        output_path="data/entreprises.csv",
        headless=False,
    )