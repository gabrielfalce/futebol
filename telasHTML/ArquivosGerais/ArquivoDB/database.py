"""
Arquivo corrigido automaticamente por ChatGPT — revisão conservadora.
Arquivo original: futebol-gabriel/telasHTML/ArquivosGerais/ArquivoDB/database.py
Não removi a lógica original; apenas apliquei limpeza e renomeações seguras.
"""

import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv
from datetime import date, datetime # NOVO IMPORT: Adicionado 'datetime'

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
        def update(self, data): return self
        def execute(self): 
            class MockResponse:
                data = None
                def json(self): return "{'message': 'Mock Supabase call failed'}"
            return MockResponse()
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

def check_user(email):
    """
    Verifica se um usuário com o email fornecido já existe no banco.
    """
    try:
        response = supabase.table('usuarios').select('email').eq('email', email).execute()
        return bool(response.data)
    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return False # Retorna Falso em caso de erro

def register_user(nome, email, senha, cidade, posicao, nascimento, numero):
    """
    Registra um novo usuário no banco de dados.
    """
    # 1. Checagem de usuário
    if check_user(email):
        print("ERRO em register_user: Usuário já existe.")
        return False

    # 2. Hashing da senha
    hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    # 3. Formatação da data de nascimento (necessária para o Supabase)
    try:
        # Tenta DD/MM/AAAA (Formato do HTML)
        date_obj = datetime.strptime(nascimento, '%d/%m/%Y')
    except ValueError:
        try:
            # Tenta AAAA-MM-DD (Formato alternativo)
            date_obj = datetime.strptime(nascimento, '%Y-%m-%d')
        except ValueError:
            print("ERRO em register_user: Formato de data de nascimento inválido.")
            return False
    
    formatted_nascimento = date_obj.strftime('%Y-%m-%d') # Salva no formato SQL

    # 4. Definição dos dados para inserção (CORREÇÃO APLICADA AQUI)
    data = {
        'nome': nome,
        'email': email,
        'senha_hash': hashed_password.decode('utf-8'),
        'cidade': cidade,
        'posicao': posicao,
        'data_nascimento': formatted_nascimento,
        'numero_telefone': numero,
        'foto_perfil': None, # Inicializa a foto de perfil como nula (se a coluna existir e for nula)
        # REMOVIDA: 'foto_capa': None, <--- REMOVIDO PARA CORRIGIR O ERRO PGRST204
    }

    try:
        # Tenta a inserção
        response = supabase.table('usuarios').insert(data).execute()
        if response.data:
            return True
        else:
            print(f"ERRO em register_user: Falha na inserção, resposta: {response.json()}")
            return False
    except Exception as e:
        # Este é o print que estava gerando o erro no log
        print(f"ERRO em register_user: {e}") 
        return False

def get_user_by_email(email):
    """
    Busca um usuário pelo email
    """
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).execute()
        if response.data:
            user = response.data[0]
            # Adiciona a idade
            if user.get('data_nascimento'):
                user['idade'] = calculate_age(user['data_nascimento'])
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
        # A resposta do Supabase tem que ser verificada para garantir que a atualização ocorreu
        return bool(response.data) 
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