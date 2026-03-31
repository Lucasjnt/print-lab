# Print Lab — Redesign Executivo + Fix de Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir tema escuro por Warm Neutral e eliminar resets de página usando `st.fragment` em todas as seções CRUD.

**Architecture:** O design system está centralizado em `tools/styles.py` — reescrever o CSS ali e atualizar `config.toml` já muda a base de todas as páginas. Cada seção de formulário/lista que chama `st.rerun()` vira um `@st.fragment` autônomo: a função lê os dados do banco internamente, então quando o fragmento re-executa ele busca dados frescos sem recarregar a página toda.

**Tech Stack:** Python 3 · Streamlit 1.55 · SQLite · `@st.fragment` (disponível desde Streamlit 1.37)

---

## Mapa de arquivos

| Arquivo | Ação | O que muda |
|---|---|---|
| `.streamlit/config.toml` | Modificar | `base = "light"`, novas cores |
| `tools/styles.py` | Reescrever | CSS completo Warm Neutral, `margem_cor()` com novas cores |
| `app.py` | Modificar | Cores inline no HTML (hardcoded) |
| `pages/03_Vendas.py` | Modificar | 2 fragments + cores inline |
| `pages/04_PL.py` | Modificar | 2 fragments (custos fixos) + cores inline |
| `pages/02_Produtos.py` | Modificar | 3 fragments (lista, edição, cadastro) + cores inline |
| `pages/01_Calculadora.py` | Modificar | Cores inline |
| `pages/05_Dashboard.py` | Modificar | Cores inline |

---

## Task 1: Atualizar config.toml para tema light

**Files:**
- Modify: `.streamlit/config.toml`

- [ ] **Step 1: Sobrescrever config.toml com tema Warm Neutral**

```toml
[theme]
base = "light"
backgroundColor = "#fafaf9"
secondaryBackgroundColor = "#ffffff"
primaryColor = "#ea580c"
textColor = "#1c1917"

[server]
headless = true
```

- [ ] **Step 2: Verificar manualmente**

Rodar `streamlit run app.py` e confirmar que o fundo mudou de preto para off-white.

- [ ] **Step 3: Commit**

```bash
git add .streamlit/config.toml
git commit -m "feat: switch theme to Warm Neutral (light base)"
```

---

## Task 2: Reescrever tools/styles.py com paleta Warm Neutral

**Files:**
- Modify: `tools/styles.py`

- [ ] **Step 1: Substituir todo o conteúdo de tools/styles.py**

```python
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
```

- [ ] **Step 2: Verificar no browser**

Abrir `http://localhost:8501` e confirmar fundo off-white, cards com bordas sutis, labels laranja.

- [ ] **Step 3: Commit**

```bash
git add tools/styles.py
git commit -m "feat: rewrite design system with Warm Neutral palette"
```

---

## Task 3: Atualizar app.py — cores inline do HTML

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Substituir todo o conteúdo de app.py**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

from tools.db import init_db
from tools.styles import aplicar_css, kpi_cards, secao
import streamlit as st
from datetime import date

init_db()

st.set_page_config(
    page_title="Print Lab — Gestão 3D",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_css()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2.5rem;">
  <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;
              color:#ea580c;margin-bottom:0.5rem;">
    PRINT LAB
  </div>
  <h1 style="margin:0 0 0.5rem 0;">Gestão de<br>Impressão 3D</h1>
  <p style="color:#a8a29e;font-size:1rem;margin:0;max-width:480px;">
    Controle completo de custos, margens e P&L para o seu negócio.
  </p>
</div>
""", unsafe_allow_html=True)

# ── KPIs do mês atual ─────────────────────────────────────────────────────────
try:
    from tools.calcular_margem import calcular_pl
    hoje = date.today()
    pl = calcular_pl(date(hoje.year, hoje.month, 1), hoje)

    kpi_cards([
        {
            "label": "Receita do Mês",
            "value": f"R$ {pl['receita_total']:,.2f}",
            "delta": f"{len(pl['vendas'])} vendas",
            "delta_type": "neu",
        },
        {
            "label": "Lucro Bruto",
            "value": f"R$ {pl['lucro_bruto']:,.2f}",
            "delta": f"{pl['margem_bruta_pct']:.1f}% margem",
            "delta_type": "pos" if pl['margem_bruta_pct'] >= 40 else "neg",
        },
        {
            "label": "Lucro Líquido",
            "value": f"R$ {pl['lucro_liquido']:,.2f}",
            "delta": f"{pl['margem_liquida_pct']:.1f}% margem",
            "delta_type": "pos" if pl['margem_liquida_pct'] >= 20 else "neg",
        },
        {
            "label": "Custos Fixos",
            "value": f"R$ {pl['custos_fixos_mes']:,.2f}",
            "delta": "/ mês",
            "delta_type": "neu",
        },
    ])
except Exception:
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ── Navegação ─────────────────────────────────────────────────────────────────
secao("Navegação")

col1, col2, col3, col4, col5 = st.columns(5)

nav_items = [
    (col1, "🧮", "Calculadora", "Simule custos de impressão e descubra a margem por produto"),
    (col2, "📦", "Produtos", "Gerencie catálogo, materiais, impressoras e custos adicionais"),
    (col3, "💰", "Vendas", "Registre vendas diárias e acompanhe o histórico por canal"),
    (col4, "📊", "P&L", "Demonstrativo de resultado completo com exportação CSV"),
    (col5, "📈", "Dashboard", "KPIs, gráficos de receita e ranking de produtos"),
]

for col, icon, titulo, desc in nav_items:
    with col:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid #e7e5e4;border-left:3px solid #ea580c;
                    border-radius:10px;padding:1.25rem;height:100%;cursor:pointer;transition:box-shadow 0.2s;"
             onmouseover="this.style.boxShadow='0 2px 12px rgba(0,0,0,0.08)'"
             onmouseout="this.style.boxShadow='none'">
          <div style="font-size:1.5rem;margin-bottom:0.5rem">{icon}</div>
          <div style="font-family:'Syne',sans-serif;font-weight:700;color:#1c1917;
                      margin-bottom:0.4rem">{titulo}</div>
          <div style="font-size:0.8rem;color:#a8a29e;line-height:1.4">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Quick start ───────────────────────────────────────────────────────────────
secao("Início rápido")
st.markdown("""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
  <div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;padding:1rem 1.25rem;">
    <div style="font-family:'DM Mono',monospace;color:#ea580c;font-size:0.9rem;margin-bottom:0.4rem">01</div>
    <div style="font-weight:600;color:#1c1917;margin-bottom:0.25rem">Cadastrar equipamento</div>
    <div style="font-size:0.8rem;color:#a8a29e">Em Produtos → Impressoras: adicione sua impressora com custo, vida útil e consumo em Watts.</div>
  </div>
  <div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;padding:1rem 1.25rem;">
    <div style="font-family:'DM Mono',monospace;color:#ea580c;font-size:0.9rem;margin-bottom:0.4rem">02</div>
    <div style="font-weight:600;color:#1c1917;margin-bottom:0.25rem">Criar produtos com custos</div>
    <div style="font-size:0.8rem;color:#a8a29e">Em Produtos: cadastre cada peça e adicione custos extras (embalagem, frete, taxas) por produto.</div>
  </div>
  <div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;padding:1rem 1.25rem;">
    <div style="font-family:'DM Mono',monospace;color:#ea580c;font-size:0.9rem;margin-bottom:0.4rem">03</div>
    <div style="font-weight:600;color:#1c1917;margin-bottom:0.25rem">Registrar vendas</div>
    <div style="font-size:0.8rem;color:#a8a29e">Em Vendas: registre cada venda com produto, quantidade, canal e preço. O P&L atualiza em tempo real.</div>
  </div>
</div>
""", unsafe_allow_html=True)
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "feat: update app.py inline HTML to Warm Neutral colors"
```

---

## Task 4: Vendas — fragments + cores

**Files:**
- Modify: `pages/03_Vendas.py`

- [ ] **Step 1: Substituir todo o conteúdo de 03_Vendas.py**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd
from datetime import date
from db import listar_produtos, listar_vendas, inserir_venda, deletar_venda
from styles import aplicar_css, secao, kpi_cards

st.set_page_config(page_title="Vendas — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

CANAIS = ["Instagram", "WhatsApp", "Feira", "Site", "Indicação", "Outro"]
CANAL_CORES = {
    "Instagram": "#e1306c", "WhatsApp": "#16a34a", "Feira": "#ea580c",
    "Site": "#2563eb", "Indicação": "#7c3aed", "Outro": "#78716c",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Vendas</h1>
  <p style="color:#a8a29e;margin:0;font-size:0.95rem;">Registre cada venda e acompanhe o resultado por canal.</p>
</div>
""", unsafe_allow_html=True)

produtos = listar_produtos()
if not produtos:
    st.warning("Nenhum produto cadastrado. Vá para **Produtos** antes de registrar vendas.")
    st.stop()

# ── KPIs do mês ───────────────────────────────────────────────────────────────
hoje = date.today()
vendas_mes = listar_vendas(date(hoje.year, hoje.month, 1), hoje)
if vendas_mes:
    df_mes = pd.DataFrame(vendas_mes)
    df_mes["total"] = df_mes["preco_unit"] * df_mes["quantidade"]
    receita_mes = df_mes["total"].sum()
    qtd_mes = df_mes["quantidade"].sum()
    ticket_medio = receita_mes / len(vendas_mes)
    canal_top = df_mes.groupby("canal")["total"].sum().idxmax() if not df_mes.empty else "—"

    kpi_cards([
        {"label": "Receita do Mês", "value": f"R$ {receita_mes:,.2f}", "delta": f"{len(vendas_mes)} pedidos", "delta_type": "pos"},
        {"label": "Unidades Vendidas", "value": str(int(qtd_mes)), "delta": "este mês", "delta_type": "neu"},
        {"label": "Ticket Médio", "value": f"R$ {ticket_medio:.2f}", "delta": "por pedido", "delta_type": "neu"},
        {"label": "Canal Líder", "value": canal_top, "delta": "maior receita", "delta_type": "pos"},
    ])

st.markdown("---")

# ── Fragment: Registrar Venda ─────────────────────────────────────────────────
@st.fragment
def form_registrar_venda():
    produtos = listar_produtos()
    secao("Registrar Nova Venda")
    with st.form("form_venda", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        prod_id = c1.selectbox(
            "Produto",
            [p["id"] for p in produtos],
            format_func=lambda x: next(p["nome"] for p in produtos if p["id"] == x),
        )
        qtd = c2.number_input("Quantidade", value=1, min_value=1, step=1)
        data_v = c3.date_input("Data", value=date.today())

        produto_selecionado = next(p for p in produtos if p["id"] == prod_id)

        c1, c2, c3 = st.columns([2, 1, 1])
        preco_unit = c1.number_input(
            "Preço unitário (R$)",
            value=float(produto_selecionado["preco_venda"]),
            min_value=0.01, step=0.5,
            help="Preço padrão do produto, ajuste se vendeu diferente"
        )
        canal = c2.selectbox("Canal", CANAIS)

        total_preview = preco_unit * qtd
        c3.markdown(f"""
        <div style="padding-top:1.8rem;">
          <div style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.1em">Total</div>
          <div style="font-family:'DM Mono',monospace;color:#ea580c;font-size:1.3rem">R$ {total_preview:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.form_submit_button("Registrar venda", type="primary", use_container_width=True):
            inserir_venda(prod_id, data_v, qtd, preco_unit, canal)
            st.success(f"✓ Venda registrada: {qtd}× {produto_selecionado['nome']} — R$ {total_preview:.2f}")


form_registrar_venda()

st.markdown("---")

# ── Fragment: Histórico ───────────────────────────────────────────────────────
@st.fragment
def historico_vendas():
    secao("Histórico de Vendas")
    hoje = date.today()

    col1, col2, col3 = st.columns([1, 1, 1])
    data_ini = col1.date_input("De", value=date(hoje.year, hoje.month, 1))
    data_fim = col2.date_input("Até", value=hoje)
    canal_filtro = col3.selectbox("Canal", ["Todos"] + CANAIS)

    vendas = listar_vendas(data_ini, data_fim)
    if canal_filtro != "Todos":
        vendas = [v for v in vendas if v.get("canal") == canal_filtro]

    if vendas:
        df = pd.DataFrame(vendas)
        df["total"] = df["preco_unit"] * df["quantidade"]
        receita = df["total"].sum()

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
          <span style="color:#a8a29e;font-size:0.85rem">{len(vendas)} registro(s)</span>
          <span style="font-family:'DM Mono',monospace;color:#ea580c;font-size:1.1rem">
            Total: R$ {receita:,.2f}
          </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">
          <div style="display:grid;grid-template-columns:90px 1fr 100px 60px 100px 100px;
                      padding:0.6rem 1rem;border-bottom:1px solid #e7e5e4;background:#f5f5f4;">
            <span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">Data</span>
            <span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">Produto</span>
            <span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">Canal</span>
            <span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:center">Qtd</span>
            <span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Unit</span>
            <span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Total</span>
          </div>
        """, unsafe_allow_html=True)

        for v in vendas:
            total_linha = v["preco_unit"] * v["quantidade"]
            cor_canal = CANAL_CORES.get(v.get("canal", ""), "#78716c")
            st.markdown(f"""
          <div style="display:grid;grid-template-columns:90px 1fr 100px 60px 100px 100px;
                      padding:0.75rem 1rem;border-bottom:1px solid #f5f5f4;align-items:center;">
            <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#a8a29e">{v['data']}</span>
            <span style="color:#1c1917;font-size:0.9rem">{v['produto_nome']}</span>
            <span style="font-size:0.75rem;padding:2px 8px;border-radius:4px;
                         background:{cor_canal}15;color:{cor_canal};border:1px solid {cor_canal}40">
              {v.get('canal','—')}
            </span>
            <span style="font-family:'DM Mono',monospace;color:#a8a29e;text-align:center">{v['quantidade']}</span>
            <span style="font-family:'DM Mono',monospace;color:#57534e;text-align:right;font-size:0.85rem">R$ {v['preco_unit']:.2f}</span>
            <span style="font-family:'DM Mono',monospace;color:#1c1917;text-align:right;font-weight:600">R$ {total_linha:.2f}</span>
          </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.expander("Remover venda"):
            del_id = st.selectbox(
                "Selecione",
                [v["id"] for v in vendas],
                format_func=lambda x: next(f"#{x} — {v['produto_nome']} em {v['data']}" for v in vendas if v["id"] == x),
                label_visibility="collapsed",
            )
            if st.button("Confirmar remoção", type="secondary"):
                deletar_venda(del_id)
                st.success("Venda removida.")
                st.rerun()
    else:
        st.markdown("""
        <div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:10px;
                    padding:2.5rem;text-align:center;">
          <div style="color:#a8a29e;font-size:0.9rem">Nenhuma venda no período selecionado.</div>
        </div>
        """, unsafe_allow_html=True)


historico_vendas()
```

- [ ] **Step 2: Testar manualmente**

1. Abrir página Vendas
2. Registrar uma venda → confirmar que a página NÃO rola pro topo
3. O formulário limpa (clear_on_submit=True) mas fica no lugar
4. Remover uma venda → confirmar que a lista atualiza sem scroll reset

- [ ] **Step 3: Commit**

```bash
git add pages/03_Vendas.py
git commit -m "feat: vendas page — fragments + Warm Neutral colors"
```

---

## Task 5: P&L — fragments para custos fixos + cores

**Files:**
- Modify: `pages/04_PL.py`

- [ ] **Step 1: Substituir todo o conteúdo de 04_PL.py**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd
from datetime import date
from db import listar_custos_fixos, inserir_custo_fixo, atualizar_custo_fixo, deletar_custo_fixo
from calcular_margem import calcular_pl, ranking_produtos
from relatorios import pl_para_csv, ranking_para_csv
from styles import aplicar_css, secao, kpi_cards, margem_cor

st.set_page_config(page_title="P&L — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">P&L</h1>
  <p style="color:#a8a29e;margin:0;font-size:0.95rem;">Demonstrativo de resultado completo por período.</p>
</div>
""", unsafe_allow_html=True)

# ── Filtro ────────────────────────────────────────────────────────────────────
hoje = date.today()
col1, col2, col3 = st.columns([1, 1, 2])
data_ini = col1.date_input("De", value=date(hoje.year, hoje.month, 1))
data_fim = col2.date_input("Até", value=hoje)

pl = calcular_pl(data_ini, data_fim)
ranking = ranking_produtos(data_ini, data_fim)

# ── KPIs ──────────────────────────────────────────────────────────────────────
kpi_cards([
    {"label": "Receita Bruta",    "value": f"R$ {pl['receita_total']:,.2f}",
     "delta": f"{len(pl['vendas'])} vendas", "delta_type": "neu"},
    {"label": "CMV",              "value": f"R$ {pl['cmv_total']:,.2f}",
     "delta": f"{pl['cmv_total']/pl['receita_total']*100:.1f}% da receita" if pl['receita_total'] else "—",
     "delta_type": "neg"},
    {"label": "Lucro Bruto",      "value": f"R$ {pl['lucro_bruto']:,.2f}",
     "delta": f"Margem {pl['margem_bruta_pct']:.1f}%",
     "delta_type": "pos" if pl['margem_bruta_pct'] >= 40 else "neg"},
    {"label": "Lucro Líquido",    "value": f"R$ {pl['lucro_liquido']:,.2f}",
     "delta": f"Margem {pl['margem_liquida_pct']:.1f}%",
     "delta_type": "pos" if pl['margem_liquida_pct'] >= 20 else "neg"},
])

# ── DRE Visual ────────────────────────────────────────────────────────────────
secao("Demonstrativo de Resultado")

cor_bruto = "#16a34a" if pl["margem_bruta_pct"] >= 40 else "#d97706"
cor_liq   = "#16a34a" if pl["margem_liquida_pct"] >= 20 else "#dc2626"

dre_itens = [
    {"label": "(+) Receita Bruta",  "valor": pl["receita_total"],    "pct": 100.0,              "cor": "#1c1917", "destaque": False},
    {"label": "(−) CMV",            "valor": -pl["cmv_total"],       "pct": -pl["cmv_total"]/pl["receita_total"]*100 if pl["receita_total"] else 0, "cor": "#dc2626", "destaque": False},
    {"label": "(=) Lucro Bruto",    "valor": pl["lucro_bruto"],      "pct": pl["margem_bruta_pct"],  "cor": cor_bruto, "destaque": True},
    {"label": "(−) Custos Fixos",   "valor": -pl["custos_fixos_mes"],"pct": -pl["custos_fixos_mes"]/pl["receita_total"]*100 if pl["receita_total"] else 0, "cor": "#dc2626", "destaque": False},
    {"label": "(=) Lucro Líquido",  "valor": pl["lucro_liquido"],    "pct": pl["margem_liquida_pct"],"cor": cor_liq, "destaque": True},
]

for item in dre_itens:
    bg     = "#fff7ed" if item["destaque"] else "#ffffff"
    border = "1px solid #fed7aa" if item["destaque"] else "1px solid #e7e5e4"
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 140px 90px;align-items:center;
                background:{bg};border:{border};border-radius:8px;
                padding:0.85rem 1.25rem;margin-bottom:4px;">
      <span style="color:{'#1c1917' if item['destaque'] else '#57534e'};
                   font-weight:{'600' if item['destaque'] else '400'}">
        {item['label']}
      </span>
      <span style="font-family:'DM Mono',monospace;color:{item['cor']};
                   text-align:right;font-size:{'1.05rem' if item['destaque'] else '0.95rem'}">
        R$ {item['valor']:,.2f}
      </span>
      <span style="font-family:'DM Mono',monospace;color:#a8a29e;text-align:right;font-size:0.8rem">
        {item['pct']:.1f}%
      </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Ranking de produtos ───────────────────────────────────────────────────────
secao("Ranking de Produtos por Margem")

if ranking:
    st.markdown("""
    <div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">
      <div style="display:grid;grid-template-columns:24px 1fr 80px 100px 90px 100px;
                  padding:0.6rem 1rem;border-bottom:1px solid #e7e5e4;background:#f5f5f4;">
        <span style="font-size:0.65rem;color:#a8a29e">#</span>
        <span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">Produto</span>
        <span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:center">Qtd</span>
        <span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Receita</span>
        <span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Lucro</span>
        <span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Margem</span>
      </div>
    """, unsafe_allow_html=True)

    for i, r in enumerate(ranking):
        cor = margem_cor(r["margem_pct"])
        largura = min(100, r["margem_pct"])
        st.markdown(f"""
      <div style="display:grid;grid-template-columns:24px 1fr 80px 100px 90px 100px;
                  padding:0.85rem 1rem;border-bottom:1px solid #f5f5f4;align-items:center;">
        <span style="font-family:'DM Mono',monospace;color:#a8a29e;font-size:0.75rem">{i+1:02d}</span>
        <span style="color:#1c1917">{r['produto']}</span>
        <span style="font-family:'DM Mono',monospace;color:#78716c;text-align:center">{r['qtd_vendida']}</span>
        <span style="font-family:'DM Mono',monospace;color:#57534e;text-align:right;font-size:0.85rem">R$ {r['receita']:,.2f}</span>
        <span style="font-family:'DM Mono',monospace;color:#16a34a;text-align:right">R$ {r['lucro']:,.2f}</span>
        <div style="text-align:right;">
          <span style="font-family:'DM Mono',monospace;color:{cor}">{r['margem_pct']:.1f}%</span>
          <div style="background:#f5f5f4;border-radius:3px;height:3px;margin-top:4px;overflow:hidden;">
            <div style="width:{largura:.0f}%;height:100%;background:{cor};"></div>
          </div>
        </div>
      </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown('<p style="color:#a8a29e">Nenhuma venda no período.</p>', unsafe_allow_html=True)

# ── Detalhamento ──────────────────────────────────────────────────────────────
with st.expander("Detalhamento de vendas"):
    if pl["vendas"]:
        df_v = pd.DataFrame(pl["vendas"])[["data","produto_nome","canal","quantidade","preco_unit","receita_linha","cmv_linha","lucro_linha"]]
        df_v.columns = ["Data","Produto","Canal","Qtd","Preço Unit","Receita","CMV","Lucro"]
        st.dataframe(df_v, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda no período.")

# ── Exportar ──────────────────────────────────────────────────────────────────
secao("Exportar")
col1, col2 = st.columns(2)
col1.download_button(
    "⬇ Exportar P&L (CSV)",
    data=pl_para_csv(data_ini, data_fim).encode("utf-8-sig"),
    file_name=f"pl_{data_ini}_{data_fim}.csv",
    mime="text/csv",
    use_container_width=True,
)
col2.download_button(
    "⬇ Exportar Ranking (CSV)",
    data=ranking_para_csv(data_ini, data_fim).encode("utf-8-sig"),
    file_name=f"ranking_{data_ini}_{data_fim}.csv",
    mime="text/csv",
    use_container_width=True,
)

# ── Custos Fixos ──────────────────────────────────────────────────────────────
st.markdown("---")

@st.fragment
def secao_custos_fixos():
    secao("Custos Fixos Mensais")
    custos_fixos = listar_custos_fixos()
    col_lista, col_form = st.columns([1.5, 1])

    with col_lista:
        if custos_fixos:
            total_fixos = sum(cf["valor"] if cf["periodo"]=="mensal" else cf["valor"]/12 for cf in custos_fixos)
            for cf in custos_fixos:
                val_mes = cf["valor"] if cf["periodo"] == "mensal" else cf["valor"] / 12
                with st.expander(f"**{cf['nome']}** — R$ {val_mes:.2f}/mês"):
                    with st.form(f"edit_cf_{cf['id']}"):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        n_cf = c1.text_input("Nome", value=cf["nome"])
                        v_cf = c2.number_input("Valor (R$)", value=float(cf["valor"]), step=10.0)
                        p_cf = c3.selectbox("Período", ["mensal","anual"],
                                             index=0 if cf["periodo"]=="mensal" else 1,
                                             format_func=lambda x: "Mensal" if x=="mensal" else "Anual (÷12)")
                        col_s, col_d = st.columns([3, 1])
                        if col_s.form_submit_button("Salvar", type="primary", use_container_width=True):
                            atualizar_custo_fixo(cf["id"], n_cf, v_cf, p_cf)
                            st.success("Salvo.")
                            st.rerun()
                        if col_d.form_submit_button("Excluir", type="secondary", use_container_width=True):
                            deletar_custo_fixo(cf["id"])
                            st.rerun()

            st.markdown(f"""
            <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;
                        display:flex;justify-content:space-between;padding:0.75rem 1rem;margin-top:0.5rem;">
              <span style="color:#57534e;font-weight:600">Total / mês</span>
              <span style="font-family:'DM Mono',monospace;color:#ea580c">R$ {total_fixos:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:10px;padding:2rem;text-align:center;color:#a8a29e;font-size:0.9rem">Nenhum custo fixo cadastrado.</div>', unsafe_allow_html=True)

    with col_form:
        with st.form("form_cf"):
            st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e;margin-bottom:1rem">Adicionar</div>', unsafe_allow_html=True)
            nome_cf   = st.text_input("Nome", placeholder="ex: Aluguel, Internet, Shopee")
            valor_cf  = st.number_input("Valor (R$)", value=0.01, min_value=0.01, step=10.0)
            periodo_cf = st.selectbox("Período", ["mensal", "anual"],
                                       format_func=lambda x: "Mensal" if x == "mensal" else "Anual (÷12)")
            if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
                if nome_cf and valor_cf > 0:
                    inserir_custo_fixo(nome_cf, valor_cf, periodo_cf)
                    st.success(f"'{nome_cf}' adicionado.")
                    st.rerun()
                else:
                    st.error("Preencha nome e valor.")


secao_custos_fixos()
```

- [ ] **Step 2: Testar manualmente**

1. Abrir P&L
2. Adicionar custo fixo → confirmar que a lista atualiza no lugar, sem scroll reset
3. Editar custo fixo → expander permanece aberto

- [ ] **Step 3: Commit**

```bash
git add pages/04_PL.py
git commit -m "feat: PL page — fragment para custos fixos + Warm Neutral colors"
```

---

## Task 6: Produtos — 3 fragments + cores (tarefa mais extensa)

**Files:**
- Modify: `pages/02_Produtos.py`

- [ ] **Step 1: Substituir todo o conteúdo de 02_Produtos.py**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd


def parse_hhmm(s):
    s = s.strip()
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            try:
                h, m = int(parts[0]), int(parts[1])
                if 0 <= m < 60:
                    return h + m / 60
            except ValueError:
                pass
    else:
        try:
            return float(s)
        except ValueError:
            pass
    return None


def h_para_hhmm(h):
    horas = int(h)
    minutos = round((h - horas) * 60)
    if minutos == 60:
        horas += 1
        minutos = 0
    return f"{horas}:{minutos:02d}"


from db import (
    listar_impressoras, inserir_impressora, atualizar_impressora, deletar_impressora,
    listar_materiais, inserir_material, atualizar_material, deletar_material,
    listar_produtos, inserir_produto, atualizar_produto, deletar_produto,
    listar_custos_produto, inserir_custo_produto, atualizar_custo_produto, deletar_custo_produto,
    CATEGORIAS_CUSTO,
)
from calcular_custo import calcular_produto_completo
from styles import aplicar_css, secao, margem_cor

st.set_page_config(page_title="Produtos — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">PRINT LAB</div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Produtos</h1>
  <p style="color:#a8a29e;margin:0;font-size:0.95rem;">Catálogo completo com todos os custos por produto.</p>
</div>
""", unsafe_allow_html=True)

tab_prod, tab_mat, tab_imp = st.tabs(["📦  Produtos & Custos", "🧵  Materiais", "🖨️  Impressoras"])

# ══ IMPRESSORAS ═══════════════════════════════════════════════════════════════
with tab_imp:
    @st.fragment
    def secao_impressoras():
        impressoras = listar_impressoras()
        secao("Impressoras Cadastradas")

        if impressoras:
            for imp in impressoras:
                with st.expander(f"**{imp['nome']}** — {imp['consumo_watts']}W · R$ {imp['custo_aquisicao']:,.0f} · {imp['vida_util_horas']:.0f}h"):
                    with st.form(f"edit_imp_{imp['id']}"):
                        st.markdown('<span style="font-size:0.68rem;color:#ea580c;text-transform:uppercase;letter-spacing:0.1em">Editar</span>', unsafe_allow_html=True)
                        nome_i  = st.text_input("Nome", value=imp["nome"])
                        c1, c2, c3 = st.columns(3)
                        custo_i = c1.number_input("Custo aquisição (R$)", value=float(imp["custo_aquisicao"]), step=100.0)
                        vida_i  = c2.number_input("Vida útil (h)", value=float(imp["vida_util_horas"]), step=100.0)
                        watts_i = c3.number_input("Consumo (W)", value=float(imp["consumo_watts"]), step=10.0)
                        col_s, col_d = st.columns([3, 1])
                        if col_s.form_submit_button("Salvar alterações", type="primary", use_container_width=True):
                            atualizar_impressora(imp["id"], nome_i, custo_i, vida_i, watts_i)
                            st.success("Salvo.")
                            st.rerun()
                        if col_d.form_submit_button("Excluir", type="secondary", use_container_width=True):
                            deletar_impressora(imp["id"])
                            st.rerun()
        else:
            st.markdown('<div style="color:#a8a29e;font-size:0.9rem">Nenhuma impressora cadastrada ainda.</div>', unsafe_allow_html=True)

        st.divider()
        secao("Adicionar Impressora")
        with st.form("form_imp"):
            nome_i = st.text_input("Nome", placeholder="ex: Bambu Lab A1 Mini")
            c1, c2, c3 = st.columns(3)
            custo_aq = c1.number_input("Custo de aquisição (R$)", value=3000.0, step=100.0)
            vida_h   = c2.number_input("Vida útil (h)", value=5000.0, step=100.0)
            watts    = c3.number_input("Consumo (W)", value=250.0, step=10.0)
            if st.form_submit_button("Adicionar", type="primary"):
                if nome_i:
                    inserir_impressora(nome_i, custo_aq, vida_h, watts)
                    st.success(f"'{nome_i}' adicionada.")
                    st.rerun()
                else:
                    st.error("Informe o nome.")

    secao_impressoras()

# ══ MATERIAIS ═════════════════════════════════════════════════════════════════
with tab_mat:
    @st.fragment
    def secao_materiais():
        materiais = listar_materiais()
        secao("Materiais Cadastrados")

        if materiais:
            for mat in materiais:
                with st.expander(f"**{mat['nome']}** — {mat['tipo']} · R$ {mat['custo_por_kg']:.2f}/kg"):
                    with st.form(f"edit_mat_{mat['id']}"):
                        st.markdown('<span style="font-size:0.68rem;color:#ea580c;text-transform:uppercase;letter-spacing:0.1em">Editar</span>', unsafe_allow_html=True)
                        nome_m  = st.text_input("Nome", value=mat["nome"])
                        c1, c2 = st.columns(2)
                        tipo_m  = c1.selectbox("Tipo", ["filamento", "resina"],
                                                index=0 if mat["tipo"] == "filamento" else 1)
                        custo_m = c2.number_input("Custo/kg (R$)", value=float(mat["custo_por_kg"]), step=1.0)
                        col_s, col_d = st.columns([3, 1])
                        if col_s.form_submit_button("Salvar", type="primary", use_container_width=True):
                            atualizar_material(mat["id"], nome_m, tipo_m, custo_m)
                            st.success("Salvo.")
                            st.rerun()
                        if col_d.form_submit_button("Excluir", type="secondary", use_container_width=True):
                            deletar_material(mat["id"])
                            st.rerun()
        else:
            st.markdown('<div style="color:#a8a29e;font-size:0.9rem">Nenhum material cadastrado ainda.</div>', unsafe_allow_html=True)

        st.divider()
        secao("Adicionar Material")
        with st.form("form_mat"):
            nome_m   = st.text_input("Nome", placeholder="ex: PLA+ Branco, Resina UV Cinza")
            c1, c2   = st.columns(2)
            tipo_m   = c1.selectbox("Tipo", ["filamento", "resina"])
            custo_kg = c2.number_input("Custo/kg (R$)", value=80.0, step=1.0)
            if st.form_submit_button("Adicionar", type="primary"):
                if nome_m:
                    inserir_material(nome_m, tipo_m, custo_kg)
                    st.success(f"'{nome_m}' adicionado.")
                    st.rerun()
                else:
                    st.error("Informe o nome.")

    secao_materiais()

# ══ PRODUTOS ══════════════════════════════════════════════════════════════════
with tab_prod:
    @st.fragment
    def lista_e_cadastro_produtos():
        produtos    = listar_produtos()
        materiais   = listar_materiais()
        impressoras = listar_impressoras()

        secao("Catálogo")

        if produtos:
            for p in produtos:
                extras = listar_custos_produto(p["id"])
                calc   = calcular_produto_completo(p, custos_extras=extras)
                m      = calc["margem_bruta_pct"]
                cor    = margem_cor(m)

                with st.expander(f"**{p['nome']}** — R$ {p['preco_venda']:.2f} · Margem {m:.1f}%"):

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Custo 3D",      f"R$ {calc['custo_total'] - calc['total_adicionais']:.2f}")
                    c2.metric("Custos Extras",  f"R$ {calc['total_adicionais']:.2f}")
                    c3.metric("Custo Total",    f"R$ {calc['custo_total']:.2f}")
                    c4.metric("Margem Bruta",   f"{m:.1f}%", delta=f"Lucro R$ {calc['lucro_unitario']:.2f}")

                    st.markdown(f"""
                    <div style="margin:0.5rem 0 1.25rem;">
                      <div style="display:flex;align-items:center;gap:0.75rem;">
                        <span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.1em">Margem</span>
                        <div style="flex:1;background:#f5f5f4;border-radius:3px;height:5px;overflow:hidden;">
                          <div style="width:{min(100,m):.0f}%;height:100%;background:{cor};"></div>
                        </div>
                        <span style="font-family:'DM Mono',monospace;color:{cor};font-size:0.85rem">{m:.1f}%</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form(f"edit_prod_{p['id']}"):
                        st.markdown('<span style="font-size:0.68rem;color:#ea580c;text-transform:uppercase;letter-spacing:0.1em">Editar produto</span>', unsafe_allow_html=True)
                        nome_p = st.text_input("Nome", value=p["nome"])
                        c1, c2 = st.columns(2)
                        mat_id = c1.selectbox("Material", [m_["id"] for m_ in materiais],
                                              index=next((i for i, m_ in enumerate(materiais) if m_["id"] == p["material_id"]), 0),
                                              format_func=lambda x: next(m_["nome"] for m_ in materiais if m_["id"] == x))
                        imp_id = c2.selectbox("Impressora", [i_["id"] for i_ in impressoras],
                                              index=next((i for i, i_ in enumerate(impressoras) if i_["id"] == p["impressora_id"]), 0),
                                              format_func=lambda x: next(i_["nome"] for i_ in impressoras if i_["id"] == x))
                        c1, c2, c3 = st.columns(3)
                        peso_g        = c1.number_input("Peso (g)",            value=float(p["peso_material_g"]), step=1.0, key=f"pg_{p['id']}")
                        tempo_imp_str = c2.text_input("Tempo impressão (h:mm)", value=h_para_hhmm(p["tempo_impressao_h"]), key=f"ti_{p['id']}")
                        preco_v       = c3.number_input("Preço venda (R$)",    value=float(p["preco_venda"]), step=0.5, key=f"pv_{p['id']}")
                        c1, c2 = st.columns(2)
                        tempo_pos_str = c1.text_input("Pós-proc. (h:mm)", value=h_para_hhmm(p["tempo_pos_proc_h"]), key=f"tp_{p['id']}")
                        mob_h         = c2.number_input("Mão de obra (R$/h)", value=float(p["custo_mao_obra_h"]), step=1.0, key=f"mo_{p['id']}")
                        obs           = st.text_input("Observações", value=p.get("observacoes") or "", key=f"ob_{p['id']}")

                        col_s, col_d = st.columns([3, 1])
                        if col_s.form_submit_button("Salvar produto", type="primary", use_container_width=True):
                            tempo_imp = parse_hhmm(tempo_imp_str)
                            tempo_pos = parse_hhmm(tempo_pos_str)
                            if tempo_imp is None:
                                st.error("Tempo de impressão inválido. Use h:mm (ex: 2:30)")
                            elif tempo_pos is None:
                                st.error("Tempo de pós-proc. inválido. Use h:mm (ex: 0:30)")
                            else:
                                atualizar_produto(p["id"], nome_p, mat_id, imp_id, peso_g,
                                                  tempo_imp, tempo_pos, mob_h, preco_v, obs)
                                st.success("Produto atualizado.")
                                st.rerun()
                        if col_d.form_submit_button("Excluir produto", type="secondary", use_container_width=True):
                            deletar_produto(p["id"])
                            st.rerun()

                    st.divider()
                    st.markdown('<span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.1em">Custos Adicionais</span>', unsafe_allow_html=True)

                    if extras:
                        for e in extras:
                            with st.form(f"edit_extra_{e['id']}"):
                                ec1, ec2, ec3, ec4, ec5 = st.columns([2, 1.5, 1.2, 1, 0.8])
                                n_e    = ec1.text_input("Nome", value=e["nome"], key=f"en_{e['id']}", label_visibility="collapsed")
                                cat_e  = ec2.selectbox("Categoria", CATEGORIAS_CUSTO,
                                                       index=CATEGORIAS_CUSTO.index(e["categoria"]) if e["categoria"] in CATEGORIAS_CUSTO else 0,
                                                       key=f"ec_{e['id']}", label_visibility="collapsed",
                                                       format_func=lambda x: x.replace("_"," ").title())
                                tipo_e = ec3.selectbox("Tipo", ["fixo","percentual"],
                                                       index=0 if e["tipo"]=="fixo" else 1,
                                                       key=f"et_{e['id']}", label_visibility="collapsed",
                                                       format_func=lambda x: "R$/unit" if x=="fixo" else "% preço")
                                val_e  = ec4.number_input("Valor", value=float(e["valor"]), step=0.5,
                                                          key=f"ev_{e['id']}", label_visibility="collapsed")
                                col_s2, col_d2 = ec5.columns(2)
                                salvo   = col_s2.form_submit_button("✓", help="Salvar")
                                excluir = col_d2.form_submit_button("✕", help="Excluir")
                                if salvo:
                                    atualizar_custo_produto(e["id"], n_e, cat_e, tipo_e, val_e)
                                    st.success("Custo atualizado.")
                                    st.rerun()
                                if excluir:
                                    deletar_custo_produto(e["id"])
                                    st.rerun()
                    else:
                        st.markdown('<span style="color:#a8a29e;font-size:0.85rem">Nenhum custo adicional ainda.</span>', unsafe_allow_html=True)

                    with st.form(f"add_extra_{p['id']}"):
                        st.markdown('<span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">+ Novo custo adicional</span>', unsafe_allow_html=True)
                        fc1, fc2, fc3, fc4 = st.columns(4)
                        nome_e = fc1.text_input("Nome",     placeholder="ex: Caixa kraft", key=f"ne_{p['id']}")
                        cat_e  = fc2.selectbox("Categoria", CATEGORIAS_CUSTO,              key=f"cat_{p['id']}",
                                               format_func=lambda x: x.replace("_"," ").title())
                        tipo_e = fc3.selectbox("Tipo", ["fixo","percentual"],              key=f"tipo_{p['id']}",
                                               format_func=lambda x: "R$ fixo/unit" if x=="fixo" else "% do preço")
                        val_e  = fc4.number_input("Valor", value=0.0, min_value=0.0, step=0.5, key=f"val_{p['id']}")
                        if st.form_submit_button("Adicionar custo", type="primary"):
                            if nome_e and val_e > 0:
                                inserir_custo_produto(p["id"], nome_e, cat_e, tipo_e, val_e)
                                st.success(f"'{nome_e}' adicionado.")
                                st.rerun()
                            else:
                                st.error("Preencha nome e valor.")
        else:
            st.markdown('<div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:10px;padding:2rem;text-align:center;color:#a8a29e">Nenhum produto cadastrado ainda.</div>', unsafe_allow_html=True)

        st.divider()
        secao("Cadastrar Novo Produto")

        if not impressoras or not materiais:
            st.warning("Cadastre pelo menos uma **impressora** e um **material** antes de criar produtos.")
        else:
            with st.form("form_prod"):
                nome_p = st.text_input("Nome do produto", placeholder="ex: Suporte articulado P")
                st.markdown("**Impressão 3D**")
                c1, c2 = st.columns(2)
                mat_id = c1.selectbox("Material",   [m_["id"] for m_ in materiais],
                                       format_func=lambda x: next(m_["nome"] for m_ in materiais if m_["id"] == x))
                imp_id = c2.selectbox("Impressora", [i_["id"] for i_ in impressoras],
                                       format_func=lambda x: next(i_["nome"] for i_ in impressoras if i_["id"] == x))
                c1, c2, c3 = st.columns(3)
                peso_g        = c1.number_input("Peso (g)",            value=100.0, min_value=0.1, step=1.0)
                tempo_imp_str = c2.text_input("Tempo impressão (h:mm)", value="2:00", placeholder="ex: 1:30")
                preco_v       = c3.number_input("Preço de venda (R$)", value=25.0,  min_value=0.01, step=0.5)
                st.markdown("**Mão de obra**")
                c1, c2 = st.columns(2)
                tempo_pos_str = c1.text_input("Pós-proc. (h:mm)", value="0:00", placeholder="ex: 0:20")
                mob_h         = c2.number_input("Custo M.O. (R$/h)", value=15.0, step=1.0)
                obs = st.text_input("Observações (opcional)")
                if st.form_submit_button("Cadastrar produto", type="primary"):
                    tempo_imp = parse_hhmm(tempo_imp_str)
                    tempo_pos = parse_hhmm(tempo_pos_str)
                    if not nome_p:
                        st.error("Informe o nome.")
                    elif tempo_imp is None:
                        st.error("Tempo de impressão inválido. Use h:mm (ex: 2:30)")
                    elif tempo_pos is None:
                        st.error("Tempo de pós-proc. inválido. Use h:mm (ex: 0:20)")
                    else:
                        inserir_produto(nome_p, mat_id, imp_id, peso_g, tempo_imp,
                                        tempo_pos, mob_h, preco_v, obs)
                        st.success(f"'{nome_p}' cadastrado. Abra-o acima para adicionar custos extras.")
                        st.rerun()

    lista_e_cadastro_produtos()
```

- [ ] **Step 2: Testar manualmente**

1. Abrir página Produtos, aba "Produtos & Custos"
2. Abrir expander de um produto
3. Editar e salvar → expander permanece aberto, sem scroll pro topo
4. Adicionar produto → lista atualiza no lugar
5. Abrir aba Materiais, adicionar material → sem reset de página
6. Abrir aba Impressoras, adicionar impressora → sem reset de página

- [ ] **Step 3: Commit**

```bash
git add pages/02_Produtos.py
git commit -m "feat: produtos page — 3 fragments + Warm Neutral colors"
```

---

## Task 7: Calculadora — cores inline

**Files:**
- Modify: `pages/01_Calculadora.py`

- [ ] **Step 1: Substituir todo o conteúdo de 01_Calculadora.py**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st


def parse_hhmm(s):
    s = s.strip()
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            try:
                h, m = int(parts[0]), int(parts[1])
                if 0 <= m < 60:
                    return h + m / 60
            except ValueError:
                pass
    else:
        try:
            return float(s)
        except ValueError:
            pass
    return None


from db import listar_produtos, listar_materiais, listar_impressoras, listar_custos_produto
from calcular_custo import calcular_custo, calcular_margens, calcular_produto_completo
from styles import aplicar_css, secao, margem_cor, barra_margem, kpi_cards

st.set_page_config(page_title="Calculadora — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Calculadora</h1>
  <p style="color:#a8a29e;margin:0;font-size:0.95rem;">Simule o custo de qualquer impressão e descubra a margem real.</p>
</div>
""", unsafe_allow_html=True)

modo = st.radio("Modo", ["Produto cadastrado", "Cálculo avulso"], horizontal=True, label_visibility="collapsed")

tarifa = st.sidebar.number_input(
    "Tarifa energia (R$/kWh)",
    value=float(os.getenv("TARIFA_KWH", "0.85")),
    step=0.01, format="%.3f",
    help="Valor do kWh na sua conta de luz"
)
st.sidebar.markdown("---")
st.sidebar.markdown('<span style="color:#a8a29e;font-size:0.75rem">Altere a tarifa conforme sua conta de luz para cálculos precisos de energia.</span>', unsafe_allow_html=True)

st.markdown("---")

CAT_CORES = {
    "embalagem": "#1d4ed8", "frete": "#6d28d9",
    "taxa_plataforma": "#b45309", "imposto": "#b91c1c"
}

if modo == "Produto cadastrado":
    produtos = listar_produtos()
    if not produtos:
        st.warning("Nenhum produto cadastrado. Vá para **Produtos** e cadastre um produto primeiro.")
        st.stop()

    escolha = st.selectbox(
        "Selecione o produto",
        [p["id"] for p in produtos],
        format_func=lambda x: next(p["nome"] for p in produtos if p["id"] == x),
        label_visibility="collapsed",
    )
    produto = next(p for p in produtos if p["id"] == escolha)
    extras = listar_custos_produto(produto["id"])
    resultado = calcular_produto_completo(produto, tarifa_kwh=tarifa, custos_extras=extras)

    m = resultado["margem_bruta_pct"]
    cor = margem_cor(m)

    kpi_cards([
        {"label": "Custo Total",    "value": f"R$ {resultado['custo_total']:.2f}",    "delta": "por unidade", "delta_type": "neu"},
        {"label": "Preço de Venda", "value": f"R$ {produto['preco_venda']:.2f}",      "delta": "praticado", "delta_type": "neu"},
        {"label": "Lucro Unitário", "value": f"R$ {resultado['lucro_unitario']:.2f}",
         "delta": f"markup {resultado['markup_pct']:.0f}%",
         "delta_type": "pos" if resultado['lucro_unitario'] > 0 else "neg"},
        {"label": "Margem Bruta",   "value": f"{m:.1f}%",
         "delta": "≥50% excelente" if m >= 50 else ("≥30% aceitável" if m >= 30 else "< 30% atenção"),
         "delta_type": "pos" if m >= 50 else ("neu" if m >= 30 else "neg")},
    ])

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
      <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e;white-space:nowrap;">MARGEM</span>
      <div style="flex:1;background:#f5f5f4;border-radius:4px;height:8px;overflow:hidden;">
        <div style="width:{min(100,m):.0f}%;height:100%;background:{cor};border-radius:4px;transition:width 0.4s;"></div>
      </div>
      <span style="font-family:'DM Mono',monospace;color:{cor};font-size:0.9rem;white-space:nowrap;">{m:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    secao("Breakdown de custos")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Custos de Impressão 3D**")
        custo_3d = resultado['custo_total'] - resultado['total_adicionais']
        items_3d = [
            ("Material", resultado['custo_material']),
            ("Energia elétrica", resultado['custo_energia']),
            ("Depreciação impressora", resultado['custo_depreciacao']),
            ("Mão de obra", resultado['custo_mao_obra']),
        ]
        for nome, val in items_3d:
            pct_do_total = (val / resultado['custo_total'] * 100) if resultado['custo_total'] > 0 else 0
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.6rem 0;border-bottom:1px solid #e7e5e4;">
              <span style="color:#57534e;font-size:0.9rem">{nome}</span>
              <span style="font-family:'DM Mono',monospace;color:#1c1917">R$ {val:.2f}
                <span style="color:#a8a29e;font-size:0.75rem"> {pct_do_total:.0f}%</span>
              </span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:0.75rem 0;margin-top:0.25rem;">
          <span style="color:#78716c;font-size:0.85rem;font-weight:600">Subtotal 3D</span>
          <span style="font-family:'DM Mono',monospace;color:#ea580c;font-weight:500">R$ {custo_3d:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**Custos Adicionais**")
        adicionais = resultado.get("detalhes_adicionais", [])
        if adicionais:
            for i, a in enumerate(adicionais):
                extra_db = extras[i] if i < len(extras) else {}
                nome_e = extra_db.get("nome", a.get("nome", "—"))
                cat = extra_db.get("categoria", "outro")
                pct_do_total = (a['valor_calculado'] / resultado['custo_total'] * 100) if resultado['custo_total'] > 0 else 0
                cat_cor = CAT_CORES.get(cat, "#57534e")
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:0.6rem 0;border-bottom:1px solid #e7e5e4;">
                  <span style="color:#57534e;font-size:0.9rem">
                    <span style="color:{cat_cor};font-size:0.65rem;text-transform:uppercase;
                                 letter-spacing:0.08em;margin-right:6px">{cat.replace('_',' ')}</span>
                    {nome_e}
                  </span>
                  <span style="font-family:'DM Mono',monospace;color:#1c1917">R$ {a['valor_calculado']:.2f}
                    <span style="color:#a8a29e;font-size:0.75rem"> {pct_do_total:.0f}%</span>
                  </span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.75rem 0;margin-top:0.25rem;">
              <span style="color:#78716c;font-size:0.85rem;font-weight:600">Subtotal extras</span>
              <span style="font-family:'DM Mono',monospace;color:#ea580c;font-weight:500">R$ {resultado['total_adicionais']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#a8a29e;font-size:0.9rem;margin-top:1rem;">Nenhum custo adicional cadastrado para este produto.<br>Adicione em <b>Produtos</b>.</p>', unsafe_allow_html=True)

    secao("Dados técnicos")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e7e5e4;border-left:3px solid #ea580c;border-radius:8px;padding:1rem;">
      <div style="color:#a8a29e;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Material</div>
      <div style="color:#1c1917;margin-bottom:0.25rem">{produto['material_nome']}</div>
      <div style="font-family:'DM Mono',monospace;color:#ea580c">R$ {produto['custo_por_kg']:.2f}/kg</div>
      <div style="color:#a8a29e;font-size:0.8rem;margin-top:0.25rem">{produto['peso_material_g']} g consumidos</div>
    </div>
    """, unsafe_allow_html=True)
    col2.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e7e5e4;border-left:3px solid #ea580c;border-radius:8px;padding:1rem;">
      <div style="color:#a8a29e;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Impressora</div>
      <div style="color:#1c1917;margin-bottom:0.25rem">{produto['impressora_nome']}</div>
      <div style="font-family:'DM Mono',monospace;color:#ea580c">{produto['consumo_watts']} W</div>
      <div style="color:#a8a29e;font-size:0.8rem;margin-top:0.25rem">{produto['tempo_impressao_h']}h de impressão</div>
    </div>
    """, unsafe_allow_html=True)
    col3.markdown(f"""
    <div style="background:#ffffff;border:1px solid #e7e5e4;border-left:3px solid #ea580c;border-radius:8px;padding:1rem;">
      <div style="color:#a8a29e;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Mão de obra</div>
      <div style="font-family:'DM Mono',monospace;color:#ea580c">R$ {produto['custo_mao_obra_h']:.2f}/h</div>
      <div style="color:#a8a29e;font-size:0.8rem;margin-top:0.25rem">{produto['tempo_pos_proc_h']}h pós-processamento</div>
    </div>
    """, unsafe_allow_html=True)

else:
    materiais   = listar_materiais()
    impressoras = listar_impressoras()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        secao("Material")
        if materiais:
            mat_id = st.selectbox("Material cadastrado", [m["id"] for m in materiais],
                                   format_func=lambda x: next(m["nome"] for m in materiais if m["id"] == x))
            mat = next(m for m in materiais if m["id"] == mat_id)
            custo_por_kg = mat["custo_por_kg"]
            st.markdown(f'<span style="font-family:\'DM Mono\',monospace;color:#ea580c;font-size:0.85rem">R$ {custo_por_kg:.2f}/kg</span>', unsafe_allow_html=True)
        else:
            custo_por_kg = st.number_input("Custo do material (R$/kg)", value=80.0, step=1.0)

        peso_g      = st.number_input("Peso consumido (g)", value=100.0, min_value=0.1, step=1.0)
        preco_venda = st.number_input("Preço de venda (R$)", value=0.0, step=0.5,
                                       help="Preencha para ver margem e lucro")

    with col2:
        secao("Impressora")
        if impressoras:
            imp_id = st.selectbox("Impressora cadastrada", [i["id"] for i in impressoras],
                                   format_func=lambda x: next(i["nome"] for i in impressoras if i["id"] == x))
            imp = next(i for i in impressoras if i["id"] == imp_id)
            consumo_w, custo_aq, vida_h = imp["consumo_watts"], imp["custo_aquisicao"], imp["vida_util_horas"]
            st.markdown(f'<span style="font-family:\'DM Mono\',monospace;color:#ea580c;font-size:0.85rem">{consumo_w}W — R$ {custo_aq:,.0f} / {vida_h:.0f}h vida útil</span>', unsafe_allow_html=True)
        else:
            consumo_w = st.number_input("Consumo (W)", value=250.0, step=10.0)
            custo_aq  = st.number_input("Custo de aquisição (R$)", value=3000.0, step=100.0)
            vida_h    = st.number_input("Vida útil (h)", value=5000.0, step=100.0)

        tempo_h_str   = st.text_input("Tempo de impressão (h:mm)", value="2:00", placeholder="ex: 1:30")
        tempo_pos_str = st.text_input("Tempo pós-processamento (h:mm)", value="0:00", placeholder="ex: 0:20")
        mob_h         = st.number_input("Custo mão de obra (R$/h)", value=float(os.getenv("CUSTO_MOB_HORA", "15.0")), step=1.0)

    tempo_h   = parse_hhmm(tempo_h_str)
    tempo_pos = parse_hhmm(tempo_pos_str)

    if tempo_h is None:
        st.error("Tempo de impressão inválido. Use h:mm (ex: 2:30)")
        st.stop()
    if tempo_pos is None:
        st.error("Tempo de pós-processamento inválido. Use h:mm (ex: 0:20)")
        st.stop()

    resultado = calcular_custo(
        peso_material_g=peso_g, custo_por_kg=custo_por_kg,
        tempo_impressao_h=tempo_h, consumo_watts=consumo_w,
        custo_aquisicao=custo_aq, vida_util_horas=vida_h,
        tempo_pos_proc_h=tempo_pos, custo_mao_obra_h=mob_h,
        tarifa_kwh=tarifa,
    )

    st.markdown("---")
    secao("Resultado")

    itens_kpi = [
        {"label": "Material",    "value": f"R$ {resultado['custo_material']:.2f}",    "delta": f"{resultado['custo_material']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
        {"label": "Energia",     "value": f"R$ {resultado['custo_energia']:.2f}",     "delta": f"{resultado['custo_energia']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
        {"label": "Depreciação", "value": f"R$ {resultado['custo_depreciacao']:.2f}", "delta": f"{resultado['custo_depreciacao']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
        {"label": "Mão de Obra", "value": f"R$ {resultado['custo_mao_obra']:.2f}",   "delta": f"{resultado['custo_mao_obra']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
    ]
    kpi_cards(itens_kpi)

    st.markdown(f"""
    <div style="background:#fff7ed;border:1px solid #fed7aa;border-left:4px solid #ea580c;
                border-radius:10px;padding:1.25rem 1.5rem;display:flex;
                justify-content:space-between;align-items:center;margin-bottom:1rem;">
      <span style="color:#78716c;font-size:0.9rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em">Custo Total</span>
      <span style="font-family:'DM Mono',monospace;font-size:2rem;color:#1c1917">R$ {resultado['custo_total']:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    if preco_venda > 0:
        margens = calcular_margens(resultado["custo_total"], preco_venda)
        m   = margens["margem_bruta_pct"]
        cor = margem_cor(m)
        kpi_cards([
            {"label": "Lucro Unitário", "value": f"R$ {margens['lucro_unitario']:.2f}",
             "delta_type": "pos" if margens['lucro_unitario'] > 0 else "neg",
             "delta": "por peça vendida"},
            {"label": "Margem Bruta", "value": f"{m:.1f}%",
             "delta": "excelente" if m>=50 else ("aceitável" if m>=30 else "atenção"),
             "delta_type": "pos" if m>=50 else ("neu" if m>=30 else "neg")},
            {"label": "Markup", "value": f"{margens['markup_pct']:.1f}%",
             "delta": "sobre o custo", "delta_type": "neu"},
        ])
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;margin-top:0.5rem;">
          <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e">MARGEM</span>
          <div style="flex:1;background:#f5f5f4;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:{min(100,m):.0f}%;height:100%;background:{cor};border-radius:4px;"></div>
          </div>
          <span style="font-family:'DM Mono',monospace;color:{cor}">{m:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
```

- [ ] **Step 2: Verificar no browser**

Abrir Calculadora, testar modo "Produto cadastrado" e modo "Cálculo avulso". Confirmar textos legíveis no fundo claro.

- [ ] **Step 3: Commit**

```bash
git add pages/01_Calculadora.py
git commit -m "feat: calculadora page — Warm Neutral colors"
```

---

## Task 8: Dashboard — cores inline

**Files:**
- Modify: `pages/05_Dashboard.py`

- [ ] **Step 1: Substituir todo o conteúdo de 05_Dashboard.py**

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd
import calendar
from datetime import date
from calcular_margem import calcular_pl, ranking_produtos
from db import listar_vendas
from styles import aplicar_css, secao, kpi_cards, margem_cor

st.set_page_config(page_title="Dashboard — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

hoje = date.today()

if hoje.month > 1:
    ant_ini = date(hoje.year, hoje.month - 1, 1)
    ant_fim = date(hoje.year, hoje.month - 1, calendar.monthrange(hoje.year, hoje.month - 1)[1])
else:
    ant_ini = date(hoje.year - 1, 12, 1)
    ant_fim = date(hoje.year - 1, 12, 31)

data_ini = date(hoje.year, hoje.month, 1)
data_fim = hoje

pl     = calcular_pl(data_ini, data_fim)
pl_ant = calcular_pl(ant_ini, ant_fim)

meses_pt = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
mes_nome = meses_pt[hoje.month - 1]

st.markdown(f"""
<div style="margin-bottom:2rem;display:flex;justify-content:space-between;align-items:flex-end;">
  <div>
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">
      PRINT LAB
    </div>
    <h1 style="margin:0.25rem 0 0.25rem 0;">Dashboard</h1>
    <p style="color:#a8a29e;margin:0;font-size:0.9rem;">{mes_nome} {hoje.year} — atualizado hoje</p>
  </div>
  <div style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#a8a29e;text-align:right;">
    {data_ini.strftime('%d/%m')} → {data_fim.strftime('%d/%m/%Y')}
  </div>
</div>
""", unsafe_allow_html=True)


def delta_tipo(atual, anterior):
    return "pos" if atual >= anterior else "neg"


def fmt_delta(atual, anterior, prefixo="R$ "):
    diff = atual - anterior
    sinal = "+" if diff >= 0 else ""
    return f"{sinal}{prefixo}{diff:,.2f} vs {meses_pt[ant_ini.month-1]}"


ranking = ranking_produtos(data_ini, data_fim)
top_prod   = ranking[0]["produto"] if ranking else "—"
top_margem = ranking[0]["margem_pct"] if ranking else 0

kpi_cards([
    {"label": "Receita",      "value": f"R$ {pl['receita_total']:,.2f}",
     "delta": fmt_delta(pl['receita_total'], pl_ant['receita_total']),
     "delta_type": delta_tipo(pl['receita_total'], pl_ant['receita_total'])},
    {"label": "Lucro Bruto",  "value": f"R$ {pl['lucro_bruto']:,.2f}",
     "delta": f"{pl['margem_bruta_pct']:.1f}% margem",
     "delta_type": "pos" if pl['margem_bruta_pct'] >= 40 else "neg"},
    {"label": "Lucro Líquido","value": f"R$ {pl['lucro_liquido']:,.2f}",
     "delta": fmt_delta(pl['lucro_liquido'], pl_ant['lucro_liquido']),
     "delta_type": delta_tipo(pl['lucro_liquido'], pl_ant['lucro_liquido'])},
    {"label": "Top Produto",  "value": top_prod[:16] + ("…" if len(top_prod)>16 else ""),
     "delta": f"{top_margem:.1f}% margem", "delta_type": "pos"},
])

vendas = listar_vendas(data_ini, data_fim)

CANAL_CORES = {
    "Instagram": "#e1306c", "WhatsApp": "#16a34a", "Feira": "#ea580c",
    "Site": "#2563eb", "Indicação": "#7c3aed", "Outro": "#78716c",
}

if vendas:
    df = pd.DataFrame(vendas)
    df["total"] = df["preco_unit"] * df["quantidade"]
    df["data"]  = pd.to_datetime(df["data"])

    col1, col2 = st.columns([2, 1])

    with col1:
        secao("Receita por Dia")
        por_dia = df.groupby("data")["total"].sum().reset_index()
        por_dia.columns = ["Data", "Receita (R$)"]
        st.bar_chart(por_dia.set_index("Data"), height=220, color="#ea580c")

    with col2:
        secao("Por Canal")
        por_canal     = df.groupby("canal")["total"].sum().sort_values(ascending=False).reset_index()
        total_canais  = por_canal["total"].sum()

        st.markdown('<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
        for _, row in por_canal.iterrows():
            pct = row["total"] / total_canais * 100 if total_canais else 0
            cor = CANAL_CORES.get(row["canal"], "#78716c")
            st.markdown(f"""
            <div style="padding:0.65rem 1rem;border-bottom:1px solid #f5f5f4;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:{cor};font-size:0.85rem">{row['canal']}</span>
                <span style="font-family:'DM Mono',monospace;color:#57534e;font-size:0.85rem">R$ {row['total']:,.2f}</span>
              </div>
              <div style="background:#f5f5f4;border-radius:3px;height:3px;overflow:hidden;">
                <div style="width:{pct:.0f}%;height:100%;background:{cor};"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    secao("Produtos — Margem vs Receita")

    col1, col2 = st.columns([1.5, 1])

    with col1:
        if ranking:
            st.markdown('<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
            st.markdown("""
            <div style="display:grid;grid-template-columns:20px 1fr 70px 100px 90px;
                        padding:0.5rem 1rem;border-bottom:1px solid #e7e5e4;background:#f5f5f4;">
              <span style="font-size:0.62rem;color:#a8a29e">#</span>
              <span style="font-size:0.62rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">Produto</span>
              <span style="font-size:0.62rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:center">Qtd</span>
              <span style="font-size:0.62rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Receita</span>
              <span style="font-size:0.62rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Margem</span>
            </div>
            """, unsafe_allow_html=True)
            for i, r in enumerate(ranking):
                cor = margem_cor(r["margem_pct"])
                st.markdown(f"""
            <div style="display:grid;grid-template-columns:20px 1fr 70px 100px 90px;
                        padding:0.75rem 1rem;border-bottom:1px solid #f5f5f4;align-items:center;">
              <span style="font-family:'DM Mono',monospace;color:#a8a29e;font-size:0.72rem">{i+1}</span>
              <span style="color:#1c1917;font-size:0.9rem">{r['produto']}</span>
              <span style="font-family:'DM Mono',monospace;color:#78716c;text-align:center;font-size:0.85rem">{r['qtd_vendida']}</span>
              <span style="font-family:'DM Mono',monospace;color:#57534e;text-align:right;font-size:0.85rem">R$ {r['receita']:,.2f}</span>
              <div style="text-align:right;">
                <span style="font-family:'DM Mono',monospace;color:{cor};font-size:0.9rem">{r['margem_pct']:.1f}%</span>
                <div style="background:#f5f5f4;border-radius:2px;height:3px;margin-top:3px;">
                  <div style="width:{min(100,r['margem_pct']):.0f}%;height:100%;background:{cor};"></div>
                </div>
              </div>
            </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        secao("vs Mês Anterior")
        itens_comp = [
            ("Receita",       pl['receita_total'],      pl_ant['receita_total'],      "R$"),
            ("Lucro Bruto",   pl['lucro_bruto'],        pl_ant['lucro_bruto'],        "R$"),
            ("Margem Bruta",  pl['margem_bruta_pct'],   pl_ant['margem_bruta_pct'],   "%"),
            ("Lucro Líquido", pl['lucro_liquido'],      pl_ant['lucro_liquido'],      "R$"),
            ("M. Líquida",    pl['margem_liquida_pct'], pl_ant['margem_liquida_pct'], "%"),
        ]
        st.markdown('<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
        for nome, atual, anterior, unidade in itens_comp:
            diff = atual - anterior
            cor  = "#16a34a" if diff >= 0 else "#dc2626"
            sinal = "▲" if diff >= 0 else "▼"
            fmt = lambda v: f"R$ {v:,.2f}" if unidade == "R$" else f"{v:.1f}%"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.7rem 1rem;border-bottom:1px solid #f5f5f4;">
              <span style="color:#78716c;font-size:0.85rem">{nome}</span>
              <div style="text-align:right;">
                <div style="font-family:'DM Mono',monospace;color:#1c1917;font-size:0.9rem">{fmt(atual)}</div>
                <div style="font-family:'DM Mono',monospace;color:{cor};font-size:0.72rem">
                  {sinal} {fmt(abs(diff))}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:12px;
                padding:4rem;text-align:center;margin-top:1rem;">
      <div style="font-size:2rem;margin-bottom:1rem">📊</div>
      <div style="color:#a8a29e;font-size:1rem;margin-bottom:0.5rem">Nenhuma venda este mês.</div>
      <div style="color:#d6d3d1;font-size:0.85rem">Registre vendas na página <b style="color:#ea580c">Vendas</b> para ver os gráficos.</div>
    </div>
    """, unsafe_allow_html=True)
```

- [ ] **Step 2: Verificar no browser**

Abrir Dashboard e confirmar que KPIs, gráfico de barras, tabela de canais e comparativo mensal estão legíveis.

- [ ] **Step 3: Commit**

```bash
git add pages/05_Dashboard.py
git commit -m "feat: dashboard page — Warm Neutral colors"
```

---

## Checklist final de validação

- [ ] Nenhuma página tem fundo preto ou cinza escuro
- [ ] Cadastrar produto não rola página pro topo
- [ ] Expander de produto permanece aberto após salvar
- [ ] Cadastrar venda não rola página pro topo
- [ ] Adicionar custo fixo no P&L não rola página pro topo
- [ ] Todas as páginas carregam sem erros no console do Streamlit
