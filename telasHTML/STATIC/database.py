import os
from supabase import create_client, Client
import bcrypt

# Configuração do cliente Supabase com as suas credenciais
url: str = "https://rtndgnydprxkykdxgexa.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0bmRnbnlkcHJ4a3lrZHhnZXhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjgwMDM3MjUsImV4cCI6MjA0MzU3OTcyNX0.3d-I2h2Y3sM052y3i5iA2s19i4p8s3mY-33V_2NfM-0"
supabase: Client = create_client(url, key )

def register_user(nome, email, senha, cidade, numero, posicao, data_nasc):
    """Regista um novo utilizador no banco de dados com senha encriptada."""
    try:
        # Verifica se o email já existe
        user_exists = supabase.table('usuarios').select('id').eq('email', email).execute()
        if user_exists.data:
            return False, "Este email já está registado."

        # Encripta a senha antes de guardar
        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        
        # Insere o novo utilizador
        data, count = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email,
            'senha': hashed_password.decode('utf-8'), # Guarda a senha como string
            'cidade': cidade,
            'numero': numero,
            'posicao': posicao,
            'data_nasc': data_nasc
        }).execute()
        
        return True, "Utilizador registado com sucesso!"
        
    except Exception as e:
        print(f"Erro ao registar utilizador: {e}")
        return False, f"Ocorreu um erro inesperado: {e}"

def check_user(email, password):
    """Verifica se um utilizador existe e se a senha está correta."""
    try:
        # Busca o utilizador pelo email
        user_data = supabase.table('usuarios').select('senha').eq('email', email).execute()
        
        # Verifica se o utilizador foi encontrado
        if not user_data.data:
            return False

        # Obtém a hash da senha armazenada no banco de dados
        hashed_password = user_data.data[0]['senha'].encode('utf-8')
        
        # Compara a senha fornecida pelo utilizador com a hash armazenada
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True # A senha está correta
        else:
            return False # A senha está incorreta
            
    except Exception as e:
        print(f"Erro ao verificar utilizador: {e}")
        return False
