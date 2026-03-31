"""
Cálculo de P&L (DRE completo) para o período solicitado.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from db import listar_vendas, listar_produtos, listar_custos_fixos, listar_custos_produto, listar_fluxo_caixa
from calcular_custo import calcular_custo, calcular_produto_completo

CATEGORIAS = ["embalagem", "frete", "taxa_plataforma", "imposto", "outro"]


def _custo_detalhado_por_produto_id() -> dict:
    """
    Retorna {produto_id: {custo_producao, embalagem, frete, taxa_plataforma, imposto, outro, total}}
    separando o custo de produção (material+energia+depreciação+mão de obra) dos custos adicionais por categoria.
    """
    produtos = listar_produtos()
    resultado = {}
    for p in produtos:
        extras = listar_custos_produto(p["id"])
        calc_3d = calcular_custo(
            peso_material_g=p["peso_material_g"],
            custo_por_kg=p["custo_por_kg"],
            tempo_impressao_h=p["tempo_impressao_h"],
            consumo_watts=p["consumo_watts"],
            custo_aquisicao=p["custo_aquisicao"],
            vida_util_horas=p["vida_util_horas"],
            tempo_pos_proc_h=p["tempo_pos_proc_h"],
            custo_mao_obra_h=p["custo_mao_obra_h"],
        )
        custo_producao = calc_3d["custo_total"]
        cats = {c: 0.0 for c in CATEGORIAS}
        for extra in extras:
            v = extra["valor"] if extra["tipo"] == "fixo" else p["preco_venda"] * extra["valor"] / 100
            cat = extra.get("categoria", "outro")
            cats[cat if cat in cats else "outro"] += v
        total = custo_producao + sum(cats.values())
        resultado[p["id"]] = {"custo_producao": custo_producao, **cats, "total": total}
    return resultado


# manter compatibilidade com código legado
def _custo_por_produto_id() -> dict:
    return {pid: d["total"] for pid, d in _custo_detalhado_por_produto_id().items()}


def calcular_pl(data_ini=None, data_fim=None) -> dict:
    """
    Calcula o DRE completo para o intervalo de datas informado.

    Returns:
        dict com:
          receita_total, cmv_total, custo_producao_total,
          custo_embalagem, custo_frete, custo_taxa_plataforma, custo_imposto, custo_outro,
          receita_liquida, lucro_bruto, margem_bruta_pct,
          custos_fixos_mes, lucro_liquido, margem_liquida_pct,
          vendas (lista detalhada)
    """
    vendas = listar_vendas(data_ini, data_fim)
    custos_fixos = listar_custos_fixos()
    custo_det = _custo_detalhado_por_produto_id()

    receita_total = 0.0
    cmv_total = 0.0
    cats_total = {c: 0.0 for c in CATEGORIAS}
    custo_producao_total = 0.0
    vendas_detalhadas = []

    for v in vendas:
        qtd = v["quantidade"]
        receita_linha = v["preco_unit"] * qtd
        det = custo_det.get(v["produto_id"], {"custo_producao": 0, **{c: 0 for c in CATEGORIAS}, "total": 0})
        cmv_linha = det["total"] * qtd

        receita_total += receita_linha
        cmv_total += cmv_linha
        custo_producao_total += det["custo_producao"] * qtd
        for cat in CATEGORIAS:
            cats_total[cat] += det[cat] * qtd

        vendas_detalhadas.append({
            **v,
            "receita_linha": round(receita_linha, 2),
            "cmv_linha": round(cmv_linha, 2),
            "lucro_linha": round(receita_linha - cmv_linha, 2),
        })

    # Deduções: taxa plataforma + impostos saem da receita bruta
    deducoes = cats_total["taxa_plataforma"] + cats_total["imposto"]
    receita_liquida = receita_total - deducoes
    lucro_bruto = receita_total - cmv_total
    margem_bruta_pct = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0

    custos_fixos_mes = sum(
        cf["valor"] if cf["periodo"] == "mensal" else cf["valor"] / 12
        for cf in custos_fixos
    )

    # Despesas esporádicas do Fluxo de Caixa marcadas como "impacta P&L"
    fluxo = listar_fluxo_caixa(data_ini, data_fim)
    despesas_esporadicas = sum(
        f["valor"] for f in fluxo
        if f["tipo"] == "saida" and f.get("impacta_pl", 0)
    )

    lucro_liquido = lucro_bruto - custos_fixos_mes - despesas_esporadicas
    margem_liquida_pct = (lucro_liquido / receita_total * 100) if receita_total > 0 else 0

    return {
        "receita_total": round(receita_total, 2),
        "receita_liquida": round(receita_liquida, 2),
        "cmv_total": round(cmv_total, 2),
        "custo_producao_total": round(custo_producao_total, 2),
        "custo_embalagem": round(cats_total["embalagem"], 2),
        "custo_frete": round(cats_total["frete"], 2),
        "custo_taxa_plataforma": round(cats_total["taxa_plataforma"], 2),
        "custo_imposto": round(cats_total["imposto"], 2),
        "custo_outro": round(cats_total["outro"], 2),
        "deducoes": round(deducoes, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "margem_bruta_pct": round(margem_bruta_pct, 2),
        "custos_fixos_mes": round(custos_fixos_mes, 2),
        "despesas_esporadicas": round(despesas_esporadicas, 2),
        "lucro_liquido": round(lucro_liquido, 2),
        "margem_liquida_pct": round(margem_liquida_pct, 2),
        "vendas": vendas_detalhadas,
    }


def ranking_produtos(data_ini=None, data_fim=None) -> list:
    """Retorna produtos ordenados por margem bruta % decrescente."""
    vendas = listar_vendas(data_ini, data_fim)
    custo_unit = _custo_por_produto_id()
    produtos = {p["id"]: p for p in listar_produtos()}

    agg = {}
    for v in vendas:
        pid = v["produto_id"]
        if pid not in agg:
            agg[pid] = {"nome": v["produto_nome"], "receita": 0, "cmv": 0, "qtd": 0}
        agg[pid]["receita"] += v["preco_unit"] * v["quantidade"]
        agg[pid]["cmv"] += custo_unit.get(pid, 0) * v["quantidade"]
        agg[pid]["qtd"] += v["quantidade"]

    result = []
    for pid, d in agg.items():
        lucro = d["receita"] - d["cmv"]
        margem = (lucro / d["receita"] * 100) if d["receita"] > 0 else 0
        result.append({
            "produto": d["nome"],
            "qtd_vendida": d["qtd"],
            "receita": round(d["receita"], 2),
            "cmv": round(d["cmv"], 2),
            "lucro": round(lucro, 2),
            "margem_pct": round(margem, 2),
        })

    return sorted(result, key=lambda x: x["margem_pct"], reverse=True)
