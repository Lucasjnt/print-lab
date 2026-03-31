import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd
from datetime import date
from db import (listar_fluxo_caixa, inserir_fluxo_caixa, deletar_fluxo_caixa,
                CATEGORIAS_FLUXO_ENTRADA, CATEGORIAS_FLUXO_SAIDA, init_db)
from styles import aplicar_css, secao, kpi_cards, sidebar_nav

st.set_page_config(page_title="Fluxo de Caixa — Print Lab", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
aplicar_css()
init_db()
sidebar_nav("fluxo")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">PRINT LAB</div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Fluxo de Caixa</h1>
  <p style="color:#a8a29e;margin:0;font-size:0.95rem;">Entradas e saídas reais de dinheiro no período.</p>
</div>
""", unsafe_allow_html=True)

# ── Filtro ────────────────────────────────────────────────────────────────────
hoje = date.today()
col1, col2, _ = st.columns([1, 1, 2])
data_ini = col1.date_input("De", value=date(hoje.year, hoje.month, 1))
data_fim = col2.date_input("Até", value=hoje)

movs = listar_fluxo_caixa(data_ini, data_fim)
entradas = sum(m["valor"] for m in movs if m["tipo"] == "entrada")
saidas   = sum(m["valor"] for m in movs if m["tipo"] == "saida")
saldo    = entradas - saidas

# ── KPIs ──────────────────────────────────────────────────────────────────────
kpi_cards([
    {"label": "Saldo do Período", "value": f"R$ {saldo:,.2f}",
     "delta": "positivo" if saldo >= 0 else "negativo",
     "delta_type": "pos" if saldo >= 0 else "neg"},
    {"label": "Total Entradas", "value": f"R$ {entradas:,.2f}",
     "delta": f"{sum(1 for m in movs if m['tipo']=='entrada')} lançamentos", "delta_type": "pos"},
    {"label": "Total Saídas", "value": f"R$ {saidas:,.2f}",
     "delta": f"{sum(1 for m in movs if m['tipo']=='saida')} lançamentos", "delta_type": "neg"},
    {"label": "Transações", "value": str(len(movs)),
     "delta": f"{data_ini.strftime('%d/%m')} → {data_fim.strftime('%d/%m')}", "delta_type": "neu"},
])

col_lista, col_form = st.columns([2, 1])

with col_form:
    secao("Novo Lançamento")
    with st.form("form_fluxo", clear_on_submit=True):
        tipo_mov = st.radio("Tipo", ["entrada", "saida"],
                            format_func=lambda x: "✚ Entrada" if x == "entrada" else "✖ Saída",
                            horizontal=True)
        data_mov = st.date_input("Data", value=hoje)
        cats = CATEGORIAS_FLUXO_ENTRADA if tipo_mov == "entrada" else CATEGORIAS_FLUXO_SAIDA
        cat_mov = st.selectbox("Categoria", cats)
        desc_mov = st.text_input("Descrição", placeholder="ex: Venda Shopee, Filamento PLA 1kg")
        val_mov = st.number_input("Valor (R$)", min_value=0.01, value=10.0, step=1.0)
        impacta_pl = st.checkbox(
            "Incluir no P&L deste período",
            help="Marque para que esta saída apareça como despesa no DRE (ex: compra de material, campanha de marketing)"
        )
        if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
            if tipo_mov == "entrada":
                impacta_pl = False
            inserir_fluxo_caixa(data_mov, tipo_mov, cat_mov, desc_mov, val_mov, impacta_pl)
            st.success("Lançamento adicionado.")
            st.rerun()

with col_lista:
    secao("Movimentações")

    if movs:
        df = pd.DataFrame(movs)
        df["data"] = pd.to_datetime(df["data"])

        # Gráfico saldo acumulado
        secao("Saldo Acumulado por Dia")
        por_dia = df.copy()
        por_dia["valor_signed"] = por_dia.apply(lambda r: r["valor"] if r["tipo"]=="entrada" else -r["valor"], axis=1)
        saldo_dia = por_dia.groupby("data")["valor_signed"].sum().sort_index().cumsum().reset_index()
        saldo_dia.columns = ["Data", "Saldo (R$)"]
        st.line_chart(saldo_dia.set_index("Data"), height=180, color="#ea580c")

        # Projeção 30 dias
        dias_periodo = max(1, (data_fim - data_ini).days + 1)
        saldo_medio_dia = saldo / dias_periodo
        projecao_30 = saldo + saldo_medio_dia * 30
        cor_proj = "#16a34a" if projecao_30 >= 0 else "#dc2626"
        sinal_proj = "+" if saldo_medio_dia >= 0 else ""
        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;'
            f'padding:0.9rem 1.25rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;">'
            f'<div><div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e">Projeção +30 dias</div>'
            f'<div style="font-size:0.75rem;color:#78716c;margin-top:2px">Média diária: {sinal_proj}R$ {saldo_medio_dia:,.2f}/dia</div></div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:1.4rem;color:{cor_proj}">R$ {projecao_30:,.2f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        secao("Lançamentos")
        st.markdown('<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
        st.markdown(
            '<div style="display:grid;grid-template-columns:80px 80px 1fr 120px 110px 40px;'
            'padding:0.5rem 1rem;border-bottom:1px solid #e7e5e4;background:#f5f5f4;">'
            '<span style="font-size:0.62rem;color:#a8a29e">DATA</span>'
            '<span style="font-size:0.62rem;color:#a8a29e">TIPO</span>'
            '<span style="font-size:0.62rem;color:#a8a29e">DESCRIÇÃO</span>'
            '<span style="font-size:0.62rem;color:#a8a29e">CATEGORIA</span>'
            '<span style="font-size:0.62rem;color:#a8a29e;text-align:right">VALOR</span>'
            '<span></span>'
            '</div>',
            unsafe_allow_html=True
        )
        for m in movs:
            cor_tipo = "#16a34a" if m["tipo"] == "entrada" else "#dc2626"
            sinal_v  = "+" if m["tipo"] == "entrada" else "−"
            label_tipo = "↑ Entrada" if m["tipo"] == "entrada" else "↓ Saída"
            desc = (m["descricao"] or "—")[:30]
            data_fmt = str(m["data"])[5:] if len(str(m["data"])) >= 7 else str(m["data"])
            badge_pl = '<span style="background:#fff7ed;color:#ea580c;border:1px solid #fed7aa;border-radius:4px;font-size:0.65rem;padding:1px 5px;font-family:\'DM Mono\',monospace;">P&L</span>' if m.get("impacta_pl") else ""
            st.markdown(
                f'<div style="display:grid;grid-template-columns:80px 80px 1fr 100px 30px 110px 40px;'
                f'padding:0.65rem 1rem;border-bottom:1px solid #f5f5f4;align-items:center;">'
                f'<span style="font-family:\'DM Mono\',monospace;color:#78716c;font-size:0.8rem">{data_fmt}</span>'
                f'<span style="color:{cor_tipo};font-size:0.78rem;font-weight:500">{label_tipo}</span>'
                f'<span style="color:#1c1917;font-size:0.85rem">{desc}</span>'
                f'<span style="color:#78716c;font-size:0.78rem">{m["categoria"]}</span>'
                f'{badge_pl}'
                f'<span style="font-family:\'DM Mono\',monospace;color:{cor_tipo};text-align:right;font-size:0.9rem">'
                f'{sinal_v} R$ {m["valor"]:,.2f}</span>'
                f'<span></span>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button("✕", key=f"del_fc_{m['id']}", help="Excluir"):
                deletar_fluxo_caixa(m["id"])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:12px;
                    padding:4rem;text-align:center;margin-top:1rem;">
          <div style="font-size:2rem;margin-bottom:1rem">💳</div>
          <div style="color:#a8a29e;font-size:1rem">Nenhum lançamento no período.</div>
          <div style="color:#d6d3d1;font-size:0.85rem;margin-top:0.5rem">Use o formulário ao lado para adicionar entradas e saídas.</div>
        </div>
        """, unsafe_allow_html=True)
