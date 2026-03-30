import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "negocio.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS impressoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            custo_aquisicao REAL NOT NULL,
            vida_util_horas REAL NOT NULL,
            consumo_watts REAL NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('filamento', 'resina')),
            custo_por_kg REAL NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            material_id INTEGER NOT NULL REFERENCES materiais(id),
            impressora_id INTEGER NOT NULL REFERENCES impressoras(id),
            peso_material_g REAL NOT NULL,
            tempo_impressao_h REAL NOT NULL,
            tempo_pos_proc_h REAL NOT NULL DEFAULT 0,
            custo_mao_obra_h REAL NOT NULL DEFAULT 0,
            preco_venda REAL NOT NULL,
            observacoes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            data DATE NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            preco_unit REAL NOT NULL,
            canal TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS custos_fixos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL,
            periodo TEXT NOT NULL CHECK(periodo IN ('mensal', 'anual'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS custos_produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL DEFAULT 'outro',
            tipo TEXT NOT NULL CHECK(tipo IN ('fixo', 'percentual')),
            valor REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ── Impressoras ──────────────────────────────────────────────────────────────

def listar_impressoras():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM impressoras ORDER BY nome")]


def inserir_impressora(nome, custo_aquisicao, vida_util_horas, consumo_watts):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO impressoras (nome, custo_aquisicao, vida_util_horas, consumo_watts) VALUES (?,?,?,?)",
            (nome, custo_aquisicao, vida_util_horas, consumo_watts),
        )


def atualizar_impressora(id_, nome, custo_aquisicao, vida_util_horas, consumo_watts):
    with get_conn() as conn:
        conn.execute(
            "UPDATE impressoras SET nome=?, custo_aquisicao=?, vida_util_horas=?, consumo_watts=? WHERE id=?",
            (nome, custo_aquisicao, vida_util_horas, consumo_watts, id_),
        )


def deletar_impressora(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM impressoras WHERE id=?", (id_,))


# ── Materiais ────────────────────────────────────────────────────────────────

def listar_materiais():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM materiais ORDER BY nome")]


def inserir_material(nome, tipo, custo_por_kg):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO materiais (nome, tipo, custo_por_kg) VALUES (?,?,?)",
            (nome, tipo, custo_por_kg),
        )


def atualizar_material(id_, nome, tipo, custo_por_kg):
    with get_conn() as conn:
        conn.execute(
            "UPDATE materiais SET nome=?, tipo=?, custo_por_kg=? WHERE id=?",
            (nome, tipo, custo_por_kg, id_),
        )


def deletar_material(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM materiais WHERE id=?", (id_,))


# ── Produtos ─────────────────────────────────────────────────────────────────

def listar_produtos():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT p.*, m.nome AS material_nome, m.custo_por_kg,
                   i.nome AS impressora_nome, i.custo_aquisicao,
                   i.vida_util_horas, i.consumo_watts
            FROM produtos p
            JOIN materiais m ON p.material_id = m.id
            JOIN impressoras i ON p.impressora_id = i.id
            ORDER BY p.nome
        """)]


def inserir_produto(nome, material_id, impressora_id, peso_material_g,
                    tempo_impressao_h, tempo_pos_proc_h, custo_mao_obra_h,
                    preco_venda, observacoes=""):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO produtos
              (nome, material_id, impressora_id, peso_material_g,
               tempo_impressao_h, tempo_pos_proc_h, custo_mao_obra_h,
               preco_venda, observacoes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (nome, material_id, impressora_id, peso_material_g,
              tempo_impressao_h, tempo_pos_proc_h, custo_mao_obra_h,
              preco_venda, observacoes))


def atualizar_produto(id_, nome, material_id, impressora_id, peso_material_g,
                      tempo_impressao_h, tempo_pos_proc_h, custo_mao_obra_h,
                      preco_venda, observacoes=""):
    with get_conn() as conn:
        conn.execute("""
            UPDATE produtos SET nome=?, material_id=?, impressora_id=?,
              peso_material_g=?, tempo_impressao_h=?, tempo_pos_proc_h=?,
              custo_mao_obra_h=?, preco_venda=?, observacoes=?
            WHERE id=?
        """, (nome, material_id, impressora_id, peso_material_g,
              tempo_impressao_h, tempo_pos_proc_h, custo_mao_obra_h,
              preco_venda, observacoes, id_))


def deletar_produto(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM produtos WHERE id=?", (id_,))


# ── Vendas ───────────────────────────────────────────────────────────────────

def listar_vendas(data_ini=None, data_fim=None):
    sql = """
        SELECT v.*, p.nome AS produto_nome
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE 1=1
    """
    params = []
    if data_ini:
        sql += " AND v.data >= ?"
        params.append(str(data_ini))
    if data_fim:
        sql += " AND v.data <= ?"
        params.append(str(data_fim))
    sql += " ORDER BY v.data DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, params)]


def inserir_venda(produto_id, data, quantidade, preco_unit, canal=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO vendas (produto_id, data, quantidade, preco_unit, canal) VALUES (?,?,?,?,?)",
            (produto_id, str(data), quantidade, preco_unit, canal),
        )


def deletar_venda(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM vendas WHERE id=?", (id_,))


# ── Custos Fixos ─────────────────────────────────────────────────────────────

def listar_custos_fixos():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM custos_fixos ORDER BY nome")]


def inserir_custo_fixo(nome, valor, periodo):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO custos_fixos (nome, valor, periodo) VALUES (?,?,?)",
            (nome, valor, periodo),
        )


def atualizar_custo_fixo(id_, nome, valor, periodo):
    with get_conn() as conn:
        conn.execute(
            "UPDATE custos_fixos SET nome=?, valor=?, periodo=? WHERE id=?",
            (nome, valor, periodo, id_),
        )


def deletar_custo_fixo(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM custos_fixos WHERE id=?", (id_,))


# ── Custos Adicionais por Produto ────────────────────────────────────────────

CATEGORIAS_CUSTO = ["embalagem", "frete", "taxa_plataforma", "imposto", "outro"]

def listar_custos_produto(produto_id):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM custos_produto WHERE produto_id=? ORDER BY categoria, nome",
            (produto_id,)
        )]


def inserir_custo_produto(produto_id, nome, categoria, tipo, valor):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO custos_produto (produto_id, nome, categoria, tipo, valor) VALUES (?,?,?,?,?)",
            (produto_id, nome, categoria, tipo, valor),
        )


def atualizar_custo_produto(id_, nome, categoria, tipo, valor):
    with get_conn() as conn:
        conn.execute(
            "UPDATE custos_produto SET nome=?, categoria=?, tipo=?, valor=? WHERE id=?",
            (nome, categoria, tipo, valor, id_),
        )


def deletar_custo_produto(id_):
    with get_conn() as conn:
        conn.execute("DELETE FROM custos_produto WHERE id=?", (id_,))


if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso.")
