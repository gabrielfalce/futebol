# /path/to/your/project/database.py

import os
from supabase import create_client, Client
from typing import Optional
from postgrest.exceptions import APIError

# Pega as variáveis de ambiente com os nomes CORRIGIDOS do Render
url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# Inicialização do cliente Supabase
supabase: Optional[Client] = None

# Verifica se as variáveis estão configuradas
if not url or not key:
    print("Erro: Variáveis de ambiente NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY não configuradas no Render.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar o cliente Supabase: {e}")

def inserir_usuario(nome: str, email: str, senha: str, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    """Insere um usuário com TODOS os dados na tabela 'usuarios' do Supabase."""
    
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Não é possível inserir dados.")
        return False

    # --- CORREÇÃO 1: Ajuste dos nomes das colunas ---
    # O nome da coluna no banco de dados deve corresponder exatamente à chave do dicionário.
    data = {
        "nome": nome,
        "email": email,
        "senha": senha,  
        "cidade": cidade,
        "posicao": posicao,
        "nascimento": nascimento,      # CORRIGIDO: de "data_nascimento" para "nascimento"
        "numero_camisa": numero
    }

    try:
        # Tenta inserir os dados na tabela 'usuarios'
        response = supabase.table("usuarios").insert(data).execute()

        # A biblioteca do Supabase lança uma exceção (APIError) em caso de falha.
        # Se o código chegar aqui, a inserção foi bem-sucedida.
        if response.data:
            print("Usuário cadastrado com sucesso:", response.data)
            return True
        else:
            # Caso a resposta seja bem-sucedida mas não contenha dados (cenário raro)
            print("A inserção foi executada, mas não retornou dados. Resposta:", response)
            return False

    except APIError as e:
        # --- CORREÇÃO 2: Tratamento de erro correto para APIError ---
        # O objeto 'e' (APIError) não tem 'status_code', mas tem 'code' e 'message'.
        print(f"--- ERRO CRÍTICO SUPABASE AO INSERIR ---")
        print(f"Código do Erro: {e.code}")      # CORRIGIDO
        print(f"Mensagem de Erro: {e.message}")  # CORRIGIDO
        print(f"Detalhes: {e.details}")
        print("----------------------------------------")
        return False
    except Exception as e:
        # Captura outros erros (ex: problemas de rede, etc.)
        print(f"Exceção inesperada ao inserir usuário: {e}")
        return False

