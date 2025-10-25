
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
import os
import random

app = Flask(__name__)

# Configurações do Supabase (preencha com suas credenciais)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lgwhpoanpyqzarxghzbe.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxnd2hwb2FucHlxemFyeGdoemJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3OTU5MzQsImV4cCI6MjA3NjM3MTkzNH0.M7E6_e6Qa8MybKj3EDN-VpiSuetJINC9IX6D3KJIctw")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/random_user")
def random_user():
    try:
        # Busca um usuário aleatório no Supabase
        response = supabase.from_('users').select('*').limit(100).execute()
        users = response.data
        if users:
            random_user_data = random.choice(users)
            return render_template("index.html", random_user=random_user_data)
        return render_template("index.html", random_user=None, message="Nenhum usuário encontrado.")
    except Exception as e:
        return render_template("index.html", random_user=None, error=f"Erro ao buscar usuário aleatório: {e}")

@app.route("/search_user", methods=["POST"])
def search_user():
    query_term = request.form.get("query_term")
    if query_term:
        try:
            # Busca usuários por nome ou email
            response_name = supabase.from_('users').select('*').ilike('nome', f'%{query_term}%').execute()
            response_email = supabase.from_('users').select('*').ilike('email', f'%{query_term}%').execute()
            
            # Combina os resultados e remove duplicatas
            searched_users_name = response_name.data
            searched_users_email = response_email.data
            
            # Usar um conjunto para remover duplicatas baseadas em nome
            unique_users = {user['nome']: user for user in searched_users_name}
            for user in searched_users_email:
                unique_users[user['nome']] = user
            
            searched_users = list(unique_users.values())

            return render_template("index.html", searched_users=searched_users, query_term=query_term)
        except Exception as e:
            return render_template("index.html", searched_users=[], query_term=query_term, error=f"Erro ao buscar usuários: {e}")
    return redirect(url_for("index"))

# Função de recomendação (exemplo: recomenda usuarios na mesma cidade)
@app.route("/recommend_users", methods=["POST"])
def recommend_users():
    user_id_to_recommend_for = request.form.get("user_id") # Assumindo que você passa um ID de usuário para recomendação
    if user_id_to_recommend_for:
        try:
            # Primeiro, obtenha os detalhes do usuário para quem você quer recomendar
            user_response = supabase.from_('users').select('*').eq('id', user_id_to_recommend_for).single().execute()
            current_user = user_response.data

            if current_user and current_user.get('cidade'):
                city = current_user['cidade']
                # Busca outros usuários na mesma cidade, excluindo o próprio usuário
                recommendations_response = supabase.from_('users').select('*').eq('cidade', city).neq('id', user_id_to_recommend_for).execute()
                recommended_users = recommendations_response.data
                return render_template("index.html", recommended_users=recommended_users, current_user_for_rec=current_user)
            else:
                return render_template("index.html", recommended_users=[], message="Não foi possível encontrar o usuário ou a cidade para recomendação.")
        except Exception as e:
            return render_template("index.html", recommended_users=[], error=f"Erro ao recomendar usuários: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

