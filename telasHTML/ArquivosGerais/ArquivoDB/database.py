import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# Configuração do Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("Sucesso: Cliente Supabase inicializado.")

def register_user(nome, email, senha_hash, cidade, posicao, data_nasc, numero):
    """
    Registra um novo usuário no banco de dados
    """
    try:
        response = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha_hash': senha_hash,
            'cidade': cidade,
            'posicao': posicao,
            'nascimento': data_nasc,  # Coluna: nascimento
            'numero': numero,         # Coluna: numero (telefone)
            'numero_camisa': None     # Coluna: numero_camisa (pode ser null inicialmente)
        }).execute()
        
        if response.data:
            return True, "Usuário cadastrado com sucesso!"
        else:
            return False, "Erro ao cadastrar usuário"
            
    except Exception as e:
        print(f"ERRO em register_user: {e}")
        return False, "Erro ao cadastrar usuário"

def check_user(email, senha):
    """
    Verifica se o usuário existe e se a senha está correta
    """
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            # Verifica a senha usando bcrypt
            if bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
                return user
        return None
        
    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return None

def get_all_users():
    """
    Retorna todos os usuários cadastrados
    """
    try:
        response = supabase.table('usuarios').select('*').execute()
        return response.data
    except Exception as e:
        print(f"ERRO em get_all_users: {e}")
        return []

def get_user_by_email(email):
    """
    Busca um usuário pelo email
    """
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"ERRO em get_user_by_email: {e}")
        return None

def update_user_profile_image(email, image_url):
    """
    Atualiza a imagem de perfil do usuário
    """
    try:
        response = supabase.table('usuarios').update({
            'foto_perfil': image_url
        }).eq('email', email).execute()
        return True
    except Exception as e:
        print(f"ERRO em update_user_profile_image: {e}")
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

# Outras funções permanecem iguais...

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

def update_user_profile(email, **update_data):
    """
    Atualiza o perfil do usuário
    """
    try:
        response = supabase.table('usuarios').update(update_data).eq('email', email).execute()
        return True
    except Exception as e:
        print(f"ERRO em update_user_profile: {e}")
        return False
def delete_user(email):
    """
    Deleta um usuário pelo email
    """
    try:
        response = supabase.table('usuarios').delete().eq('email', email).execute()
        return True
    except Exception as e:
        print(f"ERRO em delete_user: {e}")
        return False