import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd
from datetime import date
from db import listar_custos_fixos, inserir_custo_fixo, atualizar_custo_fixo, deletar_custo_fixo
from calcular_margem import calcular_pl, ranking_produtos
from relatorios import pl_para_csv, ranking_para_csv
from styles import aplicar_css, secao, kpi_cards, margem_cor, sidebar_nav

st.set_page_config(page_title="P&L — Print Lab", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
aplicar_css()
sidebar_nav("pl")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#ea580c;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">P&L — DRE</h1>
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
secao("Demonstrativo de Resultado (DRE)")

rec = pl["receita_total"]
cor_bruto = "#16a34a" if pl["margem_bruta_pct"] >= 40 else "#d97706"
cor_liq   = "#16a34a" if pl["margem_liquida_pct"] >= 20 else "#dc2626"

def pct_rec(v):
    return (v / rec * 100) if rec else 0

def dre_row(label, valor, pct, cor, destaque=False, subitem=False):
    bg     = "#fff7ed" if destaque else ("#fafaf9" if subitem else "#ffffff")
    border = "1px solid #fed7aa" if destaque else "1px solid #e7e5e4"
    indent = "padding-left:2rem;" if subitem else ""
    fw     = "600" if destaque else ("400" if subitem else "500")
    fsize  = "1.05rem" if destaque else ("0.85rem" if subitem else "0.95rem")
    vcor   = cor if valor != 0 else "#a8a29e"
    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 140px 90px;align-items:center;'
        f'background:{bg};border:{border};border-radius:8px;padding:0.75rem 1.25rem;margin-bottom:4px;">'
        f'<span style="color:#57534e;font-weight:{fw};font-size:{fsize};{indent}">{label}</span>'
        f'<span style="font-family:\'DM Mono\',monospace;color:{vcor};text-align:right;font-size:{fsize}">'
        f'R$ {valor:,.2f}</span>'
        f'<span style="font-family:\'DM Mono\',monospace;color:#a8a29e;text-align:right;font-size:0.8rem">'
        f'{pct:.1f}%</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# Receita Bruta
dre_row("(+) Receita Bruta", pl["receita_total"], 100.0, "#1c1917", destaque=False)

# Deduções (taxa plataforma + imposto)
if pl["deducoes"] > 0:
    dre_row("(−) Taxas de Plataforma", -pl["custo_taxa_plataforma"], -pct_rec(pl["custo_taxa_plataforma"]), "#dc2626", subitem=True)
    dre_row("(−) Impostos / Taxas", -pl["custo_imposto"], -pct_rec(pl["custo_imposto"]), "#dc2626", subitem=True)
    dre_row("(=) Receita Líquida", pl["receita_liquida"], pct_rec(pl["receita_liquida"]), "#78716c", destaque=True)

# CMV detalhado
dre_row("(−) Custo de Produção", -pl["custo_producao_total"], -pct_rec(pl["custo_producao_total"]), "#dc2626", subitem=True)
if pl["custo_embalagem"] > 0:
    dre_row("(−) Embalagem", -pl["custo_embalagem"], -pct_rec(pl["custo_embalagem"]), "#dc2626", subitem=True)
if pl["custo_frete"] > 0:
    dre_row("(−) Frete", -pl["custo_frete"], -pct_rec(pl["custo_frete"]), "#dc2626", subitem=True)
if pl["custo_outro"] > 0:
    dre_row("(−) Outros CMV", -pl["custo_outro"], -pct_rec(pl["custo_outro"]), "#dc2626", subitem=True)

dre_row("(=) Lucro Bruto", pl["lucro_bruto"], pl["margem_bruta_pct"], cor_bruto, destaque=True)

# Despesas Operacionais
dre_row("(−) Custos Fixos Operacionais", -pl["custos_fixos_mes"], -pct_rec(pl["custos_fixos_mes"]), "#dc2626", subitem=True)
if pl.get("despesas_esporadicas", 0) > 0:
    dre_row("(−) Despesas Esporádicas", -pl["despesas_esporadicas"], -pct_rec(pl["despesas_esporadicas"]), "#dc2626", subitem=True)

dre_row("(=) Lucro Líquido (EBIT)", pl["lucro_liquido"], pl["margem_liquida_pct"], cor_liq, destaque=True)

st.markdown("---")

# ── Ranking de produtos ───────────────────────────────────────────────────────
col_rank, col_cat = st.columns([1.5, 1])

with col_rank:
    secao("Ranking de Produtos por Margem")
    if ranking:
        st.markdown('<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
        st.markdown(
            '<div style="display:grid;grid-template-columns:24px 1fr 80px 100px 90px 100px;'
            'padding:0.6rem 1rem;border-bottom:1px solid #e7e5e4;background:#f5f5f4;">'
            '<span style="font-size:0.65rem;color:#a8a29e">#</span>'
            '<span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em">Produto</span>'
            '<span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:center">Qtd</span>'
            '<span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Receita</span>'
            '<span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Lucro</span>'
            '<span style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.08em;text-align:right">Margem</span>'
            '</div>',
            unsafe_allow_html=True
        )
        for i, r in enumerate(ranking):
            cor = margem_cor(r["margem_pct"])
            largura = min(100, r["margem_pct"])
            st.markdown(
                f'<div style="display:grid;grid-template-columns:24px 1fr 80px 100px 90px 100px;'
                f'padding:0.85rem 1rem;border-bottom:1px solid #f5f5f4;align-items:center;">'
                f'<span style="font-family:\'DM Mono\',monospace;color:#a8a29e;font-size:0.75rem">{i+1:02d}</span>'
                f'<span style="color:#1c1917">{r["produto"]}</span>'
                f'<span style="font-family:\'DM Mono\',monospace;color:#78716c;text-align:center">{r["qtd_vendida"]}</span>'
                f'<span style="font-family:\'DM Mono\',monospace;color:#57534e;text-align:right;font-size:0.85rem">R$ {r["receita"]:,.2f}</span>'
                f'<span style="font-family:\'DM Mono\',monospace;color:#16a34a;text-align:right">R$ {r["lucro"]:,.2f}</span>'
                f'<div style="text-align:right;">'
                f'<span style="font-family:\'DM Mono\',monospace;color:{cor}">{r["margem_pct"]:.1f}%</span>'
                f'<div style="background:#f5f5f4;border-radius:3px;height:3px;margin-top:4px;overflow:hidden;">'
                f'<div style="width:{largura:.0f}%;height:100%;background:{cor};"></div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#a8a29e">Nenhuma venda no período.</p>', unsafe_allow_html=True)

with col_cat:
    secao("Relatório por Categoria de Custo")

    CAT_LABELS = {
        "custo_producao_total": ("Produção 3D", "#2563eb"),
        "custo_embalagem": ("Embalagem", "#7c3aed"),
        "custo_frete": ("Frete", "#0891b2"),
        "custo_taxa_plataforma": ("Taxa Plataforma", "#ea580c"),
        "custo_imposto": ("Impostos", "#dc2626"),
        "custo_outro": ("Outros", "#78716c"),
    }

    total_custos = pl["cmv_total"] + pl["deducoes"]
    itens_cat = [
        (label, cor, pl[key])
        for key, (label, cor) in CAT_LABELS.items()
        if pl[key] > 0
    ]

    if itens_cat:
        st.markdown('<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:10px;overflow:hidden;">', unsafe_allow_html=True)
        for label, cor, valor in itens_cat:
            pct = (valor / total_custos * 100) if total_custos else 0
            pct_rec_val = pct_rec(valor)
            st.markdown(
                f'<div style="padding:0.7rem 1rem;border-bottom:1px solid #f5f5f4;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                f'<span style="color:{cor};font-size:0.85rem;font-weight:500">{label}</span>'
                f'<span style="font-family:\'DM Mono\',monospace;color:#57534e;font-size:0.82rem">R$ {valor:,.2f}</span>'
                f'</div>'
                f'<div style="display:flex;align-items:center;gap:8px;">'
                f'<div style="flex:1;background:#f5f5f4;border-radius:3px;height:4px;overflow:hidden;">'
                f'<div style="width:{pct:.0f}%;height:100%;background:{cor};"></div></div>'
                f'<span style="font-family:\'DM Mono\',monospace;color:#a8a29e;font-size:0.72rem;white-space:nowrap">'
                f'{pct_rec_val:.1f}% receita</span>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        st.markdown(
            f'<div style="padding:0.7rem 1rem;display:flex;justify-content:space-between;">'
            f'<span style="color:#57534e;font-weight:600;font-size:0.85rem">Total Custos</span>'
            f'<span style="font-family:\'DM Mono\',monospace;color:#ea580c;font-size:0.9rem">R$ {total_custos:,.2f}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#a8a29e;font-size:0.9rem">Nenhum custo adicional categorizado.</p>', unsafe_allow_html=True)

st.markdown("---")

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

            st.markdown(
                f'<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;'
                f'display:flex;justify-content:space-between;padding:0.75rem 1rem;margin-top:0.5rem;">'
                f'<span style="color:#57534e;font-weight:600">Total / mês</span>'
                f'<span style="font-family:\'DM Mono\',monospace;color:#ea580c">R$ {total_fixos:.2f}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
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
