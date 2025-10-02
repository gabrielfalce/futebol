# Localização: telasHTML/STATIC/database.py

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError

# ... (código de inicialização do supabase, sem alterações) ...
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

# --- FUNÇÃO MODIFICADA PARA RETORNAR MENSAGENS DE ERRO ---
def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> (bool, Optional[str]):
    """
    Insere um novo usuário.
    Retorna (True, None) em caso de sucesso.
    Retorna (False, "mensagem de erro") em caso de falha.
    """
    if supabase is None:
        return (False, "Erro interno: Conexão com o banco de dados não disponível.")
    
    data = {
        "nome": nome, "email": email, "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade, "posicao": posicao, "nascimento": nascimento, "numero": numero
    }
    
    try:
        supabase.table("usuarios").insert(data).execute()
        # Se chegou aqui sem erro, a inserção funcionou.
        return (True, None)

    except APIError as e:
        # --- LÓGICA INTELIGENTE ---
        # Verifica se a mensagem de erro contém o texto sobre a constraint de unicidade do e-mail.
        if 'duplicate key value violates unique constraint' in e.message and 'usuarios_email_key' in e.message:
            return (False, "Este e-mail já está cadastrado. Por favor, utilize outro.")
        else:
            # Para qualquer outro erro da API
            print(f"--- ERRO DE API SUPABASE AO INSERIR ---: {e.message}")
            return (False, "Erro de comunicação com o banco de dados. Tente novamente.")
            
    except Exception as e:
        print(f"--- ERRO INESPERADO AO INSERIR ---: {e}")
        return (False, "Ocorreu um erro inesperado no servidor.")

def buscar_usuarios() -> List[Dict[str, Any]]:
    # ... (função buscar_usuarios, sem alterações) ...
    if supabase is None: return []
    try:
        response = supabase.table("usuarios").select("nome, cidade").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []
