import os
from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario 

# --- Configuração do Flask ---
# O Flask automaticamente procura a pasta 'templates' e 'static' no mesmo nível.
# Vamos ajustar os caminhos para refletir a estrutura recomendada.
project_root = os.path.join(os.getcwd(), 'telasHTML', 'STATIC')
template_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')

app = Flask(
    __name__, 
    template_folder=template_dir, 
    static_folder=static_dir
)

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    """Rota para carregar o formulário de cadastro."""
    return render_template("cadastrar.html")

@app.route("/inicio")
def pagina_inicial():
    """Renderiza a página principal com a lista de usuários."""
    return render_template("tela_inicial.html")

@app.route("/perfil")
def perfil_usuario():
    """Renderiza a página de perfil do usuário logado."""
    # Esta é a rota para o link do botão de perfil.
    # Por enquanto, pode redirecionar para a tela inicial ou renderizar outra página.
    # Exemplo: return render_template("perfil.html")
    return "<h1>Página do Perfil do Usuário</h1>" # Placeholder

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    """Processa os dados do formulário de cadastro."""
    # ... (código para extrair dados do formulário) ...
    nome = request.form.get("nome")
    email = request.form.get("email")
    # ... etc.

    sucesso = inserir_usuario(...) # Passa todos os dados

    if sucesso:
        print("Cadastro bem-sucedido. Redirecionando para /inicio...")
        return redirect(url_for('pagina_inicial'))
    else:
        print("Falha no cadastro. Redirecionando de volta para o formulário.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
