from flask import Flask, request, jsonify
import bcrypt
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ==============================
# CONFIGURAÇÃO GOOGLE MAPS API
# ==============================
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "SUA_CHAVE_API_AQUI")

# ==============================
# ROTA: Registrar Usuário
# ==============================
@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.json
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")

    if not nome or not email or not senha:
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        # Inserir usuário no Supabase
        response = supabase.table("usuarios").insert({"nome": nome, "email": email, "senha": senha_hash}).execute()
        # Supabase retorna uma tupla (data, count) para insert
        if response.data:
            return jsonify({"mensagem": "Usuário registrado com sucesso!"}), 201
        else:
            return jsonify({"erro": "Erro desconhecido ao registrar usuário"}), 500
    except Exception as e:
        # Captura erros específicos do Supabase ou outros erros de banco de dados
        if "duplicate key value violates unique constraint" in str(e):
            return jsonify({"erro": "Email já cadastrado"}), 409
        return jsonify({"erro": f"Erro ao registrar usuário: {e}"}), 500

# ==============================
# ROTA: Listar usuários
# ==============================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        response = supabase.table("usuarios").select("id, nome, email, created_at").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar usuários: {e}"}), 500

# ==============================
# ROTA: Buscar jogadores por posição
# ==============================
@app.route("/jogadores/<posicao>", methods=["GET"])
def buscar_jogadores(posicao):
    try:
        response = supabase.table("jogadores").select("*").eq("posicao", posicao.upper()).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar jogadores: {e}. Certifique-se de que a tabela 'jogadores' existe e está configurada no Supabase."}), 500

# ==============================
# ROTA: Buscar cidade no Google Maps
# ==============================
@app.route("/cidade/<nome_cidade>", methods=["GET"])
def procurar_cidade(nome_cidade):
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == "SUA_CHAVE_API_AQUI":
        return jsonify({"erro": "Chave da API do Google Maps não configurada."}), 500

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={nome_cidade}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return jsonify(data)

# ==============================
# Rodar servidor
# ==============================
if __name__ == "__main__":
    app.run(debug=True, host=\'0.0.0.0\')


