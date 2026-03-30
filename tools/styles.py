"""
Design system centralizado.
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
    background-color: #080808 !important;
}}

[data-testid="stHeader"] {{
    border-bottom: 1px solid #141414 !important;
}}

/* Remove padding padrão do Streamlit */
.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
    background-color: #080808 !important;
}}

/* ── Tipografia ─────────────────────────────────────────────── */
h1 {{
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #ffffff !important;
    line-height: 1.1 !important;
    margin-bottom: 0.25rem !important;
}}
h2 {{
    font-family: 'Syne', sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: #e5e5e5 !important;
}}
h3 {{
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #d4d4d4 !important;
}}

/* ── Label uppercase ────────────────────────────────────────── */
.label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #737373;
    margin-bottom: 0.5rem;
    display: block;
}}

/* ── KPI Cards ──────────────────────────────────────────────── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #1a1a1a;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 2rem;
    border: 1px solid #1a1a1a;
}}
.kpi-card {{
    background: #0f0f0f;
    padding: 1.5rem 1.25rem;
    position: relative;
}}
.kpi-card:hover {{ background: #111; }}
.kpi-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #525252;
    margin-bottom: 0.5rem;
}}
.kpi-value {{
    font-family: 'DM Mono', monospace;
    font-size: 1.75rem;
    font-weight: 500;
    color: #ffffff;
    line-height: 1;
}}
.kpi-delta-pos {{ color: #4ade80; font-size: 0.8rem; font-family: 'DM Mono', monospace; }}
.kpi-delta-neg {{ color: #f87171; font-size: 0.8rem; font-family: 'DM Mono', monospace; }}
.kpi-delta-neu {{ color: #f97316; font-size: 0.8rem; font-family: 'DM Mono', monospace; }}

/* ── Metric override ────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 1.25rem !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #525252 !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 1.6rem !important;
    color: #ffffff !important;
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
    color: #f97316;
    margin: 1.75rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e1e1e;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.section-header::before {{
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: #f97316;
    border-radius: 2px;
}}

/* ── Tabelas ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* ── Forms ──────────────────────────────────────────────────── */
[data-testid="stForm"] {{
    background: #0d0d0d;
    border: 1px solid #1e1e1e;
    border-radius: 12px;
    padding: 1.5rem !important;
}}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {{
    background: #141414 !important;
    border-color: #2a2a2a !important;
    color: #e5e5e5 !important;
    font-family: 'Outfit', sans-serif !important;
}}
[data-baseweb="input"] input:focus {{
    border-color: #f97316 !important;
    box-shadow: 0 0 0 2px rgba(249,115,22,0.15) !important;
}}
[data-baseweb="select"] > div {{
    background: #141414 !important;
    border-color: #2a2a2a !important;
    color: #e5e5e5 !important;
}}

/* ── Buttons ────────────────────────────────────────────────── */
[data-testid="baseButton-primary"] {{
    background: #f97316 !important;
    border: none !important;
    color: #000 !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.02em !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
}}
[data-testid="baseButton-primary"]:hover {{
    background: #fb923c !important;
}}
[data-testid="baseButton-secondary"] {{
    background: transparent !important;
    border: 1px solid #2a2a2a !important;
    color: #737373 !important;
    font-family: 'Outfit', sans-serif !important;
    border-radius: 8px !important;
}}
[data-testid="baseButton-secondary"]:hover {{
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}}

/* ── Tabs ───────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid #1e1e1e !important;
    gap: 0 !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    color: #525252 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 0 !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    color: #f97316 !important;
    border-bottom: 2px solid #f97316 !important;
}}

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: #0d0d0d !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}}
[data-testid="stExpander"] summary {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    color: #d4d4d4 !important;
    padding: 1rem 1.25rem !important;
}}

/* ── Alerts ─────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: #050505 !important;
    border-right: 1px solid #141414 !important;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: #737373 !important;
    font-size: 0.8rem !important;
}}

/* ── Divider ────────────────────────────────────────────────── */
hr {{ border-color: #1a1a1a !important; margin: 1.5rem 0 !important; }}

/* ── Mono values ────────────────────────────────────────────── */
.mono {{
    font-family: 'DM Mono', monospace;
    color: #a3a3a3;
}}
.mono-lg {{
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    color: #ffffff;
}}

/* ── Barra de margem ────────────────────────────────────────── */
.margem-bar-wrap {{
    background: #1a1a1a;
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
.tag-embalagem    {{ background: rgba(59,130,246,0.12); color: #93c5fd; border: 1px solid rgba(59,130,246,0.3); }}
.tag-frete        {{ background: rgba(139,92,246,0.12); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.3); }}
.tag-taxa         {{ background: rgba(245,158,11,0.12); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }}
.tag-imposto      {{ background: rgba(239,68,68,0.12);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }}
.tag-outro        {{ background: rgba(107,114,128,0.12);color: #d1d5db; border: 1px solid rgba(107,114,128,0.3); }}

/* ── Canal badge ────────────────────────────────────────────── */
.canal-badge {{
    display: inline-block;
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    background: #1a1a1a;
    color: #a3a3a3;
    border: 1px solid #2a2a2a;
}}

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: #0a0a0a; }}
::-webkit-scrollbar-thumb {{ background: #2a2a2a; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: #404040; }}
</style>
"""


def aplicar_css():
    st.markdown(CSS, unsafe_allow_html=True)


def secao(titulo: str):
    st.markdown(f'<div class="section-header">{titulo}</div>', unsafe_allow_html=True)


def margem_cor(pct: float) -> str:
    if pct >= 50:
        return "#4ade80"
    elif pct >= 30:
        return "#facc15"
    else:
        return "#f87171"


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
    html = f'<div style="display:grid;grid-template-columns:{cols_css};gap:1px;background:#1a1a1a;border-radius:12px;overflow:hidden;margin-bottom:1.5rem;border:1px solid #1a1a1a;">'
    for item in items:
        delta_html = ""
        if item.get("delta"):
            dt = item.get("delta_type", "neu")
            cls = f"kpi-delta-{dt}"
            delta_html = f'<div class="{cls}">{item["delta"]}</div>'
        html += f"""
        <div class="kpi-card">
            <div class="kpi-label">{item["label"]}</div>
            <div class="kpi-value">{item["value"]}</div>
            {delta_html}
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
