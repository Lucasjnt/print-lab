import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
import pandas as pd
import calendar
from datetime import date
from calcular_margem import calcular_pl, ranking_produtos
from db import listar_vendas, obter_meta, upsert_meta, init_db
from styles import aplicar_css, secao, kpi_cards, margem_cor, sidebar_nav

st.set_page_config(page_title="Dashboard — Print Lab", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
aplicar_css()
init_db()
sidebar_nav("dashboard")

hoje = date.today()

# ── Metas na sidebar ──────────────────────────────────────────────────────────
meta = obter_meta(hoje.year, hoje.month)
with st.sidebar:
    st.markdown('<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#78716c;margin:0.5rem 0 0.75rem 0;">METAS DO MÊS</div>', unsafe_allow_html=True)
    with st.form("form_metas"):
        m_rec = st.number_input("Meta Receita (R$)", value=float(meta["meta_receita"]), min_value=0.0, step=100.0)
        m_luc = st.number_input("Meta Lucro (R$)", value=float(meta["meta_lucro"]), min_value=0.0, step=50.0)
        if st.form_submit_button("Salvar metas", use_container_width=True):
            upsert_meta(hoje.year, hoje.month, m_rec, m_luc)
            st.rerun()

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

# ── Metas do mês ──────────────────────────────────────────────────────────────
if meta["meta_receita"] > 0 or meta["meta_lucro"] > 0:
    secao("Metas do Mês")
    mc1, mc2 = st.columns(2)

    def meta_card(col, label, atual, alvo, prefixo="R$"):
        pct = min(100, (atual / alvo * 100)) if alvo > 0 else 0
        cor = "#16a34a" if pct >= 100 else ("#d97706" if pct >= 60 else "#dc2626")
        falta = max(0, alvo - atual)
        fmt = lambda v: f"R$ {v:,.2f}" if prefixo == "R$" else f"{v:.1f}%"
        col.markdown(
            f'<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:12px;padding:1.25rem;">'
            f'<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#a8a29e;margin-bottom:0.5rem">{label}</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:0.75rem;">'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:1.6rem;color:{cor}">{fmt(atual)}</div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;color:#a8a29e">de {fmt(alvo)}</div>'
            f'</div>'
            f'<div style="background:#f5f5f4;border-radius:4px;height:8px;overflow:hidden;margin-bottom:0.5rem;">'
            f'<div style="width:{pct:.0f}%;height:100%;background:{cor};border-radius:4px;transition:width 0.4s;"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;">'
            f'<span style="font-family:\'DM Mono\',monospace;color:{cor};font-weight:600">{pct:.1f}% atingido</span>'
            f'<span style="color:#a8a29e">faltam {fmt(falta)}</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    if meta["meta_receita"] > 0:
        meta_card(mc1, "Meta de Receita", pl["receita_total"], meta["meta_receita"])
    if meta["meta_lucro"] > 0:
        meta_card(mc2, "Meta de Lucro Líquido", pl["lucro_liquido"], meta["meta_lucro"])

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
