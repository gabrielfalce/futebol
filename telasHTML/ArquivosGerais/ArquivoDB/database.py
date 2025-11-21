import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv
from datetime import date 

load_dotenv()

# Configuração do Supabase
url: str = os.environ.get("SUPABASE_URL")
# Usando a chave de serviço para operações de backend.
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# Garante que as variáveis de ambiente foram carregadas
if not url or not key:
    print("ERRO: SUPABASE_URL ou SUPABASE_SERVICE_KEY não encontrados no ambiente.")
    url = "http://mock-url"
    key = "mock-key"

try:
    # A inicialização agora usa a chave de serviço, que tem mais privilégios.
    supabase: Client = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado com chave de serviço.")
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

def get_user_by_phone(phone_number):
    """Busca um usuário pelo número de telefone."""
    try:
        if not phone_number:
            return None
        response = supabase.table('usuarios').select('id').eq('numero', phone_number).limit(1).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_phone: {e}")
        return None

def register_user(nome, email, senha, cidade, posicao, nascimento, numero_camisa, numero_telefone):
    """
    Cadastra um novo usuário no banco de dados.
    """
    try:
        existing_user_by_email = get_user_by_email(email)
        if existing_user_by_email:
            return False, "Este e-mail já está cadastrado."

        existing_user_by_phone = get_user_by_phone(numero_telefone)
        if existing_user_by_phone:
            return False, "Este número de telefone já está em uso."

        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        response = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha_hash': hashed_password,
            'cidade': cidade,
            'posicao': posicao,
            'nascimento': nascimento, 
            'numero_camisa': numero_camisa,
            'numero': numero_telefone
        }).execute()
        
        if response.data:
            return True, "Cadastro realizado com sucesso!"
        else:
            return False, "Falha ao cadastrar. Nenhuma linha inserida. (Verifique RLS/Permissões)"
            
    except Exception as e:
        error_message = str(e)
        if hasattr(e, 'message') and isinstance(e.message, dict):
            error_message = e.message.get('message', str(e))
            
        print(f"ERRO em register_user: {error_message}")
        return False, f"Falha ao cadastrar devido a um erro de banco de dados: {error_message}"


def check_user(email, senha):
    """Verifica as credenciais do usuário para login."""
    try:
        user = get_user_by_email(email)
        
        if user and user.get('senha_hash') and bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
            return user
        return None
    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return None

def get_all_users():
    """Retorna a lista de todos os usuários."""
    try:
        response = supabase.table('usuarios').select('id, nome, email, cidade, posicao, profile_image_url, nascimento, numero_camisa, numero').execute()
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

def update_user_profile_image(email, profile_image_url_path):
    """Atualiza o caminho da foto de perfil do usuário."""
    try:
        response = supabase.table('usuarios').update({
            'profile_image_url': profile_image_url_path
        }).eq('email', email).execute()
        
        return bool(response.data)
        
    except Exception as e:
        print(f"ERRO em update_user_profile_image: {e}")
        return False

def update_user_profile(user_id, nome, bio, profile_image_url):
    """Atualiza o perfil do usuário com dados dinâmicos."""
    try:
        update_data = {}
        if nome is not None:
            update_data['nome'] = nome
        if bio is not None:
            update_data['bio'] = bio
        if profile_image_url is not None:
            update_data['profile_image_url'] = profile_image_url
            
        if not update_data:
            return True # Nada para atualizar

        response = supabase.table('usuarios').update(update_data).eq('id', user_id).execute()
        return bool(response.data)
    except Exception as e:
        print(f"ERRO em update_user_profile: {e}")
        return False
        
def update_password(email, new_password):
    """Redefine a senha de um usuário existente."""
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        response = supabase.table('usuarios').update({
            'senha_hash': hashed_password
        }).eq('email', email).execute()
        return bool(response.data)
    except Exception as e:
        print(f"ERRO em update_password: {e}")
        return False

# ====================== NOVAS FUNÇÕES PARA CHAT ======================
def create_message(remetente_id: int, destinatario_id: int, content: str):
    """
    Insere uma nova mensagem na tabela `mensagens`.
    Retorna (True, message_id) ou (False, error_message).
    """
    try:
        # A nova mensagem será inserida e o Realtime do Supabase a enviará.
        response = supabase.table('mensagens').insert({
            'remetente_id': remetente_id,
            'destinatario_id': destinatario_id,
            'content': content
        }).execute()

        if response.data:
            # Retorna o ID da mensagem recém-criada
            return True, response.data[0]['id']
        else:
            return False, "Nenhuma linha inserida. (Verifique RLS/Permissões)"
    except Exception as e:
        error_msg = str(e)
        print(f"ERRO em create_message: {error_msg}")
        return False, f"Falha ao enviar mensagem: {error_msg}"
        
# ====================== NOVAS FUNÇÕES PARA POSTS ======================

def create_post(autor_id: int, legenda: str, imagem_url: str = None):
    """
    Insere um novo post na tabela `posts`.
    Retorna (True, post_id) em caso de sucesso ou (False, mensagem_de_erro).
    """
    try:
        payload = {
            'autor_id': autor_id,
            'legenda': legenda,
        }
        if imagem_url:
            payload['imagem_url'] = imagem_url

        response = supabase.table('posts').insert(payload).execute()
        if response.data:
            post_id = response.data[0]['id']
            return True, post_id
        else:
            return False, "Nenhuma linha inserida (verifique RLS)."
    except Exception as e:
        error_msg = str(e)
        print(f"ERRO em create_post: {error_msg}")
        return False, error_msg

def get_post_by_id(post_id: int):
    """Busca um único post pelo seu ID, incluindo dados do autor."""
    try:
        # ALTERAÇÃO FINAL: Usando a sintaxe explícita com o nome da chave estrangeira.
        response = (
            supabase.table('posts')
            .select('*, usuarios:posts_autor_id_fkey(nome, profile_image_url)')
            .eq('id', post_id)
            .limit(1)
            .execute()
        )
        if response.data:
            p = response.data[0]
            post = {
                'id': p['id'],
                'created_at': p['created_at'],
                'legenda': p['legenda'],
                'imagem_url': p['imagem_url'],
                'autor': {
                    'nome': p['usuarios']['nome'],
                    'profile_image_url': p['usuarios']['profile_image_url']
                }
            }
            return post
        return None
    except Exception as e:
        print(f"ERRO em get_post_by_id: {e}")
        return None

def get_posts_by_user(user_id: int):
    """
    Retorna todos os posts de um usuário específico, ordenados por data (mais recente primeiro).
    Inclui dados do autor (nome, profile_image_url) via join.
    """
    try:
        # ALTERAÇÃO FINAL: Usando a sintaxe explícita com o nome da chave estrangeira.
        response = (
            supabase.table('posts')
            .select('*, usuarios:posts_autor_id_fkey(nome, profile_image_url)')
            .eq('autor_id', user_id)
            .order('created_at', desc=True)
            .execute()
        )
        if response.data:
            posts = []
            for p in response.data:
                post = {
                    'id': p['id'],
                    'created_at': p['created_at'],
                    'legenda': p['legenda'],
                    'imagem_url': p['imagem_url'],
                    'autor': {
                        'nome': p['usuarios']['nome'],
                        'profile_image_url': p['usuarios']['profile_image_url']
                    }
                }
                posts.append(post)
            return posts
        return []
    except Exception as e:
        print(f"ERRO em get_posts_by_user: {e}")
        return []


def get_all_posts():
    """
    Retorna todos os posts (feed global), com informações do autor.
    Ordenados do mais recente para o mais antigo.
    """
    try:
        # ALTERAÇÃO FINAL: Usando a sintaxe explícita com o nome da chave estrangeira.
        response = (
            supabase.table('posts')
            .select('*, usuarios:posts_autor_id_fkey(nome, profile_image_url)')
            .order('created_at', desc=True)
            .execute()
        )
        if response.data:
            posts = []
            for p in response.data:
                post = {
                    'id': p['id'],
                    'created_at': p['created_at'],
                    'legenda': p['legenda'],
                    'imagem_url': p['imagem_url'],
                    'autor': {
                        'nome': p['usuarios']['nome'],
                        'profile_image_url': p['usuarios']['profile_image_url']
                    }
                }
                posts.append(post)
            return posts
        return []
    except Exception as e:
        print(f"ERRO em get_all_posts: {e}")
        return []

# ====================== FIM DAS NOVAS FUNÇÕES ======================