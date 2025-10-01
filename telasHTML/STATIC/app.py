# Localização: telasHTML/STATIC/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import inserir_usuario 

# --- Configuração do Flask (sem alterações) ---
project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, '..') # Aponta para a pasta 'telasHTML'
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
    # Encontra o template em: telasHTML/STATIC/Cadastrar templates/cadastrar.html
    return render_template("STATIC/Cadastrar templates/cadastrar.html")

@app.route("/loading")
def tela_de_loading():
    """Renderiza a página de loading intermediária."""
    # --- CORREÇÃO APLICADA AQUI ---
    # Usando o nome de arquivo exato que você forneceu: "Telaloading.html"
    return render_template("Telaloading.html")

@app.route("/inicio")
def pagina_inicial():
    # Encontra o template em: telasHTML/TelaInicial.html
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

    if not all([nome, email, senha, cidade, posicao, nascimento, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.")
        return redirect(url_for('index'))

    sucesso = inserir_usuario(
        nome=nome, email=email, senha=senha, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero
    )

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        flash("Erro ao salvar no banco de dados. Verifique se o e-mail já foi cadastrado e tente novamente.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
