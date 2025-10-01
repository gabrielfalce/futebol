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
    print("Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas no Render.")
else:
    supabase = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado.")


def inserir_usuario(nome: str, email: str, senha: str, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    """Insere um usuário com TODOS os dados na tabela 'usuarios' do Supabase."""
    
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Não é possível inserir dados.")
        return False

    data = {
        "nome": nome,
        "email": email,
        "senha": senha,  
        "cidade": cidade,
        "posicao": posicao,
        "data_nascimento": nascimento,  # Coluna: 'data_nascimento'
        "numero_camisa": numero       # Coluna: 'numero_camisa'
    }

    try:
        # Tenta inserir
        response = supabase.table("usuarios").insert(data).execute()

        # O cliente Python do Supabase lança APIError em caso de falha de validação ou de servidor
        # Se a execução chegar aqui, a inserção foi provavelmente bem-sucedida.

        if response.data:
            print("Usuário cadastrado com sucesso:", response.data)
            return True
        else:
            # Esta parte deve ser raramente alcançada devido ao tratamento de exceções abaixo
            print("Erro Desconhecido ao inserir usuário. Resposta Vazia.", response)
            return False

    except APIError as e:
        # Captura e imprime o erro exato retornado pelo Supabase
        print(f"--- ERRO CRÍTICO SUPABASE ---")
        print(f"Código HTTP: {e.code}")
        print(f"Mensagem de Erro: {e.message}")
        print(f"Detalhes: {e.details}")
        print(f"Status: {e.status_code}")
        print("------------------------------")
        return False
    except Exception as e:
        # Captura outros erros de rede ou processamento
        print(f"Exceção inesperada ao inserir usuário: {e}")
        return False
