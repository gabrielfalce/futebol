# Localização: telasHTML/STATIC/app.py

import os
from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario 

# --- Configuração do Flask (SIMPLIFICADA E CORRIGIDA) ---

# O diretório onde o app.py está: '.../telasHTML/STATIC'
project_root = os.path.dirname(os.path.abspath(__file__))

# A pasta de templates (HTML) está um nível ACIMA: '.../telasHTML'
template_dir = os.path.join(project_root, '..')

# A pasta de arquivos estáticos (CSS, JS, Imagens) é a pasta ATUAL.
static_dir = project_root

app = Flask(
    __name__, 
    template_folder=template_dir, # Aponta para a pasta 'telasHTML'
    static_folder=static_dir,
    static_url_path=''
)

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    """Carrega a página de cadastro."""
    # --- CORREÇÃO APLICADA AQUI ---
    # Especificamos o caminho da subpasta diretamente no render_template.
    return render_template("STATIC/Cadastrar templates/cadastrar.html")

@app.route("/loading")
def tela_de_loading():
    """Renderiza a página de loading intermediária."""
    return render_template("TelaLoading.html")

@app.route("/inicio")
def pagina_inicial():
    """Renderiza a página principal do usuário."""
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

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
