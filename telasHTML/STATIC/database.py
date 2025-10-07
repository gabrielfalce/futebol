# Localização: telasHTML/STATIC/database.py

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError

url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase: Optional[Client] = None

if not url or not key:
    print("Erro Crítico: Variáveis de ambiente do Supabase não configuradas.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro Crítico ao inicializar cliente Supabase: {e}")

def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> (bool, Optional[str]):
    if supabase is None:
        return (False, "Erro interno: Conexão com o banco de dados não disponível.")
    
    data = {
        "nome": nome, "email": email, "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade, "posicao": posicao, "nascimento": nascimento, "numero": numero
    }
    
    try:
        # A biblioteca do Supabase lança uma exceção em caso de erro.
        # Se esta linha executar sem problemas, a inserção foi um sucesso.
        supabase.table("usuarios").insert(data).execute()
        
        # --- CORREÇÃO DEFINITIVA ---
        # Se chegamos aqui, é porque NENHUM erro ocorreu. Retornamos sucesso.
        return (True, None)

    except APIError as e:
        if 'duplicate key value violates unique constraint' in e.message and 'usuarios_email_key' in e.message:
            return (False, "Este e-mail já está cadastrado. Por favor, utilize outro.")
        else:
            print(f"--- ERRO DE API SUPABASE AO INSERIR ---: {e.message}")
            return (False, "Erro de comunicação com o banco de dados. Tente novamente.")
            
    except Exception as e:
        print(f"--- ERRO INESPERADO AO INSERIR ---: {e}")
        return (False, "Ocorreu um erro inesperado no servidor.")

def buscar_usuarios() -> List[Dict[str, Any]]:
    if supabase is None: return []
    try:
        response = supabase.table("usuarios").select("nome, cidade").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []
