import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent.parent.parent / "data" / "vendas.db"

def initialize_database():
    """
    Cria/verifica o banco de dados e as tabelas 'vendedores' e 'produtos'.
    """
    DB_FILE.parent.mkdir(exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Tabela 1: Vendedores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
        """)

        # Tabela 2: Produtos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            vendedor_id INTEGER,
            FOREIGN KEY (vendedor_id) REFERENCES vendedores (id)
        )
        """)

        conn.commit()
        print(f"Banco de dados verificado/inicializado com sucesso em: {DB_FILE}")

    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

def add_seller(name):
    """
    Adiciona um novo vendedor ao banco de dados.
    Retorna True se for bem-sucedido, False em caso de erro.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vendedores (nome) VALUES (?)", (name,))
        conn.commit()
        print(f"Vendedor '{name}' adicionado com sucesso.")
        return True
    except sqlite3.IntegrityError:
        print(f"Erro: O vendedor '{name}' já existe.")
        return False
    except sqlite3.Error as e:
        print(f"Erro ao adicionar vendedor: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_sellers():
    """
    Busca todos os vendedores cadastrados no banco de dados.
    Retorna uma lista de tuplas (id, nome).
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM vendedores ORDER BY nome")
        sellers = cursor.fetchall()
        return sellers
    except sqlite3.Error as e:
        print(f"Erro ao buscar vendedores: {e}")
        return []
    finally:
        if conn:
            conn.close()