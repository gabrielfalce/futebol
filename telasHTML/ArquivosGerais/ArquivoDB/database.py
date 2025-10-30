import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv
from datetime import date 

load_dotenv()

# Configuração do Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Garante que as variáveis de ambiente foram carregadas
if not url or not key:
    print("ERRO: SUPABASE_URL ou SUPABASE_KEY não encontrados no ambiente.")
    url = "http://mock-url"
    key = "mock-key"

try:
    supabase: Client = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado.")
except Exception as e:
    print(f"ERRO ao inicializar o Cliente Supabase: {e}")
    # Cliente Mock para evitar que o código quebre na inicialização, se o Supabase falhar.
    class MockSupabaseClient:
        def table(self, name): return self
        def insert(self, data): return self
        def select(self, columns): return self
        def eq(self, column, value): return self
        def limit(self, count): return self
        def execute(self): 
            class MockResponse:
                data = []
            return MockResponse()
        def update(self, data): return self

    supabase = MockSupabaseClient()

# === FUNÇÃO HELPER PARA CÁLCULO DE IDADE ===
def calculate_age(born):
    """Calcula a idade de um usuário com base na data de nascimento (AAAA-MM-DD)."""
    today = date.today()
    try:
        born_date = date.fromisoformat(born) 
    except (ValueError, TypeError):
        return 'N/A'
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))


# === FUNÇÕES DE BANCO DE DADOS ===

def get_user_by_email(email):
    """Busca um usuário por email e calcula sua idade."""
    try:
        # AQUI FOI CORRIGIDO: Seleciona todos para ter 'profile_image'
        response = supabase.table('usuarios').select('*').eq('email', email).limit(1).execute()
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

def register_user(nome, email, senha, cidade, posicao, nascimento, numero):
    """
    Cadastra um novo usuário no banco de dados.
    """
    try:
        # 1. Verifica se o email já existe
        existing_user = get_user_by_email(email)
        if existing_user:
            return False, "Este e-mail já está cadastrado."

        # 2. Hash da senha
        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 3. Insere o usuário no banco.
        response = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            # CORRIGIDO: Agora usa 'senha_hash' (nome da coluna no Supabase)
            'senha_hash': hashed_password, 
            'cidade': cidade,
            'posicao': posicao,
            'nascimento': nascimento, 
            'numero': numero         
        }).execute()
        
        if response.data:
            return True, "Cadastro realizado com sucesso!"
        else:
            return False, "Falha ao cadastrar. Nenhuma linha inserida. (Verifique RLS/Permissões)"
            
    except Exception as e:
        print(f"ERRO em register_user: {e}")
        # Esta mensagem será exibida na tela.
        return False, "Falha ao cadastrar devido a um erro de servidor ou de banco de dados."


def check_user(email, senha):
    """Verifica as credenciais do usuário para login."""
    try:
        user = get_user_by_email(email)
        
        # CORRIGIDO: Agora verifica contra 'senha_hash'
        if user and user.get('senha_hash') and bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
            return user
        return None
    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return None

def get_all_users():
    """Retorna a lista de todos os usuários."""
    try:
        # CORRIGIDO: Agora usa 'profile_image' (nome da coluna no Supabase)
        response = supabase.table('usuarios').select('id, nome, cidade, posicao, profile_image, nascimento').execute()
        if response.data:
            users = response.data
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
    """Busca um usuário por ID."""
    try:
        # AQUI FOI CORRIGIDO: Seleciona todos para ter 'profile_image'
        response = supabase.table('usuarios').select('*').eq('id', user_id).limit(1).execute()
        if response.data:
            user = response.data[0]
            if user.get('nascimento'):
                user['idade'] = calculate_age(user['nascimento'])
            else:
                user['idade'] = 'N/A'
            return user
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_id: {e}")
        return None

def update_user_profile_image(email, profile_image_path):
    """Atualiza o caminho da foto de perfil do usuário."""
    try:
        # CORRIGIDO: Agora usa 'profile_image'
        response = supabase.table('usuarios').update({
            'profile_image': profile_image_path
        }).eq('email', email).execute()
        
        return bool(response.data)
        
    except Exception as e:
        print(f"ERRO em update_user_profile_image: {e}")
        return False

def update_user_profile(email, **update_data):
    """Atualiza o perfil do usuário com dados dinâmicos."""
    try:
        # ATENÇÃO: Se 'update_data' contiver 'foto_perfil' precisa ser renomeado para 'profile_image' antes daqui
        # O código no app.py fará essa correção para uploads.
        response = supabase.table('usuarios').update(update_data).eq('email', email).execute()
        return bool(response.data)
    except Exception as e:
        print(f"ERRO em update_user_profile: {e}")
        return False
        
def update_password(email, new_password):
    """Redefine a senha de um usuário existente."""
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        response = supabase.table('usuarios').update({
            # CORRIGIDO: Agora usa 'senha_hash'
            'senha_hash': hashed_password
        }).eq('email', email).execute()
        return bool(response.data)
    except Exception as e:
        print(f"ERRO em update_password: {e}")
        return False