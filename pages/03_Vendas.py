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
    "Instagram": "#e1306c", "WhatsApp": "#25d366", "Feira": "#f97316",
    "Site": "#3b82f6", "Indicação": "#8b5cf6", "Outro": "#525252",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#f97316;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Vendas</h1>
  <p style="color:#525252;margin:0;font-size:0.95rem;">Registre cada venda e acompanhe o resultado por canal.</p>
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

# ── Formulário ────────────────────────────────────────────────────────────────
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
      <div style="font-size:0.68rem;color:#525252;text-transform:uppercase;letter-spacing:0.1em">Total</div>
      <div style="font-family:'DM Mono',monospace;color:#f97316;font-size:1.3rem">R$ {total_preview:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    submitted = st.form_submit_button("Registrar venda", type="primary", use_container_width=True)
    if submitted:
        inserir_venda(prod_id, data_v, qtd, preco_unit, canal)
        st.success(f"✓ Venda registrada: {qtd}× {produto_selecionado['nome']} — R$ {total_preview:.2f}")
        st.rerun()

st.markdown("---")

# ── Histórico ─────────────────────────────────────────────────────────────────
secao("Histórico de Vendas")

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

    # Tabela customizada
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin-bottom:0.75rem;">
      <span style="color:#737373;font-size:0.85rem">{len(vendas)} registro(s)</span>
      <span style="font-family:'DM Mono',monospace;color:#f97316;font-size:1.1rem">
        Total: R$ {receita:,.2f}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # Renderiza linhas manualmente
    st.markdown("""
    <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:10px;overflow:hidden;">
      <div style="display:grid;grid-template-columns:90px 1fr 100px 60px 100px 100px;
                  padding:0.6rem 1rem;border-bottom:1px solid #1e1e1e;">
        <span style="font-size:0.68rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em">Data</span>
        <span style="font-size:0.68rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em">Produto</span>
        <span style="font-size:0.68rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em">Canal</span>
        <span style="font-size:0.68rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:center">Qtd</span>
        <span style="font-size:0.68rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Unit</span>
        <span style="font-size:0.68rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Total</span>
      </div>
    """, unsafe_allow_html=True)

    for v in vendas:
        total_linha = v["preco_unit"] * v["quantidade"]
        cor_canal = CANAL_CORES.get(v.get("canal", ""), "#525252")
        st.markdown(f"""
      <div style="display:grid;grid-template-columns:90px 1fr 100px 60px 100px 100px;
                  padding:0.75rem 1rem;border-bottom:1px solid #111;align-items:center;">
        <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#525252">{v['data']}</span>
        <span style="color:#e5e5e5;font-size:0.9rem">{v['produto_nome']}</span>
        <span style="font-size:0.75rem;padding:2px 8px;border-radius:4px;
                     background:rgba(255,255,255,0.04);color:{cor_canal};border:1px solid {cor_canal}33">
          {v.get('canal','—')}
        </span>
        <span style="font-family:'DM Mono',monospace;color:#a3a3a3;text-align:center">{v['quantidade']}</span>
        <span style="font-family:'DM Mono',monospace;color:#a3a3a3;text-align:right;font-size:0.85rem">R$ {v['preco_unit']:.2f}</span>
        <span style="font-family:'DM Mono',monospace;color:#ffffff;text-align:right">R$ {total_linha:.2f}</span>
      </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Remover
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
    <div style="background:#0d0d0d;border:1px dashed #2a2a2a;border-radius:10px;
                padding:2.5rem;text-align:center;">
      <div style="color:#404040;font-size:0.9rem">Nenhuma venda no período selecionado.</div>
    </div>
    """, unsafe_allow_html=True)
