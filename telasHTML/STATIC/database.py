import os
from supabase import create_client, Client
from typing import Optional

# Pega as variáveis de ambiente com os nomes CORRIGIDOS
url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# Inicialização do cliente Supabase
supabase: Optional[Client] = None

# Verifica se as variáveis estão configuradas
if not url or not key:
    print("Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas no Render.")
    # supabase permanece None
else:
    # Se estiverem configuradas, inicializa o cliente
    supabase = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado.")


def inserir_usuario(nome: str, email: str, senha: str, cidade: str, posicao: str, nascimento: str) -> bool:
    """Insere um usuário com TODOS os dados na tabela 'usuarios' do Supabase."""
    
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Verifique as variáveis de ambiente.")
        return False

    try:
        data = {
            "nome": nome,
            "email": email,
            "senha": senha,  # Lembre-se, o ideal é usar hash ou Supabase Auth
            "cidade": cidade,
            "posicao": posicao,
            "data_nascimento": nascimento  # Assumindo que o nome da coluna é 'data_nascimento'
        }
        
        # Envia a requisição de inserção
        response = supabase.table("usuarios").insert(data).execute()

        if response.data:
            print("Usuário cadastrado com sucesso:", response.data)
            return True
        else:
            # Captura erros retornados pela API
            print("Erro ao inserir usuário. Resposta:", response)
            return False

    except Exception as e:
        print("Exceção ao inserir usuário:", e)
        return False
