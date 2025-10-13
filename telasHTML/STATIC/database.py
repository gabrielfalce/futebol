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
    raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram definidas.")

# Configuração do cliente Supabase
supabase: Client = create_client(url, key)

def register_user(nome, email, senha, cidade, numero, posicao, data_nasc):
    """Regista um novo utilizador no banco de dados com senha encriptada."""
    try:
        user_exists = supabase.table('usuarios').select('id').eq('email', email).execute()
        if user_exists.data:
            return False, "Este email já está registado."

        # Encripta a senha antes de guardar
        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        
        data, count = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha': hashed_password.decode('utf-8'),
            'cidade': cidade,
            'numero': numero,
            'posicao': posicao,
            'nascimento': data_nasc # <<< CORREÇÃO: Usando o nome correto da coluna
        }).execute()
        
        return True, "Utilizador registado com sucesso!"
        
    except Exception as e:
        print(f"Erro ao registar utilizador: {e}")
        return False, f"Ocorreu um erro inesperado: {e}"

def check_user(email, password):
    """Verifica se um utilizador existe e se a senha está correta."""
    try:
        user_data = supabase.table('usuarios').select('senha').eq('email', email).execute()
        
        if not user_data.data:
            return False

        # Verifica a senha encriptada
        hashed_password = user_data.data[0]['senha'].encode('utf-8')
        
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Erro ao verificar utilizador: {e}")
        return False

# --- FUNÇÕES ADICIONADAS PARA LISTAGEM E BUSCA ---

def get_all_users():
    """Recupera todos os usuários do banco de dados, excluindo a senha."""
    try:
        response = supabase.table('usuarios').select('nome, cidade, email').order('nome', desc=False).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao obter todos os usuários: {e}")
        return []

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
