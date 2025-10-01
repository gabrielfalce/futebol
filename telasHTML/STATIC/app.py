import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# Importamos a função corrigida do Supabase
from database import inserir_usuario 

# --- Configuração do Flask ---

# O nome da pasta que contém o HTML (templates)
template_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'Cadastrar templates')

# O nome da pasta que contém o CSS (static)
static_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'static')

app = Flask(
    __name__, 
    template_folder=template_dir, 
    static_folder=static_dir
)

# Adicionamos uma rota estática customizada para a pasta da sua imagem, 
# se ela não estiver na pasta 'static'.
# Se a 'bolaverde 3.png' foi movida para 'static', esta rota é desnecessária, 
# mas mantê-la não causa problemas.
image_assets_dir = os.path.join(os.getcwd(), 'telasHTML', 'STATIC', 'CriaçãoDeConta')

@app.route('/image_assets/<path:filename>')
def image_asset(filename):
    """Rota customizada para servir ativos da pasta CriaçãoDeConta."""
    return send_from_directory(image_assets_dir, filename)

# --- Rotas da Aplicação ---

# Rota para carregar o formulário (Método GET)
@app.route("/", methods=['GET'])
def index():
    # Isso assume que você tem um template chamado 'cadastrar.html'
    return render_template("cadastrar.html")


# Rota para processar o formulário de cadastro (Método POST)
@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    # 1. Extrair os dados do formulário
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    # Campos que não estão sendo usados na função inserir_usuario, mas são capturados:
    # cidade = request.form.get("cidade")
    # numero = request.form.get("numero")
    # posicao = request.form.get("posicao")
    # nascimento = request.form.get("nascimento")
    
    # Verificação básica se todos os campos principais estão presentes
    if not all([nome, email, senha]):
        # Você deve ter uma página de erro para redirecionar
        return redirect(url_for('erro_pagina')) 

    # 2. Inserir no Supabase (usando a função do database.py)
    if inserir_usuario(nome, email, senha):
        # 3. Redirecionar para uma página de sucesso (crie uma se não tiver)
        return redirect(url_for('sucesso_pagina'))
    else:
        # 4. Redirecionar para uma página de erro
        return redirect(url_for('erro_pagina'))


# Rota de Sucesso (Crie o template 'sucesso.html')
@app.route("/sucesso")
def sucesso_pagina():
    return "<h1>Sucesso!</h1><p>Sua conta foi criada com sucesso.</p><p><a href='/'>Voltar</a></p>"
    # Ou use render_template("sucesso.html") se você criar o arquivo


# Rota de Erro (Crie o template 'erro.html')
@app.route("/erro")
def erro_pagina():
    return "<h1>Erro</h1><p>Não foi possível criar sua conta. Verifique os logs do servidor.</p><p><a href='/'>Voltar</a></p>"
    # Ou use render_template("erro.html") se você criar o arquivo


if __name__ == "__main__":
    # Quando em ambiente de produção (Render), use gunicorn. 
    # Mantenha o app.run() para testes locais.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
