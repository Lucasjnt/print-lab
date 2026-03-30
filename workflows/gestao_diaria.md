# Workflow: Gestão Diária do Negócio de Impressão 3D

## Objetivo
Manter o controle atualizado de custos, margens e vendas do negócio de impressão 3D no dia a dia.

## Pré-requisitos
- App rodando: `streamlit run app.py` na pasta do projeto
- Browser aberto em `http://localhost:8501`

---

## Setup inicial (fazer uma vez)

### 1. Cadastrar impressoras
1. Ir para **Produtos → aba Impressoras**
2. Preencher: nome, custo de aquisição, vida útil em horas, consumo em Watts
3. Exemplo: "Bambu Lab A1 Mini", R$ 2.800, 5.000h, 250W

### 2. Cadastrar materiais
1. Ir para **Produtos → aba Materiais**
2. Preencher: nome, tipo (filamento/resina), custo por kg
3. Exemplo: "PLA+ Branco", filamento, R$ 85,00/kg

### 3. Cadastrar catálogo de produtos
1. Ir para **Produtos → aba Produtos**
2. Para cada produto: selecionar material + impressora, informar peso (g), tempo de impressão (h), pós-processamento (h), mão de obra (R$/h) e preço de venda
3. O sistema calcula automaticamente o custo e a margem

### 4. Cadastrar custos fixos
1. Ir para **P&L**
2. Na seção "Custos Fixos", adicionar: aluguel, energia fixa, plataformas, etc.

### 5. Ajustar tarifa de energia
1. Editar o arquivo `.env` na raiz do projeto
2. Alterar `TARIFA_KWH` para o valor da sua fatura de energia

---

## Rotina diária

### Registrar vendas
1. Ir para **Vendas**
2. Para cada venda do dia: selecionar produto, informar quantidade, confirmar preço, selecionar canal (Instagram, WhatsApp, Feira, etc.)
3. Clicar em **Registrar venda**

---

## Rotina semanal

### Verificar margens
1. Ir para **P&L**
2. Selecionar o período da semana
3. Conferir margem bruta e margem líquida
4. Se algum produto estiver com margem < 30%, revisar o preço de venda ou reduzir custos

---

## Rotina mensal

### Fechar o mês
1. Ir para **P&L**
2. Selecionar do dia 1 ao último dia do mês
3. Exportar CSV para arquivo (botão "Exportar P&L")
4. Conferir ranking de produtos — identificar os mais lucrativos
5. Ir para **Dashboard** para ver comparativo com mês anterior

---

## Calculadora de custo rápido
- Usar **Calculadora → Cálculo avulso** para avaliar novos produtos antes de precificar
- Regra de ouro: margem bruta mínima de 40% para cobrir custos fixos e gerar lucro

---

## Dicas de precificação

| Margem Bruta | Situação |
|---|---|
| < 30% | Risco — produto pode estar dando prejuízo após custos fixos |
| 30–50% | Aceitável para produtos de alto volume |
| 50–70% | Saudável |
| > 70% | Excelente — produto premium ou nicho |
