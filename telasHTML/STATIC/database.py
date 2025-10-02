# Localização: telasHTML/STATIC/database.py

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError

# Pega as variáveis de ambiente para a conexão com o Supabase
url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Optional[Client] = None

# Bloco de inicialização seguro para o cliente Supabase
if not url or not key:
    print("Erro Crítico: Variáveis de ambiente do Supabase não configuradas.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro Crítico ao inicializar cliente Supabase: {e}")

def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    """
    Insere um novo usuário no banco de dados, recebendo a senha já como hash.
    Retorna True em caso de sucesso e False em caso de falha.
    """
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Não é possível inserir dados.")
        return False
    
    # Prepara o dicionário de dados para a inserção
    data = {
        "nome": nome,
        "email": email,
        # Converte o hash de bytes para string (UTF-8) antes de enviar
        "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade,
        "posicao": posicao,
        "nascimento": nascimento,
        "numero": numero
    }
    
    try:
        print("--- TENTANDO INSERIR DADOS ---")
        print(data)
        # Executa a inserção na tabela 'usuarios'
        response = supabase.table("usuarios").insert(data).execute()
        print("--- RESPOSTA DO SUPABASE ---")
        print(response)
        
        # CORREÇÃO: A biblioteca do Supabase lança uma exceção em caso de erro.
        # Se o código chegou até aqui, a operação foi aceita pela API.
        return True

    except APIError as e:
        # Captura erros específicos da API do Supabase (ex: e-mail duplicado)
        print(f"--- ERRO DE API SUPABASE AO INSERIR ---")
        print(f"Mensagem: {e.message}")
        print(f"Código: {e.code}")
        print(f"Detalhes: {e.details}")
        return False
    except Exception as e:
        # Captura qualquer outro erro inesperado (ex: problema de rede)
        print(f"--- ERRO INESPERADO AO INSERIR ---: {e}")
        return False

def buscar_usuarios() -> List[Dict[str, Any]]:
    """
    Busca todos os usuários da tabela 'usuarios', selecionando apenas as colunas
    necessárias para a tela inicial.
    Retorna uma lista de dicionários ou uma lista vazia em caso de erro.
    """
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado para busca.")
        return []
    try:
        # Seleciona apenas as colunas 'nome' e 'cidade' para otimizar a busca
        response = supabase.table("usuarios").select("nome, cidade").execute()
        # Retorna os dados se a busca for bem-sucedida, caso contrário, uma lista vazia
        return response.data if response.data else []
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []

