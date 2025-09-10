import sqlite3
from sqlite3 import Error

# Cria conexão com o banco de dados
def criar_conexao():
    conn = None
    try:
        conn = sqlite3.connect('database.db')  # Arquivo do banco de dados
        print("Conexão com SQLite estabelecida!")
        return conn
    except Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
    return conn

# Cria a tabela de usuários
def criar_tabela_usuarios():
    conn = criar_conexao()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                nome TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("Tabela 'usuarios' criada com sucesso!")
    except Error as e:
        print(f"Erro ao criar tabela: {e}")
    finally:
        if conn:
            conn.close()

# Insere um novo usuário
def inserir_usuario(nome, email, senha):
    conn = criar_conexao()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha))
        conn.commit()
        print("Usuário cadastrado com sucesso!")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erro ao cadastrar: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Chamada para criar a tabela automaticamente
if __name__ == "__main__":
    criar_tabela_usuarios()