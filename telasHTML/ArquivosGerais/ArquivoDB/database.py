# Localização: telasHTML/STATIC/database.py

import os
import bcrypt
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError

def get_supabase_client() -> Optional[Client]:
    """Cria e retorna um cliente Supabase se as variáveis de ambiente estiverem configuradas."""
    url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

    if not url or not key:
        print("ERRO CRÍTICO: Variáveis de ambiente do Supabase não configuradas.")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Erro ao criar o cliente Supabase: {e}")
        return None

# --- CORREÇÃO APLICADA AQUI ---
# A função foi renomeada de volta para 'inserir_usuario'
def inserir_usuario(nome: str, email: str, senha: str, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    """Insere os dados de um usuário na tabela 'usuarios', com a senha hasheada."""
    
    supabase = get_supabase_client()
    if supabase is None:
        print("ERRO DE INSERÇÃO: Falha ao obter o cliente Supabase.")
        return False

    try:
        senha_bytes = senha.encode('utf-8')
        sal = bcrypt.gensalt()
        senha_hashed = bcrypt.hashpw(senha_bytes, sal)
        senha_hash_str = senha_hashed.decode('utf-8')
    except Exception as e:
        print(f"Erro ao gerar o hash da senha: {e}")
        return False

    data = {
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash_str,
        "cidade": cidade,
        "posicao": posicao,
        "nascimento": nascimento,
        "numero": numero
    }
    
    print(f"Tentando inserir dados para o email: {email}")

    try:
        response = supabase.table("usuarios").insert(data).execute()
        print(f"Resposta do Supabase: {response}")
        return bool(response.data)
    except Exception as e:
        print(f"--- ERRO DURANTE A INSERÇÃO ---: {e}")
        return False

def buscar_usuarios() -> List[Dict[str, Any]]:
    """Busca todos os usuários da tabela 'usuarios'."""
    
    supabase = get_supabase_client()
    if supabase is None:
        print("ERRO DE BUSCA: Falha ao obter o cliente Supabase.")
        return []

    try:
        response = supabase.table("usuarios").select("*").execute()
        print(f"Resposta da busca de usuários: {response}")
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []

