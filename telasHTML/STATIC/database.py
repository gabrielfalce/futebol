# Localização: telasHTML/STATIC/database.py

# ... (código existente: get_supabase_client, inserir_usuario) ...

# --- NOVA FUNÇÃO PARA BUSCAR USUÁRIOS ---
def buscar_usuarios():
    """Busca todos os usuários da tabela 'usuarios'."""
    
    supabase = get_supabase_client()
    if supabase is None:
        print("ERRO DE BUSCA: Falha ao obter o cliente Supabase.")
        return [] # Retorna uma lista vazia em caso de erro

    try:
        response = supabase.table("usuarios").select("*").execute()
        print(f"Resposta da busca de usuários: {response}")
        
        if response.data:
            return response.data
        else:
            return [] # Retorna lista vazia se não houver usuários

    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIOS ---: {e}")
        return []
