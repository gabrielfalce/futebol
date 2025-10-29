# /home/ubuntu/futebol-main/futebol-main/telasHTML/STATIC/database.py
import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env para o ambiente
load_dotenv() 

# Lê as credenciais a partir das variáveis de ambiente
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Verifica se as variáveis foram carregadas corretamente
if not url or not key:
    # Use as variáveis de ambiente corretas para o Render (se forem diferentes)
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    if not url or not key:
        print("Aviso: As variáveis de ambiente SUPABASE_URL/KEY não foram encontradas via .env ou env padrão.")

# Configuração do cliente Supabase
supabase: Client = create_client(url, key)

def register_user(nome, email, senha_hash, cidade, numero, posicao, data_nasc):
    """Regista um novo utilizador no banco de dados com senha encriptada."""
    try:
        user_exists = supabase.table('usuarios').select('id').eq('email', email).execute()
        if user_exists.data:
            return False, "Este email já está registado."

        # A senha já deve vir encriptada do app.py
        
        data, count = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha': senha_hash.decode('utf-8'),
            'cidade': cidade,
            'numero': numero,
            'posicao': posicao,
            'nascimento': data_nasc # <<< CORREÇÃO: Coluna Supabase é 'nascimento'
        }).execute()
        
        return True, "Utilizador registado com sucesso!"
        
    except Exception as e:
        print(f"Erro ao registar utilizador: {e}")
        return False, f"Ocorreu um erro inesperado: {e}"

def check_user(email, password_text):
    """Verifica se um utilizador existe e se a senha está correta."""
    try:
        user_data = supabase.table('usuarios').select('senha, id, nome, email, cidade, numero, posicao, nascimento').eq('email', email).execute()
        
        if not user_data.data:
            return False

        # Verifica a senha encriptada
        hashed_password = user_data.data[0]['senha'].encode('utf-8')
        
        if bcrypt.checkpw(password_text.encode('utf-8'), hashed_password):
            # Retorna os dados do usuário se a senha estiver correta
            return user_data.data[0]
        else:
            return False
            
    except Exception as e:
        print(f"Erro ao verificar utilizador: {e}")
        return False


# --- FUNÇÕES PARA LISTAGEM E BUSCA ---

def get_all_users():
    """Recupera todos os usuários do banco de dados, excluindo a senha."""
    try:
        response = supabase.table('usuarios').select('nome, cidade, email').order('nome', desc=False).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao obter todos os usuários: {e}")
        return []

def get_user_by_email(email):
    """Recupera os dados de um usuário pelo email."""
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Erro ao obter usuário por email: {e}")
        return None

def search_users(query):
    """Busca usuários pelo nome ou cidade."""
    try:
        response = supabase.table('usuarios').select('nome, cidade, email').or_(
            f'nome.ilike.%{query}%', 
            f'cidade.ilike.%{query}%'
        ).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return []
