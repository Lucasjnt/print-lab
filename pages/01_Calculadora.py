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
from calcular_custo import calcular_custo, calcular_margens, calcular_produto_completo, calcular_custos_adicionais
from styles import aplicar_css, secao, margem_cor, barra_margem, kpi_cards, sidebar_nav

st.set_page_config(page_title="Calculadora — Print Lab", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
aplicar_css()
sidebar_nav("calculadora")

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

    # ── Grid de cards ────────────────────────────────────────────────────────
    sel_id = st.session_state.get("calc_produto_sel")

    cols = st.columns(3)
    for idx, p in enumerate(produtos):
        extras_prev = listar_custos_produto(p["id"])
        calc_prev = calcular_produto_completo(p, tarifa_kwh=tarifa, custos_extras=extras_prev)
        mp = calc_prev["margem_bruta_pct"]
        corp = margem_cor(mp)
        farol = "🟢" if mp >= 50 else ("🟡" if mp >= 30 else "🔴")
        selecionado = sel_id == p["id"]
        borda_cor = corp if selecionado else "#e7e5e4"
        borda_esq = corp if selecionado else "#e7e5e4"
        with cols[idx % 3]:
            st.markdown(f'<div style="background:#ffffff;border:1px solid {borda_cor};border-left:4px solid {borda_esq};border-radius:10px;padding:1rem 1.1rem;margin-bottom:0.5rem;" onmouseover="this.style.boxShadow=\'0 2px 12px rgba(0,0,0,0.07)\'" onmouseout="this.style.boxShadow=\'none\'"><div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;"><div style="font-weight:600;color:#1c1917;font-size:0.95rem;line-height:1.3;">{p["nome"]}</div><span style="font-size:1.1rem;margin-left:8px;">{farol}</span></div><div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.5rem;"><span style="font-family:\'DM Mono\',monospace;font-size:1.2rem;color:#1c1917;">R$ {p["preco_venda"]:.2f}</span><span style="font-family:\'DM Mono\',monospace;font-size:0.82rem;color:{corp};font-weight:500;">{mp:.1f}%</span></div><div style="background:#f5f5f4;border-radius:3px;height:4px;overflow:hidden;"><div style="width:{min(100,mp):.0f}%;height:100%;background:{corp};border-radius:3px;"></div></div><div style="display:flex;justify-content:space-between;margin-top:0.5rem;"><span style="font-size:0.72rem;color:#a8a29e;">Custo R$ {calc_prev["custo_total"]:.2f}</span><span style="font-size:0.72rem;color:{corp};">Lucro R$ {calc_prev["lucro_unitario"]:.2f}</span></div></div>', unsafe_allow_html=True)
            if st.button("Calcular" if not selecionado else "✓ Selecionado", key=f"calc_sel_{p['id']}", use_container_width=True, type="primary" if selecionado else "secondary"):
                st.session_state["calc_produto_sel"] = p["id"]
                st.rerun()

    if not sel_id:
        st.markdown('<p style="color:#a8a29e;font-size:0.9rem;margin-top:1rem;">Selecione um produto acima para ver o breakdown completo.</p>', unsafe_allow_html=True)
        st.stop()

    produto = next((p for p in produtos if p["id"] == sel_id), None)
    if not produto:
        st.session_state.pop("calc_produto_sel", None)
        st.stop()

    st.markdown("---")
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

    # ── Simulação de Venda ──────────────────────────────────────────────────
    st.markdown("---")
    secao("Simulação de Venda")

    col_q, col_dt, col_dv = st.columns([1, 1, 1])
    qtd_sim = col_q.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_sim_prod")
    tipo_desconto = col_dt.radio("Tipo de desconto", ["Percentual (%)", "Valor fixo (R$)"], horizontal=True, key="tipo_desc_prod")
    if tipo_desconto == "Percentual (%)":
        desc_pct = col_dv.number_input("Desconto (%)", min_value=0.0, max_value=99.0, value=0.0, step=1.0, key="desc_pct_prod")
        desconto_reais = produto['preco_venda'] * desc_pct / 100
    else:
        desconto_reais = col_dv.number_input("Desconto (R$)", min_value=0.0, max_value=float(produto['preco_venda']) - 0.01, value=0.0, step=0.5, key="desc_fix_prod")

    preco_unit_sim = produto['preco_venda'] - desconto_reais
    custo_3d_base = resultado['custo_total'] - resultado['total_adicionais']
    adicionais_sim = calcular_custos_adicionais(extras, preco_unit_sim)
    custo_unit_sim = custo_3d_base + adicionais_sim['total_adicionais']
    margens_sim = calcular_margens(custo_unit_sim, preco_unit_sim)
    m_sim = margens_sim['margem_bruta_pct']
    cor_sim = margem_cor(m_sim)

    receita_total = preco_unit_sim * qtd_sim
    custo_total_sim = custo_unit_sim * qtd_sim
    lucro_total_sim = receita_total - custo_total_sim
    diff_margem = m_sim - m

    kpi_cards([
        {"label": "Preço Unitário", "value": f"R$ {preco_unit_sim:.2f}",
         "delta": f"-R$ {desconto_reais:.2f} desconto" if desconto_reais > 0 else "sem desconto",
         "delta_type": "neg" if desconto_reais > 0 else "neu"},
        {"label": "Receita Total", "value": f"R$ {receita_total:.2f}",
         "delta": f"{qtd_sim} un. × R$ {preco_unit_sim:.2f}",
         "delta_type": "neu"},
        {"label": "Custo Total", "value": f"R$ {custo_total_sim:.2f}",
         "delta": f"{qtd_sim} un. × R$ {custo_unit_sim:.2f}",
         "delta_type": "neu"},
        {"label": "Lucro Total", "value": f"R$ {lucro_total_sim:.2f}",
         "delta": f"R$ {margens_sim['lucro_unitario']:.2f}/un.",
         "delta_type": "pos" if lucro_total_sim > 0 else "neg"},
    ])

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-top:0.5rem;">
      <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e;white-space:nowrap;">MARGEM {"COM DESCONTO" if desconto_reais > 0 else ""}</span>
      <div style="flex:1;background:#f5f5f4;border-radius:4px;height:8px;overflow:hidden;">
        <div style="width:{min(100,m_sim):.0f}%;height:100%;background:{cor_sim};border-radius:4px;transition:width 0.4s;"></div>
      </div>
      <span style="font-family:'DM Mono',monospace;color:{cor_sim};font-size:0.9rem;white-space:nowrap;">{m_sim:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    if desconto_reais > 0:
        st.markdown(f"""
        <div style="margin-top:0.75rem;padding:0.75rem 1rem;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;font-size:0.85rem;color:#78716c;">
          Margem original <strong style="color:#1c1917">{m:.1f}%</strong> →
          com desconto <strong style="color:{cor_sim}">{m_sim:.1f}%</strong>
          <span style="color:#a8a29e">({diff_margem:+.1f}pp)</span>
        </div>
        """, unsafe_allow_html=True)

    if adicionais_sim['total_adicionais'] != resultado['total_adicionais'] and desconto_reais > 0:
        st.markdown(f"""
        <div style="margin-top:0.5rem;padding:0.6rem 1rem;background:#f5f5f4;border:1px solid #e7e5e4;border-radius:8px;font-size:0.82rem;color:#78716c;">
          Custos percentuais recalculados: <strong style="color:#ea580c">R$ {adicionais_sim['total_adicionais']:.2f}</strong>/un.
          <span style="color:#a8a29e">(eram R$ {resultado['total_adicionais']:.2f})</span>
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

        # ── Simulação de Venda (avulso) ──────────────────────────────────
        st.markdown("---")
        secao("Simulação de Venda")

        col_q, col_dt, col_dv = st.columns([1, 1, 1])
        qtd_av = col_q.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_sim_av")
        tipo_desc_av = col_dt.radio("Tipo de desconto", ["Percentual (%)", "Valor fixo (R$)"], horizontal=True, key="tipo_desc_av")
        if tipo_desc_av == "Percentual (%)":
            desc_pct_av = col_dv.number_input("Desconto (%)", min_value=0.0, max_value=99.0, value=0.0, step=1.0, key="desc_pct_av")
            desc_reais_av = preco_venda * desc_pct_av / 100
        else:
            desc_reais_av = col_dv.number_input("Desconto (R$)", min_value=0.0, max_value=preco_venda - 0.01, value=0.0, step=0.5, key="desc_fix_av")

        preco_unit_av = preco_venda - desc_reais_av
        margens_av = calcular_margens(resultado["custo_total"], preco_unit_av)
        m_av = margens_av['margem_bruta_pct']
        cor_av = margem_cor(m_av)

        receita_av = preco_unit_av * qtd_av
        custo_av = resultado["custo_total"] * qtd_av
        lucro_av = receita_av - custo_av

        kpi_cards([
            {"label": "Preço Unitário", "value": f"R$ {preco_unit_av:.2f}",
             "delta": f"-R$ {desc_reais_av:.2f} desconto" if desc_reais_av > 0 else "sem desconto",
             "delta_type": "neg" if desc_reais_av > 0 else "neu"},
            {"label": "Receita Total", "value": f"R$ {receita_av:.2f}",
             "delta": f"{qtd_av} un. × R$ {preco_unit_av:.2f}",
             "delta_type": "neu"},
            {"label": "Custo Total", "value": f"R$ {custo_av:.2f}",
             "delta": f"{qtd_av} un. × R$ {resultado['custo_total']:.2f}",
             "delta_type": "neu"},
            {"label": "Lucro Total", "value": f"R$ {lucro_av:.2f}",
             "delta": f"R$ {margens_av['lucro_unitario']:.2f}/un.",
             "delta_type": "pos" if lucro_av > 0 else "neg"},
        ])

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;margin-top:0.5rem;">
          <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#a8a29e;white-space:nowrap;">MARGEM {"COM DESCONTO" if desc_reais_av > 0 else ""}</span>
          <div style="flex:1;background:#f5f5f4;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:{min(100,m_av):.0f}%;height:100%;background:{cor_av};border-radius:4px;"></div>
          </div>
          <span style="font-family:'DM Mono',monospace;color:{cor_av};font-size:0.9rem;white-space:nowrap;">{m_av:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        if desc_reais_av > 0:
            diff_m_av = m_av - m
            st.markdown(f"""
            <div style="margin-top:0.75rem;padding:0.75rem 1rem;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;font-size:0.85rem;color:#78716c;">
              Margem original <strong style="color:#1c1917">{m:.1f}%</strong> →
              com desconto <strong style="color:{cor_av}">{m_av:.1f}%</strong>
              <span style="color:#a8a29e">({diff_m_av:+.1f}pp)</span>
            </div>
            """, unsafe_allow_html=True)
