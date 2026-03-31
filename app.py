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
