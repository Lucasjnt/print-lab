import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import streamlit as st
from db import listar_produtos, listar_materiais, listar_impressoras, listar_custos_produto
from calcular_custo import calcular_custo, calcular_margens, calcular_produto_completo
from styles import aplicar_css, secao, margem_cor, barra_margem, kpi_cards

st.set_page_config(page_title="Calculadora — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
  <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#f97316;">
    PRINT LAB
  </div>
  <h1 style="margin:0.25rem 0 0.5rem 0;">Calculadora</h1>
  <p style="color:#525252;margin:0;font-size:0.95rem;">Simule o custo de qualquer impressão e descubra a margem real.</p>
</div>
""", unsafe_allow_html=True)

# ── Seletor de modo ───────────────────────────────────────────────────────────
modo = st.radio(
    "Modo",
    ["Produto cadastrado", "Cálculo avulso"],
    horizontal=True,
    label_visibility="collapsed",
)

tarifa = st.sidebar.number_input(
    "Tarifa energia (R$/kWh)",
    value=float(os.getenv("TARIFA_KWH", "0.85")),
    step=0.01, format="%.3f",
    help="Valor do kWh na sua conta de luz"
)
st.sidebar.markdown("---")
st.sidebar.markdown('<span style="color:#525252;font-size:0.75rem">Altere a tarifa conforme sua conta de luz para cálculos precisos de energia.</span>', unsafe_allow_html=True)

st.markdown("---")

# ══ MODO: PRODUTO CADASTRADO ══════════════════════════════════════════════════
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

    # KPIs principais
    kpi_cards([
        {"label": "Custo Total", "value": f"R$ {resultado['custo_total']:.2f}", "delta": "por unidade", "delta_type": "neu"},
        {"label": "Preço de Venda", "value": f"R$ {produto['preco_venda']:.2f}", "delta": "praticado", "delta_type": "neu"},
        {"label": "Lucro Unitário", "value": f"R$ {resultado['lucro_unitario']:.2f}",
         "delta": f"markup {resultado['markup_pct']:.0f}%",
         "delta_type": "pos" if resultado['lucro_unitario'] > 0 else "neg"},
        {"label": "Margem Bruta", "value": f"{m:.1f}%",
         "delta": "≥50% excelente" if m >= 50 else ("≥30% aceitável" if m >= 30 else "< 30% atenção"),
         "delta_type": "pos" if m >= 50 else ("neu" if m >= 30 else "neg")},
    ])

    # Barra visual de margem
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
      <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#525252;white-space:nowrap;">MARGEM</span>
      <div style="flex:1;background:#1a1a1a;border-radius:4px;height:8px;overflow:hidden;">
        <div style="width:{min(100,m):.0f}%;height:100%;background:{cor};border-radius:4px;transition:width 0.4s;"></div>
      </div>
      <span style="font-family:'DM Mono',monospace;color:{cor};font-size:0.9rem;white-space:nowrap;">{m:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Breakdown
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
                        padding:0.6rem 0;border-bottom:1px solid #141414;">
              <span style="color:#a3a3a3;font-size:0.9rem">{nome}</span>
              <span style="font-family:'DM Mono',monospace;color:#e5e5e5">R$ {val:.2f}
                <span style="color:#404040;font-size:0.75rem"> {pct_do_total:.0f}%</span>
              </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:0.75rem 0;margin-top:0.25rem;">
          <span style="color:#737373;font-size:0.85rem;font-weight:600">Subtotal 3D</span>
          <span style="font-family:'DM Mono',monospace;color:#f97316;font-weight:500">R$ {custo_3d:.2f}</span>
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
                cat_cor = {"embalagem": "#93c5fd", "frete": "#c4b5fd",
                           "taxa_plataforma": "#fcd34d", "imposto": "#fca5a5"}.get(cat, "#d1d5db")
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:0.6rem 0;border-bottom:1px solid #141414;">
                  <span style="color:#a3a3a3;font-size:0.9rem">
                    <span style="color:{cat_cor};font-size:0.65rem;text-transform:uppercase;
                                 letter-spacing:0.08em;margin-right:6px">{cat.replace('_',' ')}</span>
                    {nome_e}
                  </span>
                  <span style="font-family:'DM Mono',monospace;color:#e5e5e5">R$ {a['valor_calculado']:.2f}
                    <span style="color:#404040;font-size:0.75rem"> {pct_do_total:.0f}%</span>
                  </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.75rem 0;margin-top:0.25rem;">
              <span style="color:#737373;font-size:0.85rem;font-weight:600">Subtotal extras</span>
              <span style="font-family:'DM Mono',monospace;color:#f97316;font-weight:500">R$ {resultado['total_adicionais']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#404040;font-size:0.9rem;margin-top:1rem;">Nenhum custo adicional cadastrado para este produto.<br>Adicione em <b>Produtos</b>.</p>', unsafe_allow_html=True)

    # Dados técnicos
    secao("Dados técnicos")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""
    <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:8px;padding:1rem;">
      <div style="color:#525252;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Material</div>
      <div style="color:#e5e5e5;margin-bottom:0.25rem">{produto['material_nome']}</div>
      <div style="font-family:'DM Mono',monospace;color:#f97316">R$ {produto['custo_por_kg']:.2f}/kg</div>
      <div style="color:#525252;font-size:0.8rem;margin-top:0.25rem">{produto['peso_material_g']} g consumidos</div>
    </div>
    """, unsafe_allow_html=True)
    col2.markdown(f"""
    <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:8px;padding:1rem;">
      <div style="color:#525252;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Impressora</div>
      <div style="color:#e5e5e5;margin-bottom:0.25rem">{produto['impressora_nome']}</div>
      <div style="font-family:'DM Mono',monospace;color:#f97316">{produto['consumo_watts']} W</div>
      <div style="color:#525252;font-size:0.8rem;margin-top:0.25rem">{produto['tempo_impressao_h']}h de impressão</div>
    </div>
    """, unsafe_allow_html=True)
    col3.markdown(f"""
    <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:8px;padding:1rem;">
      <div style="color:#525252;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">Mão de obra</div>
      <div style="font-family:'DM Mono',monospace;color:#f97316">R$ {produto['custo_mao_obra_h']:.2f}/h</div>
      <div style="color:#525252;font-size:0.8rem;margin-top:0.25rem">{produto['tempo_pos_proc_h']}h pós-processamento</div>
    </div>
    """, unsafe_allow_html=True)

# ══ MODO: CÁLCULO AVULSO ══════════════════════════════════════════════════════
else:
    materiais = listar_materiais()
    impressoras = listar_impressoras()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        secao("Material")
        if materiais:
            mat_id = st.selectbox("Material cadastrado", [m["id"] for m in materiais],
                                   format_func=lambda x: next(m["nome"] for m in materiais if m["id"] == x))
            mat = next(m for m in materiais if m["id"] == mat_id)
            custo_por_kg = mat["custo_por_kg"]
            st.markdown(f'<span style="font-family:\'DM Mono\',monospace;color:#f97316;font-size:0.85rem">R$ {custo_por_kg:.2f}/kg</span>', unsafe_allow_html=True)
        else:
            custo_por_kg = st.number_input("Custo do material (R$/kg)", value=80.0, step=1.0)

        peso_g = st.number_input("Peso consumido (g)", value=100.0, min_value=0.1, step=1.0)
        preco_venda = st.number_input("Preço de venda (R$)", value=0.0, step=0.5,
                                       help="Preencha para ver margem e lucro")

    with col2:
        secao("Impressora")
        if impressoras:
            imp_id = st.selectbox("Impressora cadastrada", [i["id"] for i in impressoras],
                                   format_func=lambda x: next(i["nome"] for i in impressoras if i["id"] == x))
            imp = next(i for i in impressoras if i["id"] == imp_id)
            consumo_w, custo_aq, vida_h = imp["consumo_watts"], imp["custo_aquisicao"], imp["vida_util_horas"]
            st.markdown(f'<span style="font-family:\'DM Mono\',monospace;color:#f97316;font-size:0.85rem">{consumo_w}W — R$ {custo_aq:,.0f} / {vida_h:.0f}h vida útil</span>', unsafe_allow_html=True)
        else:
            consumo_w = st.number_input("Consumo (W)", value=250.0, step=10.0)
            custo_aq  = st.number_input("Custo de aquisição (R$)", value=3000.0, step=100.0)
            vida_h    = st.number_input("Vida útil (h)", value=5000.0, step=100.0)

        tempo_h   = st.number_input("Tempo de impressão (h)", value=2.0, min_value=0.1, step=0.5)
        tempo_pos = st.number_input("Tempo pós-processamento (h)", value=0.0, min_value=0.0, step=0.25)
        mob_h     = st.number_input("Custo mão de obra (R$/h)", value=float(os.getenv("CUSTO_MOB_HORA", "15.0")), step=1.0)

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
        {"label": "Material",     "value": f"R$ {resultado['custo_material']:.2f}",    "delta": f"{resultado['custo_material']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
        {"label": "Energia",      "value": f"R$ {resultado['custo_energia']:.2f}",     "delta": f"{resultado['custo_energia']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
        {"label": "Depreciação",  "value": f"R$ {resultado['custo_depreciacao']:.2f}", "delta": f"{resultado['custo_depreciacao']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
        {"label": "Mão de Obra",  "value": f"R$ {resultado['custo_mao_obra']:.2f}",   "delta": f"{resultado['custo_mao_obra']/resultado['custo_total']*100:.0f}% do total" if resultado['custo_total'] else "—", "delta_type": "neu"},
    ]
    kpi_cards(itens_kpi)

    st.markdown(f"""
    <div style="background:#0d0d0d;border:1px solid #2a2a2a;border-left:4px solid #f97316;
                border-radius:10px;padding:1.25rem 1.5rem;display:flex;
                justify-content:space-between;align-items:center;margin-bottom:1rem;">
      <span style="color:#737373;font-size:0.9rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em">Custo Total</span>
      <span style="font-family:'DM Mono',monospace;font-size:2rem;color:#ffffff">R$ {resultado['custo_total']:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    if preco_venda > 0:
        margens = calcular_margens(resultado["custo_total"], preco_venda)
        m = margens["margem_bruta_pct"]
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
          <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#525252">MARGEM</span>
          <div style="flex:1;background:#1a1a1a;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:{min(100,m):.0f}%;height:100%;background:{cor};border-radius:4px;"></div>
          </div>
          <span style="font-family:'DM Mono',monospace;color:{cor}">{m:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
