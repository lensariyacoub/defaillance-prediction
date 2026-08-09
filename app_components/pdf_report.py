"""
RiskVision AI - Génération du rapport PDF.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from app_components.shap_explainer import (
    expliquer_observation,
)

from app_components.shap_formatter import (
    expliquer_facteur,
    traduire_variable,
)

def generer_rapport_pdf(
    observation,
    resultat: dict,
) -> bytes:
    """
    Génère un rapport PDF pour une analyse RiskVision AI.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="Rapport RiskVision AI",
        author="RiskVision AI",
    )

    styles = getSampleStyleSheet()

    style_titre = ParagraphStyle(
        "TitreRiskVision",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=27,
        textColor=colors.HexColor("#16324F"),
        spaceAfter=8,
    )

    style_sous_titre = ParagraphStyle(
        "SousTitreRiskVision",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=18,
    )

    style_section = ParagraphStyle(
        "SectionRiskVision",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#16324F"),
        spaceBefore=10,
        spaceAfter=8,
    )

    style_normal = ParagraphStyle(
        "NormalRiskVision",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#172033"),
    )

    style_avertissement = ParagraphStyle(
        "AvertissementRiskVision",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#92400E"),
        backColor=colors.HexColor("#FFF7ED"),
        borderColor=colors.HexColor("#FED7AA"),
        borderWidth=1,
        borderPadding=8,
        spaceBefore=12,
    )

    contenu = []

    contenu.append(
        Paragraph(
            "RiskVision AI",
            style_titre,
        )
    )

    contenu.append(
        Paragraph(
            "Rapport d'analyse exploratoire du risque",
            style_sous_titre,
        )
    )

    contenu.append(
        Paragraph(
            "Informations sur l'entreprise",
            style_section,
        )
    )

    informations = [
        ["Entreprise", observation.nom_entreprise],
        ["Département", observation.departement],
        ["Greffe", observation.greffe],
        ["Type d'entité", observation.type_entite],
        ["Activité probable", observation.activite_probable],
        [
            "Date du rapport",
            datetime.now().strftime("%d/%m/%Y %H:%M"),
        ],
    ]

    table_informations = Table(
        informations,
        colWidths=[
            5 * cm,
            11 * cm,
        ],
    )

    table_informations.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F1F5F9"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#16324F"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    contenu.append(
        table_informations
    )

    contenu.append(
        Spacer(
            1,
            14,
        )
    )

    contenu.append(
        Paragraph(
            "Résultat du modèle",
            style_section,
        )
    )

    probabilite_risque = (
        resultat["probabilite_risque"]
        * 100
    )

    probabilite_non_risque = (
        resultat["probabilite_non_risque"]
        * 100
    )

    resultats = [
        [
            "Décision",
            resultat["decision"],
        ],
        [
            "Probabilité de risque",
            f"{probabilite_risque:.2f} %",
        ],
        [
            "Probabilité de non-risque",
            f"{probabilite_non_risque:.2f} %",
        ],
        [
            "Classe prédite",
            str(
                resultat["classe_predite"]
            ),
        ],
    ]

    table_resultats = Table(
        resultats,
        colWidths=[
            7 * cm,
            9 * cm,
        ],
    )

    table_resultats.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#EFF6FF"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#16324F"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    contenu.append(
        table_resultats
    )

    contenu.append(
        Paragraph(
            "Synthèse",
            style_section,
        )
    )

    texte_resume = (
        f"L'entreprise <b>{observation.nom_entreprise}</b>, "
        f"rattachée au greffe de <b>{observation.greffe}</b> "
        f"et identifiée dans l'activité "
        f"<b>{observation.activite_probable}</b>, "
        f"est classée <b>{resultat['decision']}</b> "
        f"par le modèle Random Forest. "
        f"La probabilité de risque calculée est de "
        f"<b>{probabilite_risque:.2f} %</b>."
    )

    contenu.append(
        Paragraph(
            texte_resume,
            style_normal,
        )
    )

    contenu.append(
        Paragraph(
            "Facteurs ayant influencé la décision",
            style_section,
        )
    )

    try:
        resultat_shap = expliquer_observation(
            observation.dataframe
        )

        top_facteurs = (
            resultat_shap["tableau"]
            .head(5)
        )

        for _, ligne in top_facteurs.iterrows():

            nom_variable = str(
                ligne["variable"]
            )

            contribution = float(
                ligne["contribution_shap"]
            )

            valeur_transformee = float(
                ligne["valeur_transformee"]
            )

            variable_lisible = traduire_variable(
                nom_variable
            )

            explication_facteur = expliquer_facteur(
                nom_variable=nom_variable,
                contribution=contribution,
                valeur_transformee=valeur_transformee,
            )

            contenu.append(
                Paragraph(
                    f"<b>{variable_lisible}</b>",
                    style_normal,
                )
            )

            contenu.append(
                Paragraph(
                    explication_facteur,
                    style_normal,
                )
            )

            contenu.append(
                Spacer(
                    1,
                    6,
                )
            )

    except Exception as erreur:

        contenu.append(
            Paragraph(
                (
                    "L'explication SHAP n'a pas pu être "
                    f"générée dans le rapport : {erreur}"
                ),
                style_normal,
            )
        )

    contenu.append(
        Paragraph(
            (
                "Important : ce rapport correspond à une analyse "
                "exploratoire produite par un modèle de Machine Learning. "
                "Il ne constitue ni une notation financière officielle, "
                "ni un diagnostic juridique, comptable ou bancaire."
            ),
            style_avertissement,
        )
    )

    document.build(
        contenu
    )

    buffer.seek(0)

    return buffer.getvalue()