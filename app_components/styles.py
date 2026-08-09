"""
RiskVision AI - Styles globaux Streamlit.

Ce module centralise le CSS de l'application.
Il ne contient aucune logique métier ni Machine Learning.
"""

from __future__ import annotations

import streamlit as st

from app_components.theme import (
    BACKGROUND_COLOR,
    BUTTON_RADIUS,
    CARD_COLOR,
    CARD_RADIUS,
    CARD_SHADOW,
    DANGER_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    TEXT_SECONDARY_COLOR,
    WARNING_COLOR,
)


def appliquer_styles_globaux() -> None:
    """
    Injecte le CSS global de RiskVision AI dans l'application Streamlit.
    """

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(
                    circle at top right,
                    rgba(37, 99, 235, 0.08),
                    transparent 28%
                ),
                {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
        }}

        html, body, [class*="css"] {{
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }}

        .block-container {{
            max-width: 1380px;
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
        }}

        header[data-testid="stHeader"] {{
            background: rgba(245, 247, 250, 0.82);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(100, 116, 139, 0.12);
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        h1, h2, h3, h4 {{
            color: {PRIMARY_COLOR};
            letter-spacing: -0.025em;
        }}

        h1 {{
            font-weight: 800;
        }}

        h2, h3 {{
            font-weight: 700;
        }}

        p, label, .stMarkdown {{
            color: {TEXT_COLOR};
        }}

        .riskvision-muted {{
            color: {TEXT_SECONDARY_COLOR};
        }}

        .riskvision-eyebrow {{
            display: inline-block;
            margin-bottom: 0.75rem;
            color: {SECONDARY_COLOR};
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}

        .riskvision-hero {{
            position: relative;
            overflow: hidden;
            padding: 2.8rem 3rem;
            margin-bottom: 1.8rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 28px;
            background:
                linear-gradient(
                    135deg,
                    {PRIMARY_COLOR} 0%,
                    #214F78 52%,
                    {SECONDARY_COLOR} 100%
                );
            box-shadow: 0 22px 55px rgba(22, 50, 79, 0.22);
        }}

        .riskvision-hero::after {{
            content: "";
            position: absolute;
            width: 320px;
            height: 320px;
            right: -100px;
            top: -120px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.10);
        }}

        .riskvision-hero h1 {{
            position: relative;
            z-index: 1;
            max-width: 850px;
            margin: 0;
            color: #FFFFFF;
            font-size: clamp(2.1rem, 4vw, 4rem);
            line-height: 1.04;
        }}

        .riskvision-hero p {{
            position: relative;
            z-index: 1;
            max-width: 760px;
            margin-top: 1rem;
            margin-bottom: 0;
            color: rgba(255, 255, 255, 0.82);
            font-size: 1.05rem;
            line-height: 1.7;
        }}

        .riskvision-badge {{
            position: relative;
            z-index: 1;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.8rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            color: #FFFFFF;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        .riskvision-card {{
            height: 100%;
            padding: 1.35rem 1.4rem;
            border: 1px solid rgba(100, 116, 139, 0.14);
            border-radius: {CARD_RADIUS}px;
            background: {CARD_COLOR};
            box-shadow: {CARD_SHADOW};
        }}

        .riskvision-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.10);
            transition: all 180ms ease;
        }}

        .riskvision-card-title {{
            margin-bottom: 0.45rem;
            color: {TEXT_SECONDARY_COLOR};
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .riskvision-card-value {{
            color: {PRIMARY_COLOR};
            font-size: 1.95rem;
            font-weight: 800;
            line-height: 1.1;
        }}

        .riskvision-card-description {{
            margin-top: 0.65rem;
            color: {TEXT_SECONDARY_COLOR};
            font-size: 0.9rem;
            line-height: 1.5;
        }}

        div[data-testid="stMetric"] {{
            min-height: 138px;
            padding: 1.25rem 1.35rem;
            border: 1px solid rgba(100, 116, 139, 0.14);
            border-radius: {CARD_RADIUS}px;
            background: {CARD_COLOR};
            box-shadow: {CARD_SHADOW};
        }}

        div[data-testid="stMetricLabel"] {{
            color: {TEXT_SECONDARY_COLOR};
            font-weight: 700;
        }}

        div[data-testid="stMetricValue"] {{
            color: {PRIMARY_COLOR};
            font-size: 2rem;
            font-weight: 800;
        }}

        .stButton > button,
        .stFormSubmitButton > button {{
            min-height: 50px;
            border: 0;
            border-radius: {BUTTON_RADIUS}px;
            background:
                linear-gradient(
                    135deg,
                    {SECONDARY_COLOR},
                    #1D4ED8
                );
            color: #FFFFFF;
            font-weight: 750;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
            transition:
                transform 160ms ease,
                box-shadow 160ms ease,
                filter 160ms ease;
        }}

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {{
            transform: translateY(-1px);
            filter: brightness(1.04);
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.30);
            color: #FFFFFF;
        }}

        .stButton > button:active,
        .stFormSubmitButton > button:active {{
            transform: translateY(0);
        }}

        div[data-testid="stForm"] {{
            padding: 1.5rem;
            border: 1px solid rgba(100, 116, 139, 0.14);
            border-radius: 22px;
            background: {CARD_COLOR};
            box-shadow: {CARD_SHADOW};
        }}

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {{
            min-height: 48px;
            border-radius: 12px;
            border-color: rgba(100, 116, 139, 0.22);
            background: #FFFFFF;
        }}

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {{
            border-color: {SECONDARY_COLOR};
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }}

        label[data-testid="stWidgetLabel"] p {{
            color: {TEXT_COLOR};
            font-weight: 700;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 14px;
        }}

        .riskvision-status-success {{
            padding: 1rem 1.1rem;
            border: 1px solid rgba(22, 163, 74, 0.20);
            border-radius: 14px;
            background: rgba(22, 163, 74, 0.08);
            color: {SUCCESS_COLOR};
            font-weight: 800;
        }}

        .riskvision-status-warning {{
            padding: 1rem 1.1rem;
            border: 1px solid rgba(245, 158, 11, 0.22);
            border-radius: 14px;
            background: rgba(245, 158, 11, 0.09);
            color: {WARNING_COLOR};
            font-weight: 800;
        }}

        .riskvision-status-danger {{
            padding: 1rem 1.1rem;
            border: 1px solid rgba(220, 38, 38, 0.20);
            border-radius: 14px;
            background: rgba(220, 38, 38, 0.08);
            color: {DANGER_COLOR};
            font-weight: 800;
        }}

        section[data-testid="stSidebar"] {{
            border-right: 1px solid rgba(100, 116, 139, 0.12);
            background:
                linear-gradient(
                    180deg,
                    #FFFFFF 0%,
                    #F8FAFC 100%
                );
        }}

        section[data-testid="stSidebar"] > div {{
            padding-top: 1.3rem;
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
            color: {PRIMARY_COLOR};
        }}

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
            padding: 0.55rem 0.65rem;
            border-radius: 10px;
        }}

        div[data-testid="stDataFrame"] {{
            overflow: hidden;
            border: 1px solid rgba(100, 116, 139, 0.14);
            border-radius: 16px;
            background: {CARD_COLOR};
        }}

        details[data-testid="stExpander"] {{
            border: 1px solid rgba(100, 116, 139, 0.14);
            border-radius: 14px;
            background: {CARD_COLOR};
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }}

        div[data-testid="stProgress"] > div > div {{
            border-radius: 999px;
        }}

        div[data-testid="stProgress"] > div > div > div {{
            background:
                linear-gradient(
                    90deg,
                    {SUCCESS_COLOR},
                    {WARNING_COLOR},
                    {DANGER_COLOR}
                );
        }}

        hr {{
            border: none;
            border-top: 1px solid rgba(100, 116, 139, 0.14);
        }}

        .riskvision-footer {{
            margin-top: 3rem;
            padding-top: 1.2rem;
            border-top: 1px solid rgba(100, 116, 139, 0.14);
            color: {TEXT_SECONDARY_COLOR};
            font-size: 0.82rem;
            text-align: center;
        }}

              /* =========================================================
           IDENTITÉ DE LA SIDEBAR
           ========================================================= */

        .riskvision-sidebar-brand {{
            padding: 0.6rem 0.4rem 0.8rem 0.4rem;
            text-align: center;
        }}

        .riskvision-sidebar-logo {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 58px;
            height: 58px;
            margin: 0 auto 0.8rem auto;
            border-radius: 18px;
            background:
                linear-gradient(
                    135deg,
                    #16324F,
                    #2563EB
                );
            color: #FFFFFF;
            font-size: 1.7rem;
            box-shadow:
                0 10px 24px rgba(37, 99, 235, 0.24);
        }}

        .riskvision-sidebar-name {{
            color: #16324F;
            font-size: 1.22rem;
            font-weight: 850;
            letter-spacing: -0.02em;
        }}

        .riskvision-sidebar-subtitle {{
            max-width: 220px;
            margin: 0.45rem auto 0 auto;
            color: #64748B;
            font-size: 0.76rem;
            line-height: 1.45;
        }}

        /* =========================================================
           MENU DE NAVIGATION
           ========================================================= */

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] > div {{
            gap: 0.35rem;
        }}

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] label {{
            width: 100%;
            padding: 0.72rem 0.85rem;
            border-radius: 11px;
            color: #334155;
            font-size: 0.91rem;
            font-weight: 650;
            transition:
                background 160ms ease,
                color 160ms ease,
                transform 160ms ease;
        }}

        section[data-testid="stSidebar"]
        div[data-testid="stRadio"] label:hover {{
            transform: translateX(2px);
            background: rgba(37, 99, 235, 0.08);
            color: #2563EB;
        }}

        /* =========================================================
           CARTE DU MODÈLE
           ========================================================= */

        .riskvision-sidebar-spacer {{
            min-height: 1rem;
        }}

        .riskvision-model-card {{
            padding: 1rem;
            border: 1px solid rgba(100, 116, 139, 0.14);
            border-radius: 16px;
            background: #FFFFFF;
            box-shadow:
                0 8px 22px rgba(15, 23, 42, 0.06);
        }}

        .riskvision-model-status {{
            display: flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.75rem;
            color: #16A34A;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        .riskvision-status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #16A34A;
            box-shadow:
                0 0 0 4px rgba(22, 163, 74, 0.12);
        }}

        .riskvision-model-title {{
            margin-bottom: 0.85rem;
            color: #16324F;
            font-size: 0.98rem;
            font-weight: 800;
        }}

        .riskvision-model-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.65rem;
        }}

        .riskvision-model-grid div {{
            padding: 0.62rem;
            border-radius: 10px;
            background: #F8FAFC;
        }}

        .riskvision-model-grid span {{
            display: block;
            margin-bottom: 0.2rem;
            color: #64748B;
            font-size: 0.66rem;
        }}

        .riskvision-model-grid strong {{
            color: #16324F;
            font-size: 0.82rem;
        }}

        .riskvision-sidebar-version {{
            margin-top: 0.9rem;
            color: #94A3B8;
            font-size: 0.67rem;
            text-align: center;
        }}

        /* =========================================================
   CARTES KPI
   ========================================================= */

.riskvision-kpi-card {{
    min-height: 190px;
    padding: 1.35rem;
    border: 1px solid rgba(100, 116, 139, 0.14);
    border-radius: 22px;
    background: #FFFFFF;
    box-shadow:
        0 12px 30px rgba(15, 23, 42, 0.07);
    transition:
        transform 180ms ease,
        box-shadow 180ms ease;
}}

.riskvision-kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow:
        0 18px 36px rgba(15, 23, 42, 0.11);
}}

.riskvision-kpi-header {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1.1rem;
}}

.riskvision-kpi-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 13px;
    background: rgba(37, 99, 235, 0.10);
    font-size: 1.25rem;
}}

.riskvision-kpi-title {{
    color: #64748B;
    font-size: 0.82rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.riskvision-kpi-value {{
    margin-bottom: 0.55rem;
    color: #16324F;
    font-size: 2.25rem;
    font-weight: 850;
    line-height: 1;
    letter-spacing: -0.04em;
}}

.riskvision-kpi-description {{
    color: #64748B;
    font-size: 0.82rem;
    line-height: 1.45;
}}

        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            .riskvision-hero {{
                padding: 2rem 1.4rem;
                border-radius: 22px;
            }}

            .riskvision-hero h1 {{
                font-size: 2.2rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def afficher_hero(
    titre: str,
    sous_titre: str,
    badge: str = "Machine Learning • BODACC • SHAP",
) -> None:
    """
    Affiche une bannière principale réutilisable.
    """

    st.markdown(
        f"""
        <section class="riskvision-hero">
            <div class="riskvision-badge">{badge}</div>
            <h1>{titre}</h1>
            <p>{sous_titre}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def afficher_footer(
    texte: str = (
        "RiskVision AI • Modèle exploratoire basé sur des annonces BODACC"
    ),
) -> None:
    """
    Affiche le pied de page commun.
    """

    st.markdown(
        f"""
        <div class="riskvision-footer">
            {texte}
        </div>
        """,
        unsafe_allow_html=True,
    )