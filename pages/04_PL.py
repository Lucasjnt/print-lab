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
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#f97316;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">P&L</h1>
  <p style="color:#525252;margin:0;font-size:0.95rem;">Demonstrativo de resultado completo por período.</p>
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

dre_itens = [
    {"label": "(+) Receita Bruta",  "valor": pl["receita_total"],    "pct": 100.0,              "cor": "#ffffff", "destaque": False},
    {"label": "(−) CMV",            "valor": -pl["cmv_total"],       "pct": -pl["cmv_total"]/pl["receita_total"]*100 if pl["receita_total"] else 0, "cor": "#f87171", "destaque": False},
    {"label": "(=) Lucro Bruto",    "valor": pl["lucro_bruto"],      "pct": pl["margem_bruta_pct"],  "cor": "#4ade80" if pl["margem_bruta_pct"]>=40 else "#facc15", "destaque": True},
    {"label": "(−) Custos Fixos",   "valor": -pl["custos_fixos_mes"],"pct": -pl["custos_fixos_mes"]/pl["receita_total"]*100 if pl["receita_total"] else 0, "cor": "#f87171", "destaque": False},
    {"label": "(=) Lucro Líquido",  "valor": pl["lucro_liquido"],    "pct": pl["margem_liquida_pct"],"cor": "#4ade80" if pl["margem_liquida_pct"]>=20 else "#f87171", "destaque": True},
]

for item in dre_itens:
    bg = "#111" if item["destaque"] else "#0d0d0d"
    border = "2px solid #1e1e1e" if item["destaque"] else "1px solid #141414"
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 140px 90px;align-items:center;
                background:{bg};border:{border};border-radius:8px;
                padding:0.85rem 1.25rem;margin-bottom:4px;">
      <span style="color:{'#e5e5e5' if item['destaque'] else '#a3a3a3'};
                   font-weight:{'600' if item['destaque'] else '400'}">
        {item['label']}
      </span>
      <span style="font-family:'DM Mono',monospace;color:{item['cor']};
                   text-align:right;font-size:{'1.05rem' if item['destaque'] else '0.95rem'}">
        R$ {item['valor']:,.2f}
      </span>
      <span style="font-family:'DM Mono',monospace;color:#404040;text-align:right;font-size:0.8rem">
        {item['pct']:.1f}%
      </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Ranking de produtos ───────────────────────────────────────────────────────
secao("Ranking de Produtos por Margem")

if ranking:
    st.markdown("""
    <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:10px;overflow:hidden;">
      <div style="display:grid;grid-template-columns:24px 1fr 80px 100px 90px 100px;
                  padding:0.6rem 1rem;border-bottom:1px solid #1e1e1e;">
        <span style="font-size:0.65rem;color:#404040">#</span>
        <span style="font-size:0.65rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em">Produto</span>
        <span style="font-size:0.65rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:center">Qtd</span>
        <span style="font-size:0.65rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Receita</span>
        <span style="font-size:0.65rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Lucro</span>
        <span style="font-size:0.65rem;color:#404040;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Margem</span>
      </div>
    """, unsafe_allow_html=True)

    for i, r in enumerate(ranking):
        cor = margem_cor(r["margem_pct"])
        largura = min(100, r["margem_pct"])
        st.markdown(f"""
      <div style="display:grid;grid-template-columns:24px 1fr 80px 100px 90px 100px;
                  padding:0.85rem 1rem;border-bottom:1px solid #111;align-items:center;">
        <span style="font-family:'DM Mono',monospace;color:#404040;font-size:0.75rem">{i+1:02d}</span>
        <span style="color:#e5e5e5">{r['produto']}</span>
        <span style="font-family:'DM Mono',monospace;color:#737373;text-align:center">{r['qtd_vendida']}</span>
        <span style="font-family:'DM Mono',monospace;color:#a3a3a3;text-align:right;font-size:0.85rem">R$ {r['receita']:,.2f}</span>
        <span style="font-family:'DM Mono',monospace;color:#4ade80;text-align:right">R$ {r['lucro']:,.2f}</span>
        <div style="text-align:right;">
          <span style="font-family:'DM Mono',monospace;color:{cor}">{r['margem_pct']:.1f}%</span>
          <div style="background:#1a1a1a;border-radius:3px;height:3px;margin-top:4px;overflow:hidden;">
            <div style="width:{largura:.0f}%;height:100%;background:{cor};"></div>
          </div>
        </div>
      </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown('<p style="color:#404040">Nenhuma venda no período.</p>', unsafe_allow_html=True)

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
                    n_cf  = c1.text_input("Nome", value=cf["nome"])
                    v_cf  = c2.number_input("Valor (R$)", value=float(cf["valor"]), step=10.0)
                    p_cf  = c3.selectbox("Período", ["mensal","anual"],
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
        <div style="background:#111;border:1px solid #1e1e1e;border-radius:8px;
                    display:flex;justify-content:space-between;padding:0.75rem 1rem;margin-top:0.5rem;">
          <span style="color:#737373;font-weight:600">Total / mês</span>
          <span style="font-family:'DM Mono',monospace;color:#ffffff">R$ {total_fixos:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#0d0d0d;border:1px dashed #2a2a2a;border-radius:10px;padding:2rem;text-align:center;color:#404040;font-size:0.9rem">Nenhum custo fixo cadastrado.</div>', unsafe_allow_html=True)

with col_form:
    with st.form("form_cf"):
        st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#737373;margin-bottom:1rem">Adicionar</div>', unsafe_allow_html=True)
        nome_cf  = st.text_input("Nome", placeholder="ex: Aluguel, Internet, Shopee")
        valor_cf = st.number_input("Valor (R$)", value=0.0, min_value=0.01, step=10.0)
        periodo_cf = st.selectbox("Período", ["mensal", "anual"],
                                   format_func=lambda x: "Mensal" if x == "mensal" else "Anual (÷12)")
        if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
            if nome_cf and valor_cf > 0:
                inserir_custo_fixo(nome_cf, valor_cf, periodo_cf)
                st.success(f"'{nome_cf}' adicionado.")
                st.rerun()
            else:
                st.error("Preencha nome e valor.")
