# /path/to/your/project/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from database import inserir_usuario 

# --- Configuração do Flask ---
# Ajuste os caminhos conforme a estrutura do seu projeto
template_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'templates') # Renomeei para 'templates' por convenção
static_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'static')

app = Flask(
    __name__, 
    template_folder=template_dir, 
    static_folder=static_dir
)

# --- Rotas da Aplicação ---

@app.route("/", methods=['GET'])
def index():
    """Rota para carregar o formulário de cadastro."""
    return render_template("cadastrar.html")

# --- NOVA ROTA: Página Inicial ---
@app.route("/inicio")
def pagina_inicial():
    """Renderiza a página principal do usuário após o login/cadastro."""
    # Esta rota vai servir o seu novo HTML da tela inicial.
    return render_template("tela_inicial.html")

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

    if not all([nome, email, senha, nascimento]):
        print("Erro: Campos obrigatórios não foram preenchidos.")
        # Em caso de erro de validação, volta para o formulário
        return redirect(url_for('index')) 

    sucesso = inserir_usuario(
        nome=nome, email=email, senha=senha, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero
    )

    # --- LÓGICA DE REDIRECIONAMENTO ATUALIZADA ---
    if sucesso:
        # Se o cadastro for bem-sucedido, redireciona para a nova página inicial
        print("Cadastro bem-sucedido. Redirecionando para /inicio...")
        return redirect(url_for('pagina_inicial'))
    else:
        # Se falhar, redireciona de volta para a página de cadastro
        print("Falha no cadastro. Redirecionando de volta para o formulário.")
        return redirect(url_for('index'))

# As rotas /sucesso e /erro foram removidas, pois não são mais usadas.

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
