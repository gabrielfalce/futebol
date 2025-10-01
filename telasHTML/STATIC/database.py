# Localização: telasHTML/STATIC/database.py

import os
from supabase import create_client, Client
from typing import Optional
from postgrest.exceptions import APIError

# --- FUNÇÃO PARA OBTER O CLIENTE SUPABASE ---
# Esta função garante que sempre teremos um cliente válido.
def get_supabase_client() -> Optional[Client]:
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

# --- FUNÇÃO DE INSERÇÃO ATUALIZADA ---
def inserir_usuario(nome: str, email: str, senha: str, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    """Insere um usuário na tabela 'usuarios' e retorna True/False."""
    
    # Pega um cliente Supabase novo e válido a cada chamada.
    supabase = get_supabase_client()

    if supabase is None:
        print("ERRO DE INSERÇÃO: Falha ao obter o cliente Supabase.")
        return False

    data = {
        "nome": nome, "email": email, "senha": senha, "cidade": cidade,
        "posicao": posicao, "nascimento": nascimento, "numero_camisa": numero
    }
    
    print(f"Tentando inserir os seguintes dados: {data}")

    try:
        response = supabase.table("usuarios").insert(data).execute()
        print(f"Resposta do Supabase: {response}")

        if response.data:
            print("Usuário cadastrado com sucesso no banco de dados.")
            return True
        else:
            print("ERRO DE INSERÇÃO: A resposta do Supabase não continha dados.")
            return False

    except APIError as e:
        print(f"--- ERRO DE API DO SUPABASE ---")
        print(f"Código: {e.code}, Mensagem: {e.message}")
        return False
    except Exception as e:
        print(f"--- EXCEÇÃO INESPERADA DURANTE A INSERÇÃO ---")
        print(f"Erro: {e}")
        return False
