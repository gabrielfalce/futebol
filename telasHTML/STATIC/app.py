import os
from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario 

# --- Configuração do Flask (mantida para sua estrutura de arquivos) ---
project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, '..')
static_dir = project_root

app = Flask(
    __name__, 
    template_folder=template_dir, 
    static_folder=static_dir
)

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    """
    --- CORREÇÃO APLICADA AQUI ---
    Esta é a rota principal. Ela DEVE carregar a página de cadastro.
    """
    return render_template("cadastrar.html") # Apontando para o arquivo correto.

@app.route("/loading")
def tela_de_loading():
    """Renderiza a página de loading intermediária (telasHTML/TelaLoading.html)."""
    return render_template("TelaLoading.html")

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

    if sucesso:
        # Se o cadastro for bem-sucedido, redireciona para a tela de loading.
        return redirect(url_for('tela_de_loading'))
    else:
        # Se falhar, volta para a página de cadastro.
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
