from supabase import create_client, Client
import os

# As variáveis de ambiente do Supabase devem ser configuradas no Vercel.
# Para desenvolvimento local, você pode precisar de um arquivo .env e uma biblioteca como python-dotenv.
# Exemplo de como carregar localmente (se usar python-dotenv):
# from dotenv import load_dotenv
# load_dotenv()

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# Inicializa o cliente Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
else:
    print("AVISO: Variáveis de ambiente do Supabase (NEXT_PUBLIC_SUPABASE_URL ou NEXT_PUBLIC_SUPABASE_ANON_KEY) não configuradas.")
    print("A inserção de usuários no Supabase não funcionará sem elas.")

def inserir_usuario(nome, email, senha):
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Verifique as variáveis de ambiente.")
        return False

    try:
        # ATENÇÃO: Para um sistema de autenticação real, você DEVE fazer o hash da senha
        # antes de armazená-la. O Supabase Auth lida com isso automaticamente.
        # Se você não usar o Supabase Auth, implemente o hashing da senha aqui.
        response = supabase.table("usuarios").insert({
            "nome": nome,
            "email": email,
            "senha": senha, # Senha em texto puro, APENAS para demonstração. NÃO USE EM PRODUÇÃO!
            "created_at": "now()" # O Supabase preencherá o timestamp automaticamente se o tipo for TIMESTAMP WITH TIME ZONE e tiver DEFAULT now()
        }).execute()

        # O Supabase retorna um objeto com 'data' e 'error'
        # A propriedade 'data' pode ser uma lista vazia se a inserção for bem-sucedida mas não retornar dados.
        # Verificamos 'error' para saber se houve falha.
        if response.error:
            print("Erro ao inserir usuário no Supabase:", response.error.message)
            return False
        else:
            print("Usuário inserido com sucesso no Supabase.")
            return True

    except Exception as e:
        print(f"Erro inesperado ao inserir usuário no Supabase: {e}")
        return False
