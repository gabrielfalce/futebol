"""
Arquivo corrigido automaticamente por ChatGPT — revisão conservadora.
Arquivo original: futebol-gabriel/telasHTML/ArquivosGerais/ArquivoDB/database.py
Não removi a lógica original; apenas apliquei limpeza e renomeações seguras.
"""

import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv
from datetime import date # NOVO IMPORT

load_dotenv()

# Configuração do Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Garante que as variáveis de ambiente foram carregadas
if not url or not key:
    print("ERRO: SUPABASE_URL ou SUPABASE_KEY não encontrados no ambiente.")
    # Permite que o app.py inicie, mas as funções de DB falharão
    url = "http://mock-url"
    key = "mock-key"

try:
    supabase: Client = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado.")
except Exception as e:
    print(f"ERRO ao inicializar o Cliente Supabase: {e}")
    # Cria um cliente mock para que o resto do código possa ser executado sem erro, mas as chamadas falharão.
    class MockSupabaseClient:
        def table(self, name): return self
        def insert(self, data): return self
        def select(self, columns): return self
        def eq(self, column, value): return self
        def execute(self): return type('MockResponse', (object,), {'data': []})()
        def update(self, data): return self
    supabase = MockSupabaseClient()


# === FUNÇÃO HELPER PARA CÁLCULO DE IDADE ===
def calculate_age(born):
    """
    Calcula a idade a partir da data de nascimento (string 'AAAA-MM-DD').
    """
    today = date.today()
    try:
        # Converte a string do DB para objeto date
        born_date = date.fromisoformat(born) 
    except (ValueError, TypeError):
        return 'N/A' # Retorna N/A se a data for inválida ou nula
        
    # Lógica de cálculo da idade
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))

# === FUNÇÕES DO SUPABASE ===
def register_user(nome, email, senha_hash, cidade, posicao, data_nasc, numero):
    """
    Registra um novo usuário no banco de dados
    data_nasc deve estar no formato 'AAAA-MM-DD'
    """
    try:
        # 1. Verifica se o email já existe
        response_check = supabase.table('usuarios').select('email').eq('email', email).execute()
        if response_check.data:
            return False, "Erro: Este e-mail já está cadastrado."
            
        # 2. Insere o novo usuário
        response = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha_hash': senha_hash,
            'cidade': cidade,
            'posicao': posicao,
            'nascimento': data_nasc,  # Coluna: nascimento (AAAA-MM-DD)
            'numero': numero,         # Coluna: numero (telefone)
            'numero_camisa': None,    # NOVO: numero_camisa
            'foto_perfil': None,      # NOVO: Caminho da imagem de perfil
            'foto_capa': None         # NOVO: Caminho da imagem de capa
        }).execute()
        
        if response.data:
            return True, "Usuário cadastrado com sucesso!"
        else:
            return False, "Erro ao cadastrar usuário (Sem dados de retorno)."
            
    except Exception as e:
        print(f"ERRO em register_user: {e}")
        return False, "Erro ao cadastrar usuário. Tente novamente mais tarde."

def check_user(email, senha):
    """
    Verifica as credenciais do usuário.
    """
    try:
        # 1. Busca o usuário pelo email
        response = supabase.table('usuarios').select('id, nome, email, senha_hash, foto_perfil').eq('email', email).execute()
        
        if not response.data:
            return None  # Usuário não encontrado

        user_data = response.data[0]
        senha_hash = user_data['senha_hash'].encode('utf-8')
        
        # 2. Verifica a senha
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
            return user_data
        else:
            return None  # Senha incorreta
            
    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return None

def get_user_by_email(email):
    """
    Busca todos os dados de um usuário pelo email.
    Também adiciona o campo 'idade'.
    """
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).execute()
        if response.data:
            user = response.data[0]
            # Adiciona o campo 'idade'
            if user.get('nascimento'):
                user['idade'] = calculate_age(user['nascimento'])
            else:
                user['idade'] = 'N/A'
            
            return user
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_email: {e}")
        return None

def get_user_by_id(user_id):
    """
    Busca todos os dados de um usuário pelo ID.
    Também adiciona o campo 'idade'.
    """
    try:
        response = supabase.table('usuarios').select('*').eq('id', user_id).execute()
        if response.data:
            user = response.data[0]
            # Adiciona o campo 'idade'
            if user.get('nascimento'):
                user['idade'] = calculate_age(user['nascimento'])
            else:
                user['idade'] = 'N/A'
            
            return user
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_id: {e}")
        return None

def get_all_users():
    """
    Busca todos os usuários.
    """
    try:
        # Seleciona apenas os campos essenciais
        response = supabase.table('usuarios').select('id, nome, cidade, posicao, foto_perfil, nascimento').execute()
        if response.data:
            users = response.data
            # Adiciona a idade para cada usuário
            for user in users:
                if user.get('nascimento'):
                    user['idade'] = calculate_age(user['nascimento'])
                else:
                    user['idade'] = 'N/A'
            return users
        return []
    except Exception as e:
        print(f"ERRO em get_all_users: {e}")
        return []

def update_user_profile_image(email, foto_perfil_path):
    """
    Atualiza o caminho da foto de perfil do usuário.
    """
    try:
        response = supabase.table('usuarios').update({
            'foto_perfil': foto_perfil_path
        }).eq('email', email).execute()
        
        return bool(response.data)
        
    except Exception as e:
        print(f"ERRO em update_user_profile_image: {e}")
        return False

def update_user_profile(email, **update_data):
    """
    Atualiza o perfil do usuário com dados dinâmicos.
    """
    try:
        response = supabase.table('usuarios').update(update_data).eq('email', email).execute()
        
        return bool(response.data)
        
    except Exception as e:
        print(f"ERRO em update_user_profile: {e}")
        return False