import os
from supabase import create_client, Client
from typing import Optional

# Pega as variáveis de ambiente e garante que elas são strings (ou None)
# Corrigido para usar os nomes exatos configurados no Render,
# conforme mostrado na sua imagem.
url: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: Optional[str] = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# Inicialização do cliente Supabase
supabase: Optional[Client] = None

# Verifica se as variáveis estão configuradas
if not url or not key:
    print("Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")
    # supabase permanece None
else:
    # Se estiverem configuradas, inicializa o cliente
    supabase = create_client(url, key)
    print("Sucesso: Cliente Supabase inicializado.")


def inserir_usuario(nome: str, email: str, senha: str) -> bool:
    """Insere um usuário na tabela 'usuarios' do Supabase."""
    # O cliente Supabase deve ser um objeto válido (não None)
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Verifique as variáveis de ambiente.")
        return False

    try:
        # Nota: Idealmente, a senha deve ser hasheada antes de ser armazenada, 
        # e o Supabase Auth deve ser usado em vez de uma tabela 'usuarios' customizada.
        data = {
            "nome": nome,
            "email": email,
            "senha": senha  
        }
        
        # O método .execute() é necessário para enviar a requisição
        response = supabase.table("usuarios").insert(data).execute()

        # O objeto de resposta da biblioteca Supabase agora tem a propriedade 'data'
        if response.data:
            print("Usuário cadastrado com sucesso:", response.data)
            return True
        else:
            # Caso a API retorne um erro, mas o Python não levante uma exceção.
            print("Erro ao inserir usuário. Resposta:", response)
            return False

    except Exception as e:
        print("Exceção ao inserir usuário:", e)
        return False
