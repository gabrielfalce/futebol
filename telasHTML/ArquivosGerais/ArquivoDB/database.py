# database.py - Versão corrigida e comentada

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from postgrest.exceptions import APIError # Importação importante
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Optional[Client] = None

if not url or not key:
    print("Erro: Variáveis de ambiente do Supabase não configuradas no ambiente.")
else:
    try:
        supabase = create_client(url, key)
        print("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        print(f"Erro ao inicializar cliente Supabase: {e}")

# ... (suas outras funções como inserir_usuario, check_user, etc., continuam aqui) ...

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca os dados de um usuário pelo email, incluindo a URL da imagem de perfil."""
    if supabase is None:
        return None
    try:
        # Adicionei 'profile_image_url' à seleção para que possamos exibi-la na página.
        response = supabase.table("usuarios").select("nome, email, cidade, posicao, nascimento, numero, profile_image_url").eq("email", email).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"--- ERRO DURANTE A BUSCA DE USUÁRIO POR EMAIL ---: {e}")
        return None

def update_user_profile_image(email: str, image_url: str) -> tuple[bool, str]:
    """Atualiza a URL da imagem de perfil de um usuário no banco de dados."""
    if supabase is None:
        return False, "Erro de servidor: Banco de dados indisponível."

    try:
        # A operação de 'update' no Supabase pode não retornar 'data',
        # mas lançará uma exceção se houver um erro.
        response = supabase.table('usuarios').update({'profile_image_url': image_url}).eq('email', email).execute()

        # A verificação de sucesso deve focar na ausência de erros.
        # A API pode não retornar dados em um update bem-sucedido, então checar 'response.data' não é confiável.
        # Se a linha acima não lançou exceção, consideramos sucesso.
        return True, 'Imagem de perfil atualizada com sucesso.'

    except APIError as e:
        print(f"Erro de API do Supabase ao atualizar imagem: {e.message}")
        return False, f'Erro no banco de dados: {e.message}'
    except Exception as e:
        print(f"Erro inesperado ao atualizar imagem: {str(e)}")
        return False, f'Erro inesperado no servidor: {str(e)}'

