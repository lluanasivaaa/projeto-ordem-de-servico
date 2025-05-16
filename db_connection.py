import mysql.connector
import hashlib

# ------------------- CONEXÃO -------------------

def conectar():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='2005',
            database='ordem_servico'
        )
        if conn.is_connected():
            print("✅ Conectado ao banco de dados com sucesso!")
            return conn
    except mysql.connector.Error as err:
        print(f"❌ Erro ao conectar: {err}")
        return None

# ------------------- CLIENTES -------------------

def listar_clientes(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, telefone FROM clientes;")
    clientes = cursor.fetchall()
    cursor.close()
    return clientes

def inserir_cliente(conn, nome, email, telefone):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)"
        cursor.execute(query, (nome, email, telefone))
        conn.commit()
        print(f"✅ Cliente '{nome}' inserido com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao inserir cliente: {err}")

# ------------------- ORDENS -------------------

def listar_ordens(conn):
    cursor = conn.cursor()
    query = """
        SELECT 
            o.id, 
            c.nome AS cliente_nome, 
            o.data_abertura, 
            o.status, 
            o.total
        FROM ordens o
        JOIN clientes c ON o.cliente_id = c.id
    """
    cursor.execute(query)
    ordens = cursor.fetchall()
    cursor.close()
    return ordens

def inserir_ordem(conn, cliente_id, data_abertura, status):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO ordens (cliente_id, data_abertura, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (cliente_id, data_abertura, status))
        conn.commit()
        print(f"✅ Ordem inserida com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao inserir ordem: {err}")

def atualizar_ordem(conn, ordem_id, cliente_id=None, data_abertura=None, status=None, total=None):
    try:
        cursor = conn.cursor()
        campos = []
        valores = []
        if cliente_id is not None:
            campos.append("cliente_id = %s")
            valores.append(cliente_id)
        if data_abertura is not None:
            campos.append("data_abertura = %s")
            valores.append(data_abertura)
        if status is not None:
            campos.append("status = %s")
            valores.append(status)
        if total is not None:
            campos.append("total = %s")
            valores.append(total)
        if not campos:
            print("⚠️ Nada para atualizar na ordem.")
            cursor.close()
            return
        valores.append(ordem_id)
        query = f"UPDATE ordens SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        print(f"✅ Ordem ID {ordem_id} atualizada com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao atualizar ordem: {err}")

def deletar_ordem(conn, ordem_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM servicos WHERE ordem_id = %s", (ordem_id,))
        cursor.execute("DELETE FROM itens WHERE ordem_id = %s", (ordem_id,))
        cursor.execute("DELETE FROM ordens WHERE id = %s", (ordem_id,))
        conn.commit()
        print(f"✅ Ordem ID {ordem_id} e seus serviços e itens deletados com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao deletar ordem: {err}")

# ------------------- SERVIÇOS -------------------

def inserir_servico(conn, ordem_id, descricao, valor):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO servicos (ordem_id, descricao, valor) VALUES (%s, %s, %s)"
        cursor.execute(query, (ordem_id, descricao, valor))
        conn.commit()
        print(f"✅ Serviço '{descricao}' inserido na ordem ID {ordem_id} com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao inserir serviço: {err}")

def listar_servicos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, ordem_id, descricao, valor FROM servicos;")
    servicos = cursor.fetchall()
    cursor.close()
    return servicos

def atualizar_servico(conn, servico_id, descricao=None, valor=None):
    try:
        cursor = conn.cursor()
        campos = []
        valores = []
        if descricao is not None:
            campos.append("descricao = %s")
            valores.append(descricao)
        if valor is not None:
            campos.append("valor = %s")
            valores.append(valor)
        if not campos:
            print("⚠️ Nada para atualizar no serviço.")
            cursor.close()
            return
        valores.append(servico_id)
        query = f"UPDATE servicos SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        print(f"✅ Serviço ID {servico_id} atualizado com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao atualizar serviço: {err}")

def deletar_servico(conn, servico_id):
    try:
        cursor = conn.cursor()
        query = "DELETE FROM servicos WHERE id = %s"
        cursor.execute(query, (servico_id,))
        conn.commit()
        print(f"✅ Serviço ID {servico_id} deletado com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao deletar serviço: {err}")

# ------------------- ITENS -------------------

def inserir_item(conn, ordem_id, nome, quantidade, preco_unitario):
    try:
        cursor = conn.cursor()
        query = "INSERT INTO itens (ordem_id, nome, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (ordem_id, nome, quantidade, preco_unitario))
        conn.commit()
        print(f"✅ Item '{nome}' inserido na ordem ID {ordem_id} com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao inserir item: {err}")

def listar_itens(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, ordem_id, nome, quantidade, preco_unitario FROM itens;")
    itens = cursor.fetchall()
    cursor.close()
    return itens

def atualizar_item(conn, item_id, nome=None, quantidade=None, preco_unitario=None):
    try:
        cursor = conn.cursor()
        campos = []
        valores = []
        if nome is not None:
            campos.append("nome = %s")
            valores.append(nome)
        if quantidade is not None:
            campos.append("quantidade = %s")
            valores.append(quantidade)
        if preco_unitario is not None:
            campos.append("preco_unitario = %s")
            valores.append(preco_unitario)
        if not campos:
            print("⚠️ Nada para atualizar no item.")
            cursor.close()
            return
        valores.append(item_id)
        query = f"UPDATE itens SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        print(f"✅ Item ID {item_id} atualizado com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao atualizar item: {err}")

def deletar_item(conn, item_id):
    try:
        cursor = conn.cursor()
        query = "DELETE FROM itens WHERE id = %s"
        cursor.execute(query, (item_id,))
        conn.commit()
        print(f"✅ Item ID {item_id} deletado com sucesso!")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao deletar item: {err}")

# ------------------- ATUALIZAR TOTAL -------------------

def atualizar_total_ordem(conn, ordem_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT IFNULL(SUM(valor),0) FROM servicos WHERE ordem_id = %s", (ordem_id,))
        total_servicos = cursor.fetchone()[0]

        cursor.execute("SELECT IFNULL(SUM(quantidade * preco_unitario),0) FROM itens WHERE ordem_id = %s", (ordem_id,))
        total_itens = cursor.fetchone()[0]

        total = total_servicos + total_itens

        cursor.execute("UPDATE ordens SET total = %s WHERE id = %s", (total, ordem_id))
        conn.commit()
        print(f"💰 Total da ordem ID {ordem_id} atualizado para R$ {total:.2f}")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Erro ao atualizar total da ordem: {err}")

# ------------------- USUÁRIO -------------------

def validar_usuario(conn, usuario, senha):
    cursor = conn.cursor(buffered=True)
    senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    query = "SELECT id FROM usuarios WHERE usuario = %s AND senha = %s"
    cursor.execute(query, (usuario, senha_hash))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None
#luana comentário