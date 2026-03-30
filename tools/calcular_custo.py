"""
Lógica de cálculo de custo de impressão 3D.
Todos os valores monetários em R$.
"""
import os

TARIFA_KWH = float(os.getenv("TARIFA_KWH", "0.85"))


def calcular_custo(
    peso_material_g: float,
    custo_por_kg: float,
    tempo_impressao_h: float,
    consumo_watts: float,
    custo_aquisicao: float,
    vida_util_horas: float,
    tempo_pos_proc_h: float,
    custo_mao_obra_h: float,
    tarifa_kwh: float = None,
) -> dict:
    """
    Retorna breakdown completo de custo para uma peça impressa.

    Args:
        peso_material_g:   Gramas de filamento/resina consumidos
        custo_por_kg:      R$/kg do material
        tempo_impressao_h: Horas de impressão
        consumo_watts:     Watts da impressora
        custo_aquisicao:   R$ pago pela impressora
        vida_util_horas:   Horas estimadas de vida útil da impressora
        tempo_pos_proc_h:  Horas de pós-processamento/acabamento
        custo_mao_obra_h:  R$/hora de mão de obra
        tarifa_kwh:        R$/kWh (usa .env se None)

    Returns:
        dict com custo por componente e custo_total
    """
    if tarifa_kwh is None:
        tarifa_kwh = TARIFA_KWH

    custo_material = (peso_material_g / 1000) * custo_por_kg
    custo_energia = (consumo_watts / 1000) * tempo_impressao_h * tarifa_kwh
    custo_depreciacao = (custo_aquisicao / vida_util_horas) * tempo_impressao_h if vida_util_horas > 0 else 0
    custo_mao_obra = tempo_pos_proc_h * custo_mao_obra_h

    custo_total = custo_material + custo_energia + custo_depreciacao + custo_mao_obra

    return {
        "custo_material": round(custo_material, 4),
        "custo_energia": round(custo_energia, 4),
        "custo_depreciacao": round(custo_depreciacao, 4),
        "custo_mao_obra": round(custo_mao_obra, 4),
        "custo_total": round(custo_total, 4),
    }


def calcular_margens(custo_total: float, preco_venda: float) -> dict:
    """
    Calcula lucro e margem bruta dado custo e preço.
    """
    lucro = preco_venda - custo_total
    margem_pct = (lucro / preco_venda * 100) if preco_venda > 0 else 0
    markup = (lucro / custo_total * 100) if custo_total > 0 else 0

    return {
        "lucro_unitario": round(lucro, 4),
        "margem_bruta_pct": round(margem_pct, 2),
        "markup_pct": round(markup, 2),
    }


def calcular_custos_adicionais(custos_extras: list, preco_venda: float) -> dict:
    """
    Soma os custos adicionais por produto (embalagem, frete, taxas, etc.).

    Args:
        custos_extras: lista de dicts com {tipo, valor} onde:
                       tipo='fixo'       → valor em R$ por unidade
                       tipo='percentual' → valor em % do preço de venda
        preco_venda: preço de venda para calcular os percentuais

    Returns:
        dict com total_adicionais e breakdown por item
    """
    total = 0.0
    detalhes = []
    for c in custos_extras:
        if c["tipo"] == "fixo":
            v = c["valor"]
        else:
            v = preco_venda * c["valor"] / 100
        total += v
        detalhes.append({**c, "valor_calculado": round(v, 4)})
    return {"total_adicionais": round(total, 4), "detalhes_adicionais": detalhes}


def calcular_produto_completo(produto: dict, tarifa_kwh: float = None,
                               custos_extras: list = None) -> dict:
    """
    Recebe um dict de produto (com joins de material e impressora)
    e retorna custo de impressão + custos adicionais + margens.

    Args:
        produto:       dict com dados do produto + material + impressora
        tarifa_kwh:    sobrescreve a tarifa do .env se informado
        custos_extras: lista de custos adicionais do produto (do banco)
    """
    custos_3d = calcular_custo(
        peso_material_g=produto["peso_material_g"],
        custo_por_kg=produto["custo_por_kg"],
        tempo_impressao_h=produto["tempo_impressao_h"],
        consumo_watts=produto["consumo_watts"],
        custo_aquisicao=produto["custo_aquisicao"],
        vida_util_horas=produto["vida_util_horas"],
        tempo_pos_proc_h=produto["tempo_pos_proc_h"],
        custo_mao_obra_h=produto["custo_mao_obra_h"],
        tarifa_kwh=tarifa_kwh,
    )

    adicionais = calcular_custos_adicionais(custos_extras or [], produto["preco_venda"])
    custo_total_completo = round(custos_3d["custo_total"] + adicionais["total_adicionais"], 4)

    margens = calcular_margens(custo_total_completo, produto["preco_venda"])

    return {
        **custos_3d,
        **adicionais,
        "custo_total": custo_total_completo,
        **margens,
    }
