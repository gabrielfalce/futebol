import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError
from dotenv import load_dotenv # Adicionado para carregar .env localmente
import bcrypt

# Tenta carregar variáveis do .env (se existir)
load_dotenv() 

# Prioriza as chaves do Render/Vercel ou as chaves Supabase padrão
# Garante que as variáveis de ambiente do Render sejam usadas
url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Optional[Client] = None

if not url or not key:
    print("Erro: Variáveis de ambiente do Supabase não configuradas no ambiente.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar cliente Supabase: {e}")

# Renomeada para 'inserir_usuario' para corresponder à função no app.py
def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> tuple[bool, str]:
    """Insere um novo usuário na tabela 'usuarios'."""
    if supabase is None:
        return False, "Erro de servidor: Banco de dados indisponível."
    
    # 1. Checagem de e-mail duplicado
    try:
        if supabase.table('usuarios').select('email').eq('email', email).execute().data:
            return False, "Erro: Este e-mail já está cadastrado."
    except Exception as e:
        print(f"Erro ao checar e-mail duplicado: {e}")

    # 2. DEFINITIVO: Usa a coluna 'nascimento' (tipo date, conforme seu print do BD)
    data = {
        "nome": nome, 
        "email": email, 
        "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade, 
        "posicao": posicao, 
        "nascimento": nascimento, # NOME DA COLUNA CORRIGIDO PARA 'nascimento'
        "numero": numero
    }
    
    try:
        response = supabase.table("usuarios").insert(data).execute()
        # Se a execução ocorrer sem exceção, o registro foi bem-sucedido
        return True, "Cadastro realizado com sucesso! Faça login."

    except APIError as e:
        print(f"--- ERRO DE API SUPABASE ---: {e.message}")
        return False, f"Erro ao salvar: {e.message}"
    except Exception as e:
        print(f"--- ERRO INESPERADO AO INSERIR ---: {e}")
        return False, "Ocorreu um erro inesperado ao cadastrar."

# Função para checar login
def check_user(email: str, senha_texto_puro: str) -> Optional[Dict[str, Any]]:
    """Verifica as credenciais do usuário e retorna os dados se o login for bem-sucedido."""
    if supabase is None:
        return None
        
    try:
        # Busca o usuário pelo email
        response = supabase.table("usuarios").select("senha_hash, nome, email").eq("email", email).limit(1).execute()
        
        if not response.data:
            return None # Usuário não encontrado

        user_data = response.data[0]
        stored_hash = user_data.get('senha_hash', '').encode('utf-8')

        # Compara a senha fornecida com o hash armazenado
        if bcrypt.checkpw(senha_texto_puro.encode('utf-8'), stored_hash):
            return user_data # Login bem-sucedido
        else:
            return None # Senha incorreta

    except Exception as e:
        print(f"Erro durante a checagem de login: {e}")
        return None

# Renomeada para 'get_all_users' para corresponder à função no app.py
def get_all_users() -> List[Dict[str, Any]]:
    """Busca todos os usuários da tabela 'usuarios'."""
    if supabase is None:
        return []
    try:
        # Retorna apenas nome e cidade para a lista inicial
        response = supabase.table("usuarios").select("nome, cidade").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []
