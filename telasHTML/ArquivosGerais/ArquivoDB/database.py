"""
Arquivo corrigido automaticamente por Gemini.
Baseado no arquivo original: futebol-gabriel/telasHTML/ArquivosGerais/ArquivoDB/database.py
"""

import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv
from datetime import date # NOVO IMPORT
import json

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
        def execute(self):
            class MockResponse:
                data = None
                error = {'message': 'Mock DB Error'}
            return MockResponse()
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

# database.py (Trecho da função register_user)

# ... (outras funções e imports)

def register_user(nome, email, senha, cidade, posicao, nascimento, numero): # <--- Parâmetro 'numero' incluído
    """
    Cadastra um novo usuário no banco de dados.
    """
    try:
        # Hash da senha
        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insere o usuário no banco.
        # CORREÇÃO CRÍTICA: O campo agora usa a chave 'numero', conforme solicitado.
        response = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha': hashed_password,
            'cidade': cidade,
            'posicao': posicao,
            'nascimento': nascimento,
            'numero': numero # <--- CHAVE CORRIGIDA!
        }).execute()
        
        if response.data:
            return True, "Cadastro realizado com sucesso!"
    
        else:
            # Tenta pegar a mensagem de erro detalhada do PostgREST
            error_details = response.error
            if error_details and error_details.get('code') == '23505':
                return False, "O email fornecido já está cadastrado."
            else:
                return False, f"Erro ao cadastrar: {error_details.get('message', 'Erro desconhecido')}"
            
    except Exception as e:
        error_info = str(e)
        print(f"ERRO em register_user: {error_info}")
        
        # Tenta extrair detalhes do erro (caso o erro não venha do response.error)
        try:
            error_details = json.loads(error_info)
            if error_details.get('code') == '23505':
                return False, "O email fornecido já está cadastrado."
            else:
                return False, f"Erro ao cadastrar: {error_details.get('message', 'Erro desconhecido')}"
        except:
            return False, "Erro desconhecido ao cadastrar."

def check_user(email, senha):
    """
    Verifica as credenciais do usuário.
    """
    try:
        response = supabase.table('usuarios').select('senha').eq('email', email).execute()
        
        if response.data and len(response.data) > 0:
            stored_hashed_password = response.data[0]['senha'].encode('utf-8')
            if bcrypt.checkpw(senha.encode('utf-8'), stored_hashed_password):
                return True
        return False
        
    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return False

def get_user_by_email(email):
    """
    Busca um usuário pelo email e adiciona a idade.
    """
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).execute()
        
        if response.data:
            user = response.data[0]
            if user.get('nascimento'):
                user['idade'] = calculate_age(user['nascimento'])
            else:
                user['idade'] = 'N/A'
            return user
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_email: {e}")
        return None

def get_all_users():
    """
    Busca e retorna todos os usuários.
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

def get_user_by_id(user_id):
    """
    Busca um usuário pelo ID
    """
    try:
        response = supabase.table('usuarios').select('*').eq('id', user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_id: {e}")
        return None

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
        return True
    except Exception as e:
        print(f"ERRO em update_user_profile: {e}")
        return False

def update_user_camisa(email, numero_camisa):
    """
    Atualiza o número da camisa do usuário
    """
    try:
        response = supabase.table('usuarios').update({
            'numero_camisa': numero_camisa
        }).eq('email', email).execute()
        return True
    except Exception as e:
        print(f"ERRO em update_user_camisa: {e}")
        return False