"""
Cálculo de P&L (DRE simplificado) para o período solicitado.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from db import listar_vendas, listar_produtos, listar_custos_fixos, listar_custos_produto
from calcular_custo import calcular_produto_completo


def _custo_por_produto_id() -> dict:
    """Retorna {produto_id: custo_total_unitario} incluindo custos adicionais."""
    produtos = listar_produtos()
    resultado = {}
    for p in produtos:
        extras = listar_custos_produto(p["id"])
        resultado[p["id"]] = calcular_produto_completo(p, custos_extras=extras)["custo_total"]
    return resultado


def calcular_pl(data_ini=None, data_fim=None) -> dict:
    """
    Calcula o P&L para o intervalo de datas informado.

    Returns:
        dict com:
          receita_total, cmv_total, lucro_bruto, margem_bruta_pct,
          custos_fixos_mes, lucro_liquido, margem_liquida_pct,
          vendas (lista detalhada)
    """
    vendas = listar_vendas(data_ini, data_fim)
    custos_fixos = listar_custos_fixos()
    custo_unit = _custo_por_produto_id()

    receita_total = 0.0
    cmv_total = 0.0
    vendas_detalhadas = []

    for v in vendas:
        receita_linha = v["preco_unit"] * v["quantidade"]
        custo_prod = custo_unit.get(v["produto_id"], 0)
        cmv_linha = custo_prod * v["quantidade"]

        receita_total += receita_linha
        cmv_total += cmv_linha

        vendas_detalhadas.append({
            **v,
            "receita_linha": round(receita_linha, 2),
            "cmv_linha": round(cmv_linha, 2),
            "lucro_linha": round(receita_linha - cmv_linha, 2),
        })

    lucro_bruto = receita_total - cmv_total
    margem_bruta_pct = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0

    # Normaliza custos fixos para mensal
    custos_fixos_mes = sum(
        cf["valor"] if cf["periodo"] == "mensal" else cf["valor"] / 12
        for cf in custos_fixos
    )

    lucro_liquido = lucro_bruto - custos_fixos_mes
    margem_liquida_pct = (lucro_liquido / receita_total * 100) if receita_total > 0 else 0

    return {
        "receita_total": round(receita_total, 2),
        "cmv_total": round(cmv_total, 2),
        "lucro_bruto": round(lucro_bruto, 2),
        "margem_bruta_pct": round(margem_bruta_pct, 2),
        "custos_fixos_mes": round(custos_fixos_mes, 2),
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
