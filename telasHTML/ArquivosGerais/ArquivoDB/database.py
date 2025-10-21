import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError
from dotenv import load_dotenv 
import bcrypt
from datetime import datetime # datetime é necessário para calcular a idade

# Carrega variáveis de ambiente de um arquivo .env, se existir (para desenvolvimento local)
load_dotenv() 

# Pega as credenciais do Supabase a partir das variáveis de ambiente (funciona no Render)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Optional[Client] = None

# Inicializa o cliente Supabase de forma segura
if not url or not key:
    print("Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar cliente Supabase: {e}")

# Em database.py

def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str, numero_camisa: str) -> tuple[bool, str]:
    """Insere um novo usuário. A data de nascimento DEVE estar no formato ISO (AAAA-MM-DD)."""
    if supabase is None:
        return False, "Erro de servidor: Banco de dados indisponível."
    
    # Validação da data de nascimento no formato ISO
    try:
        datetime.strptime(nascimento, '%Y-%m-%d')
    except ValueError:
        return False, "Erro: A data de nascimento fornecida não está no formato correto (AAAA-MM-DD)."
    
    # Checagem de e-mail duplicado
    try:
        if supabase.table('usuarios').select('email').eq('email', email).execute().data:
            return False, "Erro: Este e-mail já está cadastrado."
    except Exception as e:
        print(f"Erro ao checar e-mail duplicado: {e}")
        return False, "Erro ao verificar e-mail. Tente novamente."

    # Dados a serem inseridos
    data = {
        "nome": nome, 
        "email": email, 
        "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade, 
        "posicao": posicao, 
        "nascimento": nascimento,
        "numero": numero,
        "numero_camisa": numero_camisa 
    }
    
    try:
        supabase.table("usuarios").insert(data).execute()
        return True, "Cadastro realizado com sucesso! Faça login."
    except APIError as e:
        error_message = f"Erro de banco de dados: {e.message}"
        print(f"--- ERRO DE API SUPABASE ---: {error_message}")
        return False, error_message


def check_user(email: str, senha_texto_puro: str) -> Optional[Dict[str, Any]]:
    """Verifica as credenciais de um usuário e retorna seus dados se válidos."""
    if supabase is None:
        return None
    
    try:
        response = supabase.table("usuarios").select("senha_hash, nome, email").eq("email", email).limit(1).execute()
        
        if not response.data:
            return None

        user_data = response.data[0]
        stored_hash = user_data.get('senha_hash', '').encode('utf-8')

        if bcrypt.checkpw(senha_texto_puro.encode('utf-8'), stored_hash):
            return user_data
        else:
            return None

    except Exception as e:
        print(f"Erro durante a checagem de login: {e}")
        return None

def get_all_users() -> List[Dict[str, Any]]:
    """Busca todos os usuários, calcula a idade e retorna a lista."""
    if supabase is None:
        return []
    try:
        # Busca ID, nome, cidade, posição, data de nascimento e imagem de perfil
        response = supabase.table("usuarios").select("id, nome, cidade, posicao, nascimento, profile_image").execute()
        
        # Lógica para calcular a idade
        users_with_age = []
        today = datetime.now()
        
        for user in response.data:
            # 1. Renomeia a coluna da imagem para consistência com o template HTML
            user['profile_image_url'] = user.pop('profile_image', None)
            
            # 2. Calcula a idade com base na data de nascimento
            if user.get('nascimento'):
                try:
                    birth_date = datetime.strptime(user['nascimento'], '%Y-%m-%d')
                    # Cálculo da idade: subtrai o ano e ajusta se o aniversário não passou
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    user['idade'] = age
                except ValueError:
                    user['idade'] = "N/A"
            else:
                 user['idade'] = "N/A"
            
            users_with_age.append(user)
            
        return users_with_age if users_with_age else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []

# Em database.py

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca os dados de um usuário pelo email."""
    if supabase is None:
        return None
    try:
        # Busca os dados do perfil
        response = supabase.table("usuarios").select("nome, email, cidade, posicao, nascimento, numero, numero_camisa, profile_image").eq("email", email).limit(1).execute()
        
        # Renomeia profile_image para profile_image_url antes de retornar
        if response.data:
            user_data = response.data[0]
            user_data['profile_image_url'] = user_data.pop('profile_image', None)
            return user_data
        
        return None
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIO POR EMAIL ---: {e}")
        return None

def update_user_profile_image(email: str, image_url: str) -> tuple[bool, str]:
    """Atualiza a URL da imagem de perfil de um usuário no banco de dados."""
    if supabase is None:
        return False, "Erro de servidor: Banco de dados indisponível."

    try:
        # Usa o nome da coluna do banco de dados: 'profile_image'
        supabase.table('usuarios').update({'profile_image': image_url}).eq('email', email).execute()
        return True, 'Imagem de perfil atualizada com sucesso.'

    except APIError as e:
        print(f"Erro de API do Supabase ao atualizar imagem: {e.message}")
        return False, f'Erro no banco de dados: {e.message}'
    except Exception as e:
        print(f"Erro inesperado ao atualizar imagem: {str(e)}")
        return False, f'Erro inesperado no servidor: {str(e)}'