# Agent Instructions — Print Lab

Você está trabalhando no projeto **Print Lab**, uma plataforma de gestão de custos, margens e P&L para um negócio de impressão 3D. O projeto segue a arquitetura **WAT framework** (Workflows, Agents, Tools).

---

## O Projeto

**Print Lab** é um app Streamlit local que permite ao dono do negócio:
- Calcular o custo real de cada impressão 3D (material, energia, depreciação, mão de obra)
- Gerenciar custos adicionais por produto (embalagem, frete, taxas de plataforma, impostos)
- Registrar vendas diárias por canal (Instagram, WhatsApp, Feira, etc.)
- Visualizar P&L completo com margem bruta e líquida
- Acompanhar KPIs e comparativos mensais no Dashboard

**Repositório:** https://github.com/Lucasjnt/print-lab
**Stack:** Python 3 · Streamlit · SQLite · DM Mono / Syne / Outfit (Google Fonts)
**Tema:** Dark (`#080808`) com acento laranja filamento (`#f97316`)

---

## Arquitetura WAT

### Layer 1 — Workflows (`workflows/`)
SOPs em Markdown. Cada workflow define objetivo, inputs, ferramentas, outputs e edge cases.
- `workflows/gestao_diaria.md` — rotina de uso diário do app

### Layer 2 — Agent (você)
Lê os workflows, executa ferramentas na sequência certa, trata erros e melhora o sistema continuamente. Não tenta fazer tudo diretamente — delega execução para os tools.

### Layer 3 — Tools (`tools/`)
Scripts Python determinísticos que fazem o trabalho real:

| Arquivo | Responsabilidade |
|---|---|
| `tools/db.py` | Conexão SQLite, init do banco, todo CRUD (insert/update/delete/list) |
| `tools/calcular_custo.py` | Lógica de custo de impressão 3D + custos adicionais + margens |
| `tools/calcular_margem.py` | P&L por período, ranking de produtos |
| `tools/relatorios.py` | Exportação CSV de P&L e ranking |
| `tools/styles.py` | Design system: CSS global, `aplicar_css()`, `kpi_cards()`, `secao()`, `margem_cor()` |

---

## Banco de Dados (`data/negocio.db`)

SQLite local. Tabelas:

| Tabela | Descrição |
|---|---|
| `impressoras` | Equipamentos com custo, vida útil (h) e consumo (W) |
| `materiais` | Filamentos/resinas com tipo e custo/kg |
| `produtos` | Catálogo com FK para material e impressora |
| `custos_produto` | Custos adicionais por produto (fixo R$/unit ou % do preço) |
| `vendas` | Registro de vendas com data, canal, qtd e preço |
| `custos_fixos` | Despesas fixas mensais/anuais (aluguel, internet, etc.) |

**Nunca commitar `data/negocio.db`** — está no `.gitignore`.

---

## Lógica de Cálculo

### Custo de impressão 3D
```
custo_material    = peso_g / 1000 * custo_por_kg
custo_energia     = (watts / 1000) * tempo_h * tarifa_kwh
custo_depreciacao = (custo_aquisicao / vida_util_horas) * tempo_h
custo_mao_obra    = tempo_pos_proc_h * custo_mao_obra_h
```

### Custos adicionais por produto
```
tipo 'fixo'       → valor R$ por unidade
tipo 'percentual' → valor % × preco_venda / 100
```

### P&L
```
receita_total    = SUM(preco_unit × qtd)
cmv_total        = SUM(custo_total_produto × qtd)
lucro_bruto      = receita_total − cmv_total
margem_bruta_%   = lucro_bruto / receita_total × 100
custos_fixos_mes = SUM(fixos mensais + anuais/12)
lucro_liquido    = lucro_bruto − custos_fixos_mes
margem_liquida_% = lucro_liquido / receita_total × 100
```

---

## Páginas do App

| Arquivo | Rota | Função |
|---|---|---|
| `app.py` | `/` | Home com KPIs do mês e navegação |
| `pages/01_Calculadora.py` | `/Calculadora` | Custo por produto cadastrado ou avulso |
| `pages/02_Produtos.py` | `/Produtos` | CRUD completo: produtos, materiais, impressoras, custos adicionais |
| `pages/03_Vendas.py` | `/Vendas` | Registro e histórico de vendas |
| `pages/04_PL.py` | `/PL` | DRE, ranking, exportação CSV, custos fixos |
| `pages/05_Dashboard.py` | `/Dashboard` | KPIs, gráficos, comparativo mensal |

---

## Design System (`tools/styles.py`)

Importar em todas as páginas:
```python
from styles import aplicar_css, secao, kpi_cards, margem_cor, barra_margem
```

Funções disponíveis:
- `aplicar_css()` — aplica o CSS global (chamar no topo de toda página)
- `secao("Título")` — header de seção com acento laranja
- `kpi_cards([{label, value, delta, delta_type}])` — grid de métricas
- `margem_cor(pct)` — retorna cor (#4ade80 / #facc15 / #f87171) pela margem
- `barra_margem(pct)` — HTML de barra visual de margem

---

## Configuração (`.env`)

```
TARIFA_KWH=0.85       # R$/kWh da sua conta de luz
CUSTO_MOB_HORA=15.00  # R$/hora de mão de obra padrão
MOEDA=BRL
```

Tema Streamlit em `.streamlit/config.toml`:
```toml
[theme]
base = "dark"
backgroundColor = "#080808"
secondaryBackgroundColor = "#0d0d0d"
primaryColor = "#f97316"
```

---

## Como Rodar

```bash
cd "Caluladora de margem"
streamlit run app.py
# Abre em http://localhost:8501
```

**Primeiro uso:**
1. Produtos → Impressoras → cadastrar impressora
2. Produtos → Materiais → cadastrar material
3. Produtos → cadastrar produto + adicionar custos extras
4. P&L → Custos Fixos → cadastrar despesas fixas
5. Vendas → registrar vendas

---

## Regras para o Agent

1. **Antes de criar qualquer coisa**, verificar se já existe em `tools/` ou `pages/`
2. **Toda nova página** deve importar `aplicar_css()` de `styles.py` como primeira instrução visual
3. **Toda nova função de banco** deve seguir o padrão de `db.py`: `listar_X`, `inserir_X`, `atualizar_X`, `deletar_X`
4. **Nunca commitar** `.env`, `data/negocio.db`, `credentials.json` ou `token.json`
5. **Depois de alterar cálculos**, verificar se `calcular_margem.py` e as páginas de P&L/Dashboard refletem corretamente
6. **Ao adicionar campos ao banco**, usar `ALTER TABLE` ou atualizar `init_db()` com `CREATE TABLE IF NOT EXISTS` — nunca dropar tabelas com dados

---

## Saúde de Margem (referência)

| Margem Bruta | Situação |
|---|---|
| ≥ 50% | Excelente |
| 30–49% | Aceitável |
| < 30% | Atenção — pode não cobrir custos fixos |
