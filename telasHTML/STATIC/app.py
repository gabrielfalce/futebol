# Localização: telasHTML/STATIC/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import inserir_usuario 

# --- Configuração do Flask ---
project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, '..')
static_dir = project_root

app = Flask(
    __name__, 
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path=''
)
app.secret_key = 'uma-chave-secreta-muito-segura-pode-mudar-depois'

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    return render_template("STATIC/Cadastrar templates/cadastrar.html")

@app.route("/loading")
def tela_de_loading():
    return render_template("TelaLoading.html")

@app.route("/inicio")
def pagina_inicial():
    return render_template("TelaInicial.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    """Processa os dados do formulário de cadastro."""
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    numero = request.form.get("numero") 

    # --- CORREÇÃO APLICADA AQUI ---
    # A chamada da função agora passa TODAS as variáveis corretamente.
    sucesso = inserir_usuario(
        nome=nome, 
        email=email, 
        senha=senha, 
        cidade=cidade, 
        posicao=posicao, 
        nascimento=nascimento, 
        numero=numero
    )

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        flash("Erro ao realizar o cadastro. Verifique os dados e tente novamente.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
