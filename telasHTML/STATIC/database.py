import os
from supabase import create_client, Client

# Pega as variáveis de ambiente
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Verifica se estão corretas
if not url or not key:
    print("Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")
    supabase: Client = None
else:
    supabase: Client = create_client(url, key)

def inserir_usuario(nome: str, email: str, senha: str) -> bool:
    """Insere um usuário na tabela 'usuarios' do Supabase."""
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado.")
        return False

    try:
        data = {
            "nome": nome,
            "email": email,
            "senha": senha
        }
        response = supabase.table("usuarios").insert(data).execute()

        if response.data:
            print("Usuário cadastrado com sucesso:", response.data)
            return True
        else:
            print("Erro ao inserir usuário:", response)
            return False

    except Exception as e:
        print("Exceção ao inserir usuário:", e)
        return False
