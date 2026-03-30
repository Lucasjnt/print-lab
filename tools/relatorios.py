"""
Geração de relatórios em CSV para exportação.
"""
import csv
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from calcular_margem import calcular_pl, ranking_produtos


def pl_para_csv(data_ini=None, data_fim=None) -> str:
    """Retorna string CSV com o detalhamento de vendas do período."""
    pl = calcular_pl(data_ini, data_fim)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Data", "Produto", "Canal", "Qtd", "Preço Unit", "Receita", "CMV", "Lucro"])
    for v in pl["vendas"]:
        writer.writerow([
            v["data"],
            v["produto_nome"],
            v.get("canal", ""),
            v["quantidade"],
            f'{v["preco_unit"]:.2f}',
            f'{v["receita_linha"]:.2f}',
            f'{v["cmv_linha"]:.2f}',
            f'{v["lucro_linha"]:.2f}',
        ])

    writer.writerow([])
    writer.writerow(["RESUMO"])
    writer.writerow(["Receita Total", f'R$ {pl["receita_total"]:.2f}'])
    writer.writerow(["CMV Total", f'R$ {pl["cmv_total"]:.2f}'])
    writer.writerow(["Lucro Bruto", f'R$ {pl["lucro_bruto"]:.2f}'])
    writer.writerow(["Margem Bruta", f'{pl["margem_bruta_pct"]:.1f}%'])
    writer.writerow(["Custos Fixos (mês)", f'R$ {pl["custos_fixos_mes"]:.2f}'])
    writer.writerow(["Lucro Líquido", f'R$ {pl["lucro_liquido"]:.2f}'])
    writer.writerow(["Margem Líquida", f'{pl["margem_liquida_pct"]:.1f}%'])

    return output.getvalue()


def ranking_para_csv(data_ini=None, data_fim=None) -> str:
    """Retorna string CSV com ranking de produtos por margem."""
    ranking = ranking_produtos(data_ini, data_fim)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Produto", "Qtd Vendida", "Receita", "CMV", "Lucro", "Margem %"])
    for r in ranking:
        writer.writerow([
            r["produto"],
            r["qtd_vendida"],
            f'{r["receita"]:.2f}',
            f'{r["cmv"]:.2f}',
            f'{r["lucro"]:.2f}',
            f'{r["margem_pct"]:.1f}%',
        ])

    return output.getvalue()
