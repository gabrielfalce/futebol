# Localização: telasHTML/STATIC/app.py

import os
# Adicione 'flash' às importações do Flask
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

# --- CHAVE SECRETA (Necessária para flash messages) ---
# Adicione uma chave secreta para a sessão do Flask. Pode ser qualquer string.
app.secret_key = 'uma-chave-secreta-muito-segura-pode-mudar-depois'

# --- Rotas ---

@app.route("/")
def index():
    return render_template("STATIC/Cadastrar templates/cadastrar.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    # ... (código para pegar os dados do formulário)
    nome = request.form.get("nome")
    email = request.form.get("email")
    # ... etc.

    sucesso = inserir_usuario(...) # Passa todos os dados

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        # --- ALTERAÇÃO AQUI ---
        # Se falhar, envie uma mensagem de erro para a próxima requisição
        flash("Erro ao realizar o cadastro. Verifique os dados e tente novamente.")
        return redirect(url_for('index'))

# ... (outras rotas)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
