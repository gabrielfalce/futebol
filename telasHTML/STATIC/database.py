# Localização: telasHTML/STATIC/database.py

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import bcrypt
from postgrest.exceptions import APIError

url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Optional[Client] = None

if not url or not key:
    print("Erro: Variáveis de ambiente do Supabase não configuradas.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar cliente Supabase: {e}")

def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    # ... (código de inserção que já funciona)
    if supabase is None: return False
    data = {
        "nome": nome, "email": email, "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade, "posicao": posicao, "nascimento": nascimento, "numero": numero
    }
    try:
        response = supabase.table("usuarios").insert(data).execute()
        return bool(response.data)
    except Exception as e:
        print(f"--- ERRO AO INSERIR USUÁRIO ---: {e}")
        return False

# --- NOVA FUNÇÃO A SER ADICIONADA ---
def buscar_usuarios() -> List[Dict[str, Any]]:
    """Busca todos os usuários da tabela 'usuarios'."""
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado para busca.")
        return []
    try:
        # Seleciona apenas as colunas que vamos usar na tela inicial
        response = supabase.table("usuarios").select("nome, cidade").execute()
        print("Busca de usuários realizada. Resposta:", response)
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []
