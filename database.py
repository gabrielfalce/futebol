from supabase import create_client, Client
import os

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
        response = supabase.table("usuarios").insert({
            "nome": nome,
            "email": email,
            "senha": senha # Senha em texto puro, APENAS para demonstração. NÃO USE EM PRODUÇÃO!
            # REMOVIDO: "created_at": "now()" - O Supabase preenche automaticamente
        }).execute()

        if response.error:
            print("Erro ao inserir usuário no Supabase:", response.error.message)
            return False
        else:
            print("Usuário inserido com sucesso no Supabase.")
            return True

    except Exception as e:
        print(f"Erro inesperado ao inserir usuário no Supabase: {e}")
        return False
