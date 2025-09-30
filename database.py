from supabase import create_client, Client
import os
import bcrypt

# Pega as variáveis de ambiente (Render)
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# Debug (sem expor a key inteira)
print(f"DEBUG: SUPABASE_URL={SUPABASE_URL}")
print(f"DEBUG: SUPABASE_KEY={'[None]' if SUPABASE_KEY is None else SUPABASE_KEY[:8] + '...'}")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("AVISO: Variáveis de ambiente do Supabase não configuradas.")
    print("A inserção de usuários no Supabase não funcionará sem elas.")

def inserir_usuario(nome, email, senha, cidade, numero, posicao, nascimento):
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Verifique as variáveis de ambiente.")
        return False

    try:
        print(f"Recebido: nome={nome}, email={email}, senha=[oculto], cidade={cidade}, numero={numero}, posicao={posicao}, nascimento={nascimento}")
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Senha hash gerada: {senha_hash[:10]}...")

        # Dados para inserir no Supabase
        data = {
            "nome": nome,
            "email": email,
            "senha": senha,            # senha em texto (se quiser guardar)
            "senha_hash": senha_hash,  # senha criptografada
            "cidade": cidade,
            "numero": numero,
            "posicao": posicao,
            "nascimento": nascimento
        }

        print(f"Dados a inserir: {data}")
        response = supabase.table("usuarios").insert(data).execute()
        print(f"Resposta do Supabase: {response}")

        # Checagem de sucesso (Supabase v2 retorna dict)
        if not response or "data" not in response or len(response["data"]) == 0:
            print("Erro ao inserir usuário no Supabase.")
            return False

        print("Usuário inserido com sucesso no Supabase.")
        return True
    except Exception as e:
        print(f"Erro inesperado ao inserir usuário no Supabase: {str(e)}")
        return False
