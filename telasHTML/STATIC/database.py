# Localização: telasHTML/STATIC/database.py
# ... (todo o código de inicialização do supabase) ...

def inserir_usuario(nome: str, email: str, senha_hash: bytes, cidade: str, posicao: str, nascimento: str, numero: str) -> bool:
    # ... (código de preparação dos dados) ...
    data = {
        "nome": nome, "email": email, "senha_hash": senha_hash.decode('utf-8'),
        "cidade": cidade, "posicao": posicao, "nascimento": nascimento, "numero": numero
    }
    try:
        response = supabase.table("usuarios").insert(data).execute()
        # Se chegou aqui sem erro, a inserção funcionou.
        return True
    except Exception as e:
        print(f"--- ERRO AO INSERIR USUÁRIO ---: {e}")
        return False

# ... (função buscar_usuarios) ...
