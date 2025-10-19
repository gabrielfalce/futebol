import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError
from dotenv import load_dotenv 
import bcrypt
from datetime import datetime

# Tenta carregar variáveis do .env (se existir)
load_dotenv() 

# Usa apenas as variáveis de ambiente do Render
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Optional[Client] = None

if not url or not key:
    print("Erro: Variáveis de ambiente do Supabase não configuradas no ambiente.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar cliente Supabase: {e}")

def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> tuple[bool, str]:
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
        "numero": numero
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
    """Busca todos os usuários da tabela 'usuarios'."""
    if supabase is None:
        return []
    try:
        response = supabase.table("usuarios").select("nome, cidade").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca os dados de um usuário pelo email."""
    if supabase is None:
        return None
    try:
        response = supabase.table("usuarios").select("nome, email, cidade, posicao, nascimento, numero").eq("email", email).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIO POR EMAIL ---: {e}")
        return None

def update_user_profile_image(email, image_url):
    try:
        response = supabase.table('usuarios').update({'profile_image_url': image_url}).eq('email', email).execute()
        if response.data:
            return True, 'Imagem de perfil atualizada com sucesso.'
        return False, 'Erro ao atualizar a imagem de perfil.'
    except Exception as e:
        return False, f'Erro no banco de dados: {str(e)}'
