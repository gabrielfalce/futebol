import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from database import inserir_usuario 

# --- Configuração do Flask ---

# Certifique-se de que estes caminhos estão corretos
template_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'Cadastrar templates')
static_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'static')
image_assets_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'CriaçãoDeConta')

app = Flask(
    __name__, 
    template_folder=template_dir, 
    static_folder=static_dir
)

@app.route('/image_assets/<path:filename>')
def image_asset(filename):
    """Rota customizada para servir ativos da pasta CriaçãoDeConta."""
    return send_from_directory(image_assets_dir, filename)

# --- Rotas da Aplicação ---

# Rota para carregar o formulário (Método GET)
@app.route("/", methods=['GET'])
def index():
    return render_template("cadastrar.html")


# Rota para processar o formulário de cadastro (Método POST)
@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    # 1. Extrair TODOS os dados do formulário, incluindo o NUMERO
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    # NOVO CAMPO: Numero da camisa
    numero = request.form.get("numero") 

    # Verificação básica se campos obrigatórios estão presentes
    if not all([nome, email, senha]):
        return redirect(url_for('erro_pagina')) 

    # 2. Inserir no Supabase (PASSANDO TODOS OS CAMPOS, incluindo NUMERO)
    if inserir_usuario(nome, email, senha, cidade, posicao, nascimento, numero):
        # 3. Redirecionar para uma página de sucesso
        return redirect(url_for('sucesso_pagina'))
    else:
        # 4. Redirecionar para uma página de erro
        return redirect(url_for('erro_pagina'))


# Rota de Sucesso
@app.route("/sucesso")
def sucesso_pagina():
    return "<h1>Sucesso!</h1><p>Sua conta foi criada com sucesso com todos os dados.</p><p><a href='/'>Voltar</a></p>"


# Rota de Erro
@app.route("/erro")
def erro_pagina():
    return "<h1>Erro</h1><p>Não foi possível criar sua conta. Verifique os logs e se as colunas da tabela Supabase estão corretas.</p><p><a href='/'>Voltar</a></p>"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
