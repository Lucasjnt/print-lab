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
from styles import aplicar_css, secao, margem_cor, sidebar_nav

st.set_page_config(page_title="Produtos — Print Lab", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")
aplicar_css()
sidebar_nav("produtos")

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

        sel_id = st.session_state.get("produto_selecionado")

        # ── Grid de cards ────────────────────────────────────────────────────
        secao("Catálogo")

        if produtos:
            # Preparar dados de cada produto
            dados = []
            for p in produtos:
                extras = listar_custos_produto(p["id"])
                calc = calcular_produto_completo(p, custos_extras=extras)
                dados.append({"p": p, "extras": extras, "calc": calc})

            # Renderizar grid 3 colunas
            cols = st.columns(3)
            for idx, d in enumerate(dados):
                p, calc = d["p"], d["calc"]
                m = calc["margem_bruta_pct"]
                cor = margem_cor(m)
                farol = "🟢" if m >= 50 else ("🟡" if m >= 30 else "🔴")
                selecionado = sel_id == p["id"]
                borda = f"border-left:4px solid {cor}" if selecionado else "border-left:4px solid #e7e5e4"

                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background:#ffffff;border:1px solid {'#ea580c' if selecionado else '#e7e5e4'};{borda};
                                border-radius:10px;padding:1rem 1.1rem;margin-bottom:0.75rem;
                                transition:box-shadow 0.15s;"
                         onmouseover="this.style.boxShadow='0 2px 12px rgba(0,0,0,0.07)'"
                         onmouseout="this.style.boxShadow='none'">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
                        <div style="font-weight:600;color:#1c1917;font-size:0.95rem;line-height:1.3;">{p['nome']}</div>
                        <span style="font-size:1.1rem;margin-left:8px;">{farol}</span>
                      </div>
                      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.5rem;">
                        <span style="font-family:'DM Mono',monospace;font-size:1.2rem;color:#1c1917;">R$ {p['preco_venda']:.2f}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:0.82rem;color:{cor};font-weight:500;">{m:.1f}%</span>
                      </div>
                      <div style="background:#f5f5f4;border-radius:3px;height:4px;overflow:hidden;">
                        <div style="width:{min(100,m):.0f}%;height:100%;background:{cor};border-radius:3px;"></div>
                      </div>
                      <div style="display:flex;justify-content:space-between;margin-top:0.5rem;">
                        <span style="font-size:0.72rem;color:#a8a29e;">Custo R$ {calc['custo_total']:.2f}</span>
                        <span style="font-size:0.72rem;color:{cor};">Lucro R$ {calc['lucro_unitario']:.2f}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Ver detalhes", key=f"sel_{p['id']}", use_container_width=True):
                        if sel_id == p["id"]:
                            st.session_state.pop("produto_selecionado", None)
                        else:
                            st.session_state["produto_selecionado"] = p["id"]
                        st.rerun()

            # ── Painel de detalhe do produto selecionado ─────────────────────
            if sel_id:
                d_sel = next((d for d in dados if d["p"]["id"] == sel_id), None)
                if d_sel:
                    p = d_sel["p"]
                    calc = d_sel["calc"]
                    extras = d_sel["extras"]
                    m = calc["margem_bruta_pct"]
                    cor = margem_cor(m)

                    st.markdown("---")
                    secao(f"Detalhes — {p['nome']}")

                    # KPIs
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Custo 3D", f"R$ {calc['custo_total'] - calc['total_adicionais']:.2f}")
                    c2.metric("Custos Extras", f"R$ {calc['total_adicionais']:.2f}")
                    c3.metric("Custo Total", f"R$ {calc['custo_total']:.2f}")
                    c4.metric("Margem Bruta", f"{m:.1f}%", delta=f"Lucro R$ {calc['lucro_unitario']:.2f}")

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

                    # Breakdown em duas colunas
                    col_info, col_custos = st.columns(2)
                    with col_info:
                        st.markdown(f"""
                        <div style="background:#ffffff;border:1px solid #e7e5e4;border-left:3px solid #ea580c;border-radius:8px;padding:1rem;margin-bottom:0.75rem;">
                          <div style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Impressão 3D</div>
                          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem 1rem;font-size:0.85rem;">
                            <span style="color:#78716c">Material</span><span style="color:#1c1917">{p.get('material_nome','—')}</span>
                            <span style="color:#78716c">Impressora</span><span style="color:#1c1917">{p.get('impressora_nome','—')}</span>
                            <span style="color:#78716c">Peso</span><span style="font-family:'DM Mono',monospace;color:#1c1917">{p['peso_material_g']:.0f}g</span>
                            <span style="color:#78716c">Tempo imp.</span><span style="font-family:'DM Mono',monospace;color:#1c1917">{h_para_hhmm(p['tempo_impressao_h'])}</span>
                            <span style="color:#78716c">Pós-proc.</span><span style="font-family:'DM Mono',monospace;color:#1c1917">{h_para_hhmm(p['tempo_pos_proc_h'])}</span>
                            <span style="color:#78716c">M.O.</span><span style="font-family:'DM Mono',monospace;color:#1c1917">R$ {p['custo_mao_obra_h']:.2f}/h</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_custos:
                        items_custo = [
                            ("Material", calc['custo_material']),
                            ("Energia", calc['custo_energia']),
                            ("Depreciação", calc['custo_depreciacao']),
                            ("Mão de obra", calc['custo_mao_obra']),
                        ]
                        rows_html = ""
                        for nome_c, val_c in items_custo:
                            rows_html += f'<div style="display:flex;justify-content:space-between;padding:0.35rem 0;border-bottom:1px solid #f5f5f4;"><span style="color:#78716c;font-size:0.85rem">{nome_c}</span><span style="font-family:\'DM Mono\',monospace;color:#1c1917;font-size:0.85rem">R$ {val_c:.2f}</span></div>'
                        custo_3d_total = calc['custo_total'] - calc['total_adicionais']
                        st.markdown(f'<div style="background:#ffffff;border:1px solid #e7e5e4;border-radius:8px;padding:1rem;margin-bottom:0.75rem;"><div style="font-size:0.65rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Breakdown de custo</div>{rows_html}<div style="display:flex;justify-content:space-between;padding:0.5rem 0 0;"><span style="color:#78716c;font-size:0.85rem;font-weight:600">Total 3D</span><span style="font-family:\'DM Mono\',monospace;color:#ea580c;font-weight:500;font-size:0.85rem">R$ {custo_3d_total:.2f}</span></div></div>', unsafe_allow_html=True)

                    # ── Custos Adicionais ────────────────────────────────────
                    st.markdown("---")
                    secao("Custos Adicionais")

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

                    # ── Editar produto ───────────────────────────────────────
                    st.markdown("---")
                    secao("Editar Produto")
                    with st.form(f"edit_prod_{p['id']}"):
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
                            st.session_state.pop("produto_selecionado", None)
                            st.rerun()

        else:
            st.markdown('<div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:10px;padding:2rem;text-align:center;color:#a8a29e">Nenhum produto cadastrado ainda.</div>', unsafe_allow_html=True)

        # ── Cadastrar novo produto ───────────────────────────────────────────
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
                        st.success(f"'{nome_p}' cadastrado. Clique no card para adicionar custos extras.")
                        st.rerun()

    lista_e_cadastro_produtos()
