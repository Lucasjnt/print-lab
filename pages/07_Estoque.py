import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
from db import listar_materiais, listar_estoque, upsert_estoque, init_db
from styles import aplicar_css, secao, kpi_cards, sidebar_nav

st.set_page_config(page_title="Estoque — Print Lab", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
aplicar_css()
init_db()
sidebar_nav("estoque")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">PRINT LAB</div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Estoque de Materiais</h1>
  <p style="color:#a8a29e;margin:0;font-size:0.95rem;">Controle de filamentos e resinas disponíveis.</p>
</div>
""", unsafe_allow_html=True)

materiais = listar_materiais()
estoque   = listar_estoque()

# índice rápido por material_id
est_idx = {e["material_id"]: e for e in estoque}

# KPIs
total_kg   = sum(e["quantidade_kg"] for e in estoque)
alertas    = sum(1 for e in estoque if e["quantidade_kg"] <= e["quantidade_minima_kg"])
valor_est  = sum(e["quantidade_kg"] * e["custo_por_kg"] for e in estoque)
materiais_c = len(materiais)

kpi_cards([
    {"label": "Total em Estoque", "value": f"{total_kg:.2f} kg",
     "delta": f"{materiais_c} materiais cadastrados", "delta_type": "neu"},
    {"label": "Valor do Estoque", "value": f"R$ {valor_est:,.2f}",
     "delta": "custo total do estoque atual", "delta_type": "neu"},
    {"label": "Alertas de Estoque Baixo", "value": str(alertas),
     "delta": "abaixo do mínimo" if alertas else "tudo em ordem",
     "delta_type": "neg" if alertas else "pos"},
    {"label": "Materiais", "value": str(materiais_c),
     "delta": "cadastre mais em Produtos", "delta_type": "neu"},
])

if not materiais:
    st.markdown("""
    <div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:12px;
                padding:4rem;text-align:center;margin-top:1rem;">
      <div style="font-size:2rem;margin-bottom:1rem">📦</div>
      <div style="color:#a8a29e;font-size:1rem">Nenhum material cadastrado.</div>
      <div style="color:#d6d3d1;font-size:0.85rem;margin-top:0.5rem">Cadastre materiais na página <b style="color:#ea580c">Produtos</b> primeiro.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

secao("Estoque por Material")

cols = st.columns(3)
for idx, mat in enumerate(materiais):
    est = est_idx.get(mat["id"])
    qtd_atual = est["quantidade_kg"] if est else 0.0
    qtd_min   = est["quantidade_minima_kg"] if est else 0.5
    valor_mat = qtd_atual * mat["custo_por_kg"]
    alerta    = qtd_atual <= qtd_min

    cor_status = "#dc2626" if alerta else ("#d97706" if qtd_atual <= qtd_min * 2 else "#16a34a")
    label_status = "⚠ Estoque baixo" if alerta else ("⚡ Atenção" if qtd_atual <= qtd_min * 2 else "✓ OK")
    bar_pct = min(100, (qtd_atual / max(qtd_min * 3, 0.01)) * 100)

    with cols[idx % 3]:
        st.markdown(
            f'<div style="background:#ffffff;border:1px solid {"#fecaca" if alerta else "#e7e5e4"};'
            f'border-radius:12px;padding:1.25rem;margin-bottom:1rem;'
            f'border-left:4px solid {cor_status};">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem;">'
            f'<div>'
            f'<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e;">'
            f'{mat["tipo"].upper()}</div>'
            f'<div style="font-size:1rem;font-weight:600;color:#1c1917;margin-top:2px">{mat["nome"]}</div>'
            f'</div>'
            f'<span style="color:{cor_status};font-size:0.75rem;font-weight:500">{label_status}</span>'
            f'</div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:1.6rem;color:{cor_status};margin-bottom:4px">'
            f'{qtd_atual:.2f} kg</div>'
            f'<div style="background:#f5f5f4;border-radius:3px;height:4px;margin-bottom:0.75rem;overflow:hidden;">'
            f'<div style="width:{bar_pct:.0f}%;height:100%;background:{cor_status};"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#78716c;">'
            f'<span>Mín: {qtd_min:.2f} kg</span>'
            f'<span style="font-family:\'DM Mono\',monospace">R$ {mat["custo_por_kg"]:.2f}/kg</span>'
            f'</div>'
            f'<div style="font-size:0.78rem;color:#a8a29e;margin-top:2px">Valor: R$ {valor_mat:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        with st.expander("Atualizar estoque"):
            with st.form(f"form_est_{mat['id']}"):
                c1, c2 = st.columns(2)
                nova_qtd = c1.number_input("Quantidade (kg)", value=float(qtd_atual), min_value=0.0, step=0.1, key=f"qtd_{mat['id']}")
                nova_min = c2.number_input("Mínimo (kg)", value=float(qtd_min), min_value=0.0, step=0.1, key=f"min_{mat['id']}")
                if st.form_submit_button("Salvar", type="primary", use_container_width=True):
                    upsert_estoque(mat["id"], nova_qtd, nova_min)
                    st.success("Atualizado.")
                    st.rerun()

# Alertas consolidados
alertas_list = [e for e in estoque if e["quantidade_kg"] <= e["quantidade_minima_kg"]]
if alertas_list:
    st.markdown("---")
    secao("Alertas — Comprar Agora")
    st.markdown('<div style="background:#ffffff;border:1px solid #fecaca;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
    for e in alertas_list:
        falta = max(0, e["quantidade_minima_kg"] * 3 - e["quantidade_kg"])
        custo_reposicao = falta * e["custo_por_kg"]
        st.markdown(
            f'<div style="display:grid;grid-template-columns:1fr 120px 120px 130px;'
            f'padding:0.75rem 1rem;border-bottom:1px solid #fef2f2;align-items:center;">'
            f'<div><div style="color:#1c1917;font-weight:500">{e["material_nome"]}</div>'
            f'<div style="font-size:0.75rem;color:#a8a29e">{e["material_tipo"]}</div></div>'
            f'<div><div style="font-size:0.65rem;color:#a8a29e">ATUAL</div>'
            f'<div style="font-family:\'DM Mono\',monospace;color:#dc2626">{e["quantidade_kg"]:.2f} kg</div></div>'
            f'<div><div style="font-size:0.65rem;color:#a8a29e">SUGERIDO COMPRAR</div>'
            f'<div style="font-family:\'DM Mono\',monospace;color:#78716c">{falta:.2f} kg</div></div>'
            f'<div><div style="font-size:0.65rem;color:#a8a29e">CUSTO ESTIMADO</div>'
            f'<div style="font-family:\'DM Mono\',monospace;color:#ea580c">R$ {custo_reposicao:.2f}</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
