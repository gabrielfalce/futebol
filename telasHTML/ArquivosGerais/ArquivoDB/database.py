import os
from supabase import create_client, Client
import bcrypt
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env para o ambiente
load_dotenv()

# --- CONFIGURAÇÃO DO CLIENTE SUPABASE ---
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERRO CRÍTICO: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram encontradas.")
    # Em um ambiente de produção, seria ideal levantar uma exceção aqui.
    # raise ValueError("Credenciais do Supabase não configuradas no ambiente.")

try:
    supabase: Client = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado.")
except Exception as e:
    print(f"Erro crítico ao inicializar o cliente Supabase: {e}")
    raise

def register_user(nome, email, senha_hash, cidade, numero, posicao, data_nasc):
    """Registra um novo utilizador no banco de dados."""
    try:
        # 1. Verifica se o usuário já existe
        user_exists = supabase.table('usuarios').select('id').eq('email', email).execute()
        if user_exists.data:
            return False, "Este email já está registrado."

        # 2. Insere o novo usuário
        # O hash da senha (bytes) é decodificado para string para ser salvo no banco
        data, count = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha': senha_hash, # senha_hash já deve ser string
            'cidade': cidade,
            'numero': numero,
            'posicao': posicao,
            'nascimento': data_nasc
        }).execute()

        return True, "Usuário registrado com sucesso!"

    except Exception as e:
        print(f"ERRO em register_user: {e}")
        return False, f"Ocorreu um erro inesperado durante o registro."

def check_user(email, password_text):
    """Verifica as credenciais de um utilizador e retorna seus dados em caso de sucesso."""
    try:
        # Busca o usuário pelo email
        response = supabase.table('usuarios').select('*').eq('email', email).single().execute()
        user_data = response.data

        if not user_data:
            return None # Usuário não encontrado

        # Pega a senha hasheada (que é uma string) do banco e a codifica para bytes
        hashed_password_from_db = user_data['senha'].encode('utf-8')

        # Compara a senha fornecida (codificada para bytes) com o hash do banco
        if bcrypt.checkpw(password_text.encode('utf-8'), hashed_password_from_db):
            return user_data # Senha correta, retorna todos os dados do usuário
        else:
            return None # Senha incorreta

    except Exception as e:
        print(f"ERRO em check_user: {e}")
        return None

def get_all_users():
    """Recupera todos os usuários para a lista inicial, incluindo a URL da imagem."""
    try:
        # Incluído 'profile_image_url' para a TelaInicial funcionar corretamente
        response = supabase.table('usuarios').select('id, nome, cidade, email, profile_image_url').order('nome', desc=False).execute()
        return response.data
    except Exception as e:
        print(f"ERRO em get_all_users: {e}")
        return []

def get_user_by_email(email):
    """Recupera todos os dados de um usuário específico pelo seu email."""
    try:
        response = supabase.table('usuarios').select('*').eq('email', email).single().execute()
        return response.data
    except Exception as e:
        print(f"ERRO em get_user_by_email: {e}")
        return None

# --- FUNÇÃO ESSENCIAL PARA O UPLOAD ---
def update_user_profile_image(user_email, image_url):
    """
    Atualiza a coluna 'profile_image_url' de um usuário no banco de dados.
    Esta função é essencial para a funcionalidade de upload de imagem.
    """
    try:
        data, count = supabase.table('usuarios') \
                              .update({'profile_image_url': image_url}) \
                              .eq('email', user_email) \
                              .execute()

        # Verifica se a atualização foi bem-sucedida
        if count.count > 0:
            print(f"Sucesso: URL da imagem atualizada para o usuário {user_email}")
            return True, "Imagem de perfil atualizada com sucesso."
        else:
            # Isso pode acontecer se o email não for encontrado, embora seja improvável em um fluxo normal.
            print(f"Aviso: Nenhum usuário encontrado com o email {user_email} para atualizar a imagem.")
            return False, "Usuário não encontrado para atualização."

    except Exception as e:
        print(f"ERRO em update_user_profile_image: {e}")
        return False, "Ocorreu um erro ao atualizar a imagem de perfil no banco de dados."

