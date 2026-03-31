"""
Design system centralizado — Warm Neutral.
Importar em todas as páginas: from styles import aplicar_css, margem_cor, barra_margem
"""
import streamlit as st

FONTS = "https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@700;800&family=Outfit:wght@300;400;500;600&display=swap"

CSS = f"""
<style>
@import url('{FONTS}');

/* ── Reset & Base ───────────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif !important;
}}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stHeader"] {{
    background-color: #fafaf9 !important;
}}

[data-testid="stHeader"] {{
    border-bottom: 1px solid #e7e5e4 !important;
    background-color: #fafaf9 !important;
}}

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
    background-color: #fafaf9 !important;
}}

/* ── Tipografia ─────────────────────────────────────────────── */
h1 {{
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #1c1917 !important;
    line-height: 1.1 !important;
    margin-bottom: 0.25rem !important;
}}
h2 {{
    font-family: 'Syne', sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: #1c1917 !important;
}}
h3 {{
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #292524 !important;
}}

/* ── Label uppercase ────────────────────────────────────────── */
.label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a8a29e;
    margin-bottom: 0.5rem;
    display: block;
}}

/* ── KPI Cards ──────────────────────────────────────────────── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 2rem;
}}
.kpi-card {{
    background: #ffffff;
    border: 1px solid #e7e5e4;
    border-radius: 10px;
    padding: 1.25rem;
    position: relative;
}}
.kpi-card:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.kpi-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a8a29e;
    margin-bottom: 0.5rem;
}}
.kpi-value {{
    font-family: 'DM Mono', monospace;
    font-size: 1.75rem;
    font-weight: 500;
    color: #1c1917;
    line-height: 1;
}}
.kpi-delta-pos {{ color: #16a34a; font-size: 0.8rem; font-family: 'DM Mono', monospace; }}
.kpi-delta-neg {{ color: #dc2626; font-size: 0.8rem; font-family: 'DM Mono', monospace; }}
.kpi-delta-neu {{ color: #ea580c; font-size: 0.8rem; font-family: 'DM Mono', monospace; }}

/* ── Metric override ────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: #ffffff;
    border: 1px solid #e7e5e4;
    border-radius: 10px;
    padding: 1.25rem !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #a8a29e !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 1.6rem !important;
    color: #1c1917 !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}}

/* ── Section header ─────────────────────────────────────────── */
.section-header {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #ea580c;
    margin: 1.75rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e7e5e4;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.section-header::before {{
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: #ea580c;
    border-radius: 2px;
}}

/* ── Tabelas ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border: 1px solid #e7e5e4 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Forms ──────────────────────────────────────────────────── */
[data-testid="stForm"] {{
    background: #ffffff;
    border: 1px solid #e7e5e4;
    border-radius: 12px;
    padding: 1.5rem !important;
}}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {{
    background: #fafaf9 !important;
    border-color: #e7e5e4 !important;
    color: #1c1917 !important;
    font-family: 'Outfit', sans-serif !important;
}}
[data-baseweb="input"] input:focus {{
    border-color: #ea580c !important;
    box-shadow: 0 0 0 2px rgba(234,88,12,0.12) !important;
}}
[data-baseweb="select"] > div {{
    background: #fafaf9 !important;
    border-color: #e7e5e4 !important;
    color: #1c1917 !important;
}}

/* ── Buttons ────────────────────────────────────────────────── */
[data-testid="baseButton-primary"] {{
    background: #ea580c !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.02em !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
}}
[data-testid="baseButton-primary"]:hover {{
    background: #c2410c !important;
}}
[data-testid="baseButton-secondary"] {{
    background: transparent !important;
    border: 1px solid #e7e5e4 !important;
    color: #78716c !important;
    font-family: 'Outfit', sans-serif !important;
    border-radius: 8px !important;
}}
[data-testid="baseButton-secondary"]:hover {{
    border-color: #dc2626 !important;
    color: #dc2626 !important;
}}

/* ── Tabs ───────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid #e7e5e4 !important;
    gap: 0 !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    color: #a8a29e !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 0 !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    color: #ea580c !important;
    border-bottom: 2px solid #ea580c !important;
}}

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: #ffffff !important;
    border: 1px solid #e7e5e4 !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}}
[data-testid="stExpander"] summary {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    color: #1c1917 !important;
    padding: 1rem 1.25rem !important;
}}

/* ── Alerts ─────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: #f5f5f4 !important;
    border-right: 1px solid #e7e5e4 !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: #78716c !important;
    font-size: 0.8rem !important;
}}

/* ── Divider ────────────────────────────────────────────────── */
hr {{ border-color: #e7e5e4 !important; margin: 1.5rem 0 !important; }}

/* ── Mono values ────────────────────────────────────────────── */
.mono {{
    font-family: 'DM Mono', monospace;
    color: #57534e;
}}
.mono-lg {{
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    color: #1c1917;
}}

/* ── Barra de margem ────────────────────────────────────────── */
.margem-bar-wrap {{
    background: #f5f5f4;
    border-radius: 4px;
    height: 6px;
    width: 100%;
    overflow: hidden;
    margin-top: 6px;
}}
.margem-bar {{
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}}

/* ── Tag de categoria ───────────────────────────────────────── */
.tag {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 500;
    font-family: 'DM Mono', monospace;
    margin: 2px;
}}
.tag-embalagem    {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }}
.tag-frete        {{ background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; }}
.tag-taxa         {{ background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }}
.tag-imposto      {{ background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }}
.tag-outro        {{ background: #f5f5f4; color: #57534e; border: 1px solid #e7e5e4; }}

/* ── Canal badge ────────────────────────────────────────────── */
.canal-badge {{
    display: inline-block;
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    background: #f5f5f4;
    color: #57534e;
    border: 1px solid #e7e5e4;
}}

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: #f5f5f4; }}
::-webkit-scrollbar-thumb {{ background: #d6d3d1; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: #a8a29e; }}
</style>
"""


def aplicar_css():
    st.markdown(CSS, unsafe_allow_html=True)


def secao(titulo: str):
    st.markdown(f'<div class="section-header">{titulo}</div>', unsafe_allow_html=True)


def margem_cor(pct: float) -> str:
    if pct >= 50:
        return "#16a34a"
    elif pct >= 30:
        return "#d97706"
    else:
        return "#dc2626"


def barra_margem(pct: float) -> str:
    cor = margem_cor(pct)
    largura = min(100, max(0, pct))
    return f"""
    <div class="margem-bar-wrap">
        <div class="margem-bar" style="width:{largura}%;background:{cor};"></div>
    </div>
    """


def kpi_cards(items: list):
    """
    items: lista de dicts com {label, value, delta?, delta_type?}
    delta_type: 'pos' | 'neg' | 'neu'
    """
    n = len(items)
    cols_css = " ".join(["1fr"] * n)
    html = f'<div class="kpi-grid" style="grid-template-columns:{cols_css};">'
    for item in items:
        delta_html = ""
        if item.get("delta"):
            dt = item.get("delta_type", "neu")
            cls = f"kpi-delta-{dt}"
            delta_html = f'<div class="{cls}" style="margin-top:0.4rem">{item["delta"]}</div>'
        html += f"""
        <div class="kpi-card">
            <div class="kpi-label">{item["label"]}</div>
            <div class="kpi-value">{item["value"]}</div>
            {delta_html}
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
