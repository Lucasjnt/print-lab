# Print Lab — Redesign Executivo + Fix de Reset de Página

**Data:** 2026-03-30
**Status:** Aprovado

---

## Problema

A interface atual tem dois problemas que prejudicam o uso diário:

1. **Tema preto puro (`#080808`)** — baixo contraste, dificulta leitura de dados financeiros, não comunica profissionalismo para um painel executivo.
2. **Reset de página após cadastro** — ao chamar `st.rerun()` após cada operação CRUD, a página inteira recarrega: o scroll volta pro topo, expanders fecham, o usuário perde o contexto do que estava fazendo.

---

## Solução

### 1. Novo tema: Warm Neutral

Substituição completa do design system em `tools/styles.py`:

| Token | Antes | Depois |
|---|---|---|
| Background principal | `#080808` | `#fafaf9` |
| Background secundário (cards) | `#0d0d0d` | `#ffffff` |
| Background destaque (margem) | `#0f0f0f` | `#fff7ed` |
| Bordas | `#1e1e1e` | `#e7e5e4` |
| Texto principal | `#ffffff` | `#1c1917` |
| Texto secundário | `#a3a3a3` | `#57534e` |
| Texto muted | `#525252` | `#a8a29e` |
| Acento laranja | `#f97316` | `#ea580c` |
| Sucesso (margem boa) | `#4ade80` | `#16a34a` |
| Alerta (margem ok) | `#facc15` | `#d97706` |
| Erro (margem ruim) | `#f87171` | `#dc2626` |

**Detalhe visual:** Cards com `border-left: 3px solid #ea580c` no lugar de backgrounds escuros. Sensação de relatório financeiro premium, estilo Stripe/Linear.

Configuração do Streamlit em `.streamlit/config.toml`:
```toml
[theme]
base = "light"
backgroundColor = "#fafaf9"
secondaryBackgroundColor = "#ffffff"
primaryColor = "#ea580c"
textColor = "#1c1917"
```

### 2. Fix de reset: `st.fragment`

Cada seção de formulário CRUD vira um `@st.fragment`. Quando o usuário cadastra ou edita um dado, apenas aquele fragmento re-executa — sem scroll pro topo, sem fechar expanders de outras seções.

**Padrão de implementação:**

```python
@st.fragment
def secao_adicionar_produto():
    with st.form("form_prod", clear_on_submit=True):
        # campos...
        if st.form_submit_button("Cadastrar"):
            inserir_produto(...)
            st.success("Cadastrado!")
            # sem st.rerun() — o fragment se atualiza sozinho

@st.fragment
def lista_produtos():
    produtos = listar_produtos()
    for p in produtos:
        with st.expander(...):
            # edição inline
```

**Regra:** `st.rerun()` só é mantido quando for necessário atualizar dados que estão **fora** do fragmento (ex: KPIs da home que dependem de vendas cadastradas em outra página). Nesse caso, usar `st.rerun(scope="app")`.

---

## Escopo de mudanças

| Arquivo | O que muda |
|---|---|
| `tools/styles.py` | Paleta completa, `aplicar_css()`, funções de componente |
| `.streamlit/config.toml` | Theme `base = "light"`, novas cores |
| `app.py` | Fragment para KPIs, novo CSS aplicado |
| `pages/01_Calculadora.py` | Tema atualizado, fragment para resultado |
| `pages/02_Produtos.py` | Fragments para lista, edição e cadastro (3 fragments) |
| `pages/03_Vendas.py` | Fragments para form de registro e histórico |
| `pages/04_PL.py` | Fragments para custos fixos e DRE |
| `pages/05_Dashboard.py` | Tema atualizado |

---

## O que NÃO muda

- Estrutura de dados (banco SQLite, tabelas, campos)
- Lógica de cálculo (`calcular_custo.py`, `calcular_margem.py`)
- Rotas e nomes das páginas
- Funcionalidades existentes

---

## Critérios de sucesso

- Cadastrar produto/material/impressora sem scroll pro topo
- Expander que estava aberto permanece aberto após edição
- Interface visualmente legível com fundo claro
- Nenhuma funcionalidade quebrada após a migração
