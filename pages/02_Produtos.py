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
from styles import aplicar_css, secao, margem_cor

st.set_page_config(page_title="Produtos — Print Lab", page_icon="⬡", layout="wide")
aplicar_css()

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

        secao("Catálogo")

        if produtos:
            for p in produtos:
                extras = listar_custos_produto(p["id"])
                calc   = calcular_produto_completo(p, custos_extras=extras)
                m      = calc["margem_bruta_pct"]
                cor    = margem_cor(m)

                with st.expander(f"**{p['nome']}** — R$ {p['preco_venda']:.2f} · Margem {m:.1f}%"):

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Custo 3D",      f"R$ {calc['custo_total'] - calc['total_adicionais']:.2f}")
                    c2.metric("Custos Extras",  f"R$ {calc['total_adicionais']:.2f}")
                    c3.metric("Custo Total",    f"R$ {calc['custo_total']:.2f}")
                    c4.metric("Margem Bruta",   f"{m:.1f}%", delta=f"Lucro R$ {calc['lucro_unitario']:.2f}")

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

                    with st.form(f"edit_prod_{p['id']}"):
                        st.markdown('<span style="font-size:0.68rem;color:#ea580c;text-transform:uppercase;letter-spacing:0.1em">Editar produto</span>', unsafe_allow_html=True)
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
                            st.rerun()

                    st.divider()
                    st.markdown('<span style="font-size:0.68rem;color:#a8a29e;text-transform:uppercase;letter-spacing:0.1em">Custos Adicionais</span>', unsafe_allow_html=True)

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
        else:
            st.markdown('<div style="background:#ffffff;border:1px dashed #e7e5e4;border-radius:10px;padding:2rem;text-align:center;color:#a8a29e">Nenhum produto cadastrado ainda.</div>', unsafe_allow_html=True)

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
                        st.success(f"'{nome_p}' cadastrado. Abra-o acima para adicionar custos extras.")
                        st.rerun()

    lista_e_cadastro_produtos()
