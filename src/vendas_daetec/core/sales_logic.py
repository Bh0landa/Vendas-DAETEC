import sqlite3
import datetime
from pathlib import Path

# Configuração do Caminho do Banco de Dados
DB_PATH = Path(__file__).parent.parent.parent / "data" / "planilhas.db"

def initialize_database():
    """
    Cria/verifica o banco de dados e as tabelas 'vendedores' e 'produtos'.
    """
    
    # Garante que o diretório para o banco de dados exista
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = None
    
    # Criação das tabelas necessárias para a aplicação
    try:
        conn = sqlite3.connect(DB_PATH)
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
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            vendedor_id INTEGER,
            FOREIGN KEY (vendedor_id) REFERENCES vendedores (id)
        )
        """)

        # Tabela 3: Vendas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            valor_total REAL NOT NULL,
            data_venda TEXT NOT NULL,
            FOREIGN KEY (vendedor_id) REFERENCES vendedores (id)
        )
        """)

        # Tabela 4: Itens da Venda
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS venda_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario_na_venda REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        """)

        # Tabela 5: Pagamentos da Venda
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS venda_pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            metodo TEXT NOT NULL,
            valor REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id)
        )
        """)

        # Tabela 6: Configurações da Aplicação
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
        """)

        # Confirma as alterações no banco de dados
        conn.commit()
        print(f"Banco de dados verificado/inicializado com sucesso em: {DB_PATH}")

    # Tratamento de erros específicos do SQLite
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    
    # Fechamento da conexão com o banco de dados
    finally:
        if conn:
            conn.close()

def add_seller(name):
    """
    Adiciona um novo vendedor ao banco de dados.
    """
    
    # Tenta inserir um novo vendedor
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Padroniza o nome para ter a primeira letra de cada palavra em maiúsculo
        name = name.strip().title()

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

def delete_seller(seller_id):
    """
    Remove um vendedor do banco de dados pelo ID.
    Retorna True em caso de sucesso, uma mensagem de erro específica em caso de falha.
    """
    
    # Tenta deletar um vendedor
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM vendedores WHERE id = ?", (seller_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True
        
        else:
            return "not_found"
    
    except sqlite3.IntegrityError:
        return "constraint_failed"
    
    except sqlite3.Error as e:
        print(f"Erro ao deletar vendedor: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def get_all_sellers():
    """
    Busca todos os vendedores cadastrados no banco de dados.
    Retorna uma lista de tuplas (id, nome).
    """
    
    # Busca todos os vendedores
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM vendedores ORDER BY id")
        sellers = cursor.fetchall()
        return sellers
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar vendedores: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def add_product(name, price, seller_id):
    """
    Adiciona um novo produto ao banco de dados.
    """
    
    # Gera um ID único para o produto
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM produtos WHERE id LIKE 'PROD-%' ORDER BY id DESC LIMIT 1")
        last_id = cursor.fetchone()

        if last_id:
            last_number = int(last_id[0].split('-')[1])
            new_product_id = f"PROD-{last_number + 1:04d}"
        
        else:
            new_product_id = "PROD-0001"

        cursor.execute("INSERT INTO produtos (id, nome, preco, vendedor_id) VALUES (?, ?, ?, ?)", (new_product_id, name, price, seller_id))
        conn.commit()
        print(f"Produto '{name}' adicionado com sucesso com o ID {new_product_id}.")
        return True
    
    except sqlite3.Error as e:
        print(f"Erro ao adicionar produto: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def delete_product(product_id):
    """
    Remove um produto do banco de dados pelo seu ID.
    """
    
    # Tenta deletar um produto
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Produto com ID {product_id} deletado com sucesso.")
            return True
        else:
            print(f"Nenhum produto encontrado com ID {product_id}.")
            return False
            
    except sqlite3.Error as e:
        print(f"Erro ao deletar produto: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def get_all_products():
    """
    Busca todos os produtos com os nomes dos vendedores correspondentes.
    Retorna uma lista de tuplas (nome_vendedor, id_produto, nome_produto, preco).
    """
    
    # Busca todos os produtos junto com o nome do vendedor
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Consulta SQL para buscar os produtos junto com o nome do vendedor
        sql_query = """
        SELECT
            v.nome,
            p.id,
            p.nome,
            p.preco
        FROM produtos p
        JOIN vendedores v ON p.vendedor_id = v.id
        ORDER BY v.nome, p.id;
        """

        cursor.execute(sql_query)
        products = cursor.fetchall()
        return products
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar produtos: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def get_products_by_seller(seller_id):
    """
    Busca todos os produtos de um vendedor específico.
    Retorna uma lista de tuplas (id_produto, nome_produto, preco).
    """
    
    # Busca os produtos de um vendedor específico
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, preco FROM produtos WHERE vendedor_id = ? ORDER BY nome", (seller_id,))
        products = cursor.fetchall()
        return products
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar produtos por vendedor: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def get_product_details(product_id):
    """
    Busca os detalhes de um único produto pelo seu ID.
    Retorna uma tupla (id, nome, preco) ou None se não for encontrado.
    """
    
    # Busca os detalhes de um produto específico
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, preco FROM produtos WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        return product
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes do produto: {e}")
        return None
    
    finally:
        if conn:
            conn.close()

def get_config(chave):
    """
    Busca o valor de uma configuração específica.
    Retorna '0.0' se a chave não for encontrada.
    """
    
    # Busca o valor de uma configuração específica
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else '0.0'
    
    except sqlite3.Error as e:
        print(f"Erro ao buscar configuração '{chave}': {e}")
        return '0.0'
    
    finally:
        if conn:
            conn.close()

def set_config(chave, valor):
    """
    Salva ou atualiza o valor de uma configuração.
    """
    
    # Tenta salvar ou atualizar o valor de uma configuração
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))
        conn.commit()
        return True
    
    except sqlite3.Error as e:
        print(f"Erro ao salvar configuração '{chave}': {e}")
        return False
    
    finally:
        if conn:
            conn.close()

def register_sale(vendedor_id, valor_total, cart_items, payments):
    """
    Registra uma venda completa no banco de dados usando uma transação.
    
    :param vendedor_id: ID do vendedor.
    :param valor_total: Valor total da venda (soma dos produtos).
    :param cart_items: Lista de dicionários, cada um representando um item no carrinho.
                       Ex: [{'produto_id': 'PROD-0001', 'quantidade': 2, 'preco_unitario': 10.0}, ...]
    :param payments: Lista de dicionários, cada um representando um pagamento.
                     Ex: [{'metodo': 'Pix', 'valor': 20.0}, ...]
    """
    
    # Registra uma venda completa usando uma transação para garantir integridade dos dados
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # 1. Inserir na tabela 'vendas' (o recibo geral)
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO vendas (vendedor_id, valor_total, data_venda) VALUES (?, ?, ?)",
            (vendedor_id, valor_total, data_atual)
        )
        
        # Pega o ID da venda que acabamos de criar
        venda_id = cursor.lastrowid

        # 2. Inserir na tabela 'venda_itens' (os produtos do carrinho)
        itens_para_inserir = []
        
        for item in cart_items:
            itens_para_inserir.append(
                (venda_id, item['produto_id'], item['quantidade'], item['preco_unitario'])
            )
        cursor.executemany(
            "INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario_na_venda) VALUES (?, ?, ?, ?)",
            itens_para_inserir
        )

        # 3. Inserir na tabela 'venda_pagamentos' (os pagamentos)
        pagamentos_para_inserir = []
        
        for pagamento in payments:
            pagamentos_para_inserir.append(
                (venda_id, pagamento['metodo'], pagamento['valor'])
            )
        cursor.executemany(
            "INSERT INTO venda_pagamentos (venda_id, metodo, valor) VALUES (?, ?, ?)",
            pagamentos_para_inserir
        )

        # Confirma todas as operações se tudo deu certo
        conn.commit()
        print(f"Venda ID {venda_id} registrada com sucesso!")
        return True

    except sqlite3.Error as e:
        print(f"Erro ao registrar venda. A transação foi revertida. Erro: {e}")
        
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()

def generate_sales_report():
    """
    Busca todos os dados de vendas e gera uma string de relatório formatado.
    """
    
    # Gera um relatório geral de vendas
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT v.id, v.nome
            FROM vendedores v
            JOIN vendas ON v.id = vendas.vendedor_id
            ORDER BY v.nome
        """)
        vendedores = cursor.fetchall()

        if not vendedores:
            return "Nenhuma venda registrada para gerar relatório."

        report_lines = [
            "=====================================",
            "      RELATÓRIO GERAL DE VENDAS      ",
            "=====================================",
            ""
        ]

        # 2. Para cada vendedor, buscar seus dados
        for vendedor_id, vendedor_nome in vendedores:
            report_lines.append("-------------------------------------")
            report_lines.append(f"VENDEDOR: {vendedor_nome}")
            report_lines.append("-------------------------------------")
            report_lines.append("")

            # 3. Buscar produtos vendidos pelo vendedor
            cursor.execute("""
                SELECT p.id, p.nome, SUM(vi.quantidade)
                FROM venda_itens vi
                JOIN vendas v ON vi.venda_id = v.id
                JOIN produtos p ON vi.produto_id = p.id
                WHERE v.vendedor_id = ?
                GROUP BY p.id, p.nome
                ORDER BY p.nome
            """, (vendedor_id,))
            produtos_vendidos = cursor.fetchall()

            report_lines.append("  PRODUTOS VENDIDOS:")
            
            if not produtos_vendidos:
                report_lines.append("    - Nenhum produto vendido neste período.")
            
            else:
                for prod_id, prod_nome, quantidade in produtos_vendidos:
                    report_lines.append(f"    - [{prod_id}] {prod_nome}: {quantidade} unidade(s)")
            
            report_lines.append("")

            # 4. Buscar resumo de pagamentos para o vendedor
            cursor.execute("""
                SELECT vp.metodo, SUM(vp.valor)
                FROM venda_pagamentos vp
                JOIN vendas v ON vp.venda_id = v.id
                WHERE v.vendedor_id = ?
                GROUP BY vp.metodo
                ORDER BY vp.metodo
            """, (vendedor_id,))
            pagamentos = cursor.fetchall()
            
            total_recebido = 0
            report_lines.append("  RESUMO DE PAGAMENTOS:")
            
            if not pagamentos:
                report_lines.append("    - Nenhum pagamento registrado.")
            
            else:
                for metodo, valor in pagamentos:
                    total_recebido += valor
                    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    report_lines.append(f"    - {metodo}: {valor_formatado}")
            
            total_formatado = f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            report_lines.append(f"    - TOTAL RECEBIDO: {total_formatado}")
            report_lines.append("")

        return "\n".join(report_lines)

    except sqlite3.Error as e:
        print(f"Erro ao gerar relatório: {e}")
        return f"Erro ao gerar relatório: {e}"
    
    finally:
        if conn:
            conn.close()

def clear_sales_data():
    """
    Remove todos os registros das tabelas relacionadas a vendas.
    Mantém vendedores e produtos intactos.
    """
    
    # Limpa todos os dados relacionados a vendas, mantendo vendedores e produtos
    conn = None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM venda_pagamentos")
        cursor.execute("DELETE FROM venda_itens")
        cursor.execute("DELETE FROM vendas")
        
        conn.commit()
        return True
    
    except sqlite3.Error as e:
        print(f"Erro ao limpar dados de vendas: {e}")
        return False
    
    finally:
        if conn:
            conn.close()