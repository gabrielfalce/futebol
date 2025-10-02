# Localização: telasHTML/STATIC/database.py

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
# Não precisamos mais de bcrypt aqui, ele fica só no app.py
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

# --- FUNÇÃO CORRIGIDA ---
# Agora ela espera 'senha_hash' como um bytes e o converte para string
def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado para inserção.")
        return False
    
    data = {
        "nome": nome,
        "email": email,
        # IMPORTANTE: Converte o hash de bytes para string antes de enviar
        "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade,
        "posicao": posicao,
        "nascimento": nascimento,
        "numero": numero
    }
    
    try:
        print("--- TENTANDO INSERIR DADOS ---")
        print(data)
        response = supabase.table("usuarios").insert(data).execute()
        print("--- RESPOSTA DO SUPABASE ---")
        print(response)
        # A inserção é bem-sucedida se a resposta contiver dados
        return bool(response.data)
    except APIError as e:
        print(f"--- ERRO DE API SUPABASE ---")
        print(f"Mensagem: {e.message}")
        print(f"Código: {e.code}")
        print(f"Detalhes: {e.details}")
        return False
    except Exception as e:
        print(f"--- ERRO INESPERADO AO INSERIR ---: {e}")
        return False

def buscar_usuarios() -> List[Dict[str, Any]]:
    """Busca todos os usuários da tabela 'usuarios'."""
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado para busca.")
        return []
    try:
        response = supabase.table("usuarios").select("nome, cidade").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []
