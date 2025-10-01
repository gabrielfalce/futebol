# Localização: telasHTML/STATIC/database.py

import os
import bcrypt # Importa a biblioteca de hashing
from supabase import create_client, Client
from typing import Optional
from postgrest.exceptions import APIError

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

def inserir_usuario(nome: str, email: str, senha: str, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    supabase = get_supabase_client()
    if supabase is None:
        print("ERRO DE INSERÇÃO: Falha ao obter o cliente Supabase.")
        return False

    # --- CORREÇÃO DE SEGURANÇA DA SENHA ---
    # 1. Converte a senha para bytes
    senha_bytes = senha.encode('utf-8')
    # 2. Gera o "sal" e o hash da senha
    sal = bcrypt.gensalt()
    senha_hashed = bcrypt.hashpw(senha_bytes, sal)
    # 3. Decodifica o hash para salvar como texto no banco
    senha_hash_str = senha_hashed.decode('utf-8')

    # O dicionário agora envia o HASH para a coluna 'senha_hash'
    data = {
        "nome": nome,
        "email": email,
        # "senha": senha, # Não salvamos mais a senha em texto puro
        "senha_hash": senha_hash_str, # Salvamos o hash seguro
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
