from supabase import create_client, Client
import os
import bcrypt

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicializa o cliente Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("AVISO: Variáveis de ambiente do Supabase (SUPABASE_URL ou SUPABASE_KEY) não configuradas.")
    print("A inserção de usuários no Supabase não funcionará sem elas.")

def inserir_usuario(nome, email, senha, cidade, numero, posicao, nascimento):
    if supabase is None:
        print("Erro: Cliente Supabase não inicializado. Verifique as variáveis de ambiente.")
        return False

    try:
        print(f"Recebido: nome={nome}, email={email}, senha=[hash], cidade={cidade}, numero={numero}, posicao={posicao}, nascimento={nascimento}")
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Senha hash gerada: {senha_hash[:10]}...")  # Mostra só parte da hash por segurança
        data = {
            "nome": nome,
            "email": email,
            "senha": senha_hash,
            "cidade": cidade,
            "numero": numero,
            "posicao": posicao,
            "nascimento": nascimento
        }
        print(f"Dados a inserir: {data}")
        response = supabase.table("usuarios").insert(data).execute()
        print(f"Resposta do Supabase: status={response.status}, data={response.data}")
        if response.status >= 400:
            print(f"Erro ao inserir usuário no Supabase: {response}")
            return False
        print("Usuário inserido com sucesso no Supabase.")
        return True
    except Exception as e:
        print(f"Erro inesperado ao inserir usuário no Supabase: {str(e)}")
        return False
