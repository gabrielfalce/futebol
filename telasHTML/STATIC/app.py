# Localização: telasHTML/STATIC/app.py

import os
from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario 

# --- Configuração do Flask para a SUA estrutura de arquivos ---

# O diretório onde o app.py está: '.../telasHTML/STATIC'
project_root = os.path.dirname(os.path.abspath(__file__))

# 1. A pasta de templates (HTML) está um nível ACIMA: '.../telasHTML'
template_dir = os.path.join(project_root, '..')

# 2. A pasta de arquivos estáticos (CSS, JS, Imagens) é a pasta ATUAL: '.../telasHTML/STATIC'
static_dir = project_root

app = Flask(
    __name__, 
    template_folder=template_dir, 
    static_folder=static_dir
)

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    """Rota para carregar o formulário de cadastro (telasHTML/index.html)."""
    return render_template("index.html")

@app.route("/inicio")
def pagina_inicial():
    """Renderiza a página principal do usuário (telasHTML/TelaInicial.html)."""
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

    sucesso = inserir_usuario(
        nome=nome, email=email, senha=senha, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero
    )

    # --- LÓGICA DE REDIRECIONAMENTO ---
    if sucesso:
        # SE DEU CERTO: Redireciona para a rota /inicio, que renderiza TelaInicial.html
        print("Cadastro bem-sucedido. Redirecionando para a página inicial...")
        return redirect(url_for('pagina_inicial'))
    else:
        # SE DEU ERRADO: Volta para a página de cadastro
        print("Falha no cadastro. Redirecionando de volta para o formulário.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
