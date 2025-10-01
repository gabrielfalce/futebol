# /path/to/your/project/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from database import inserir_usuario 

# --- Configuração do Flask ---
# Nenhuma alteração necessária aqui, mas certifique-se de que os caminhos estão corretos para o seu ambiente.
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

@app.route("/", methods=['GET'])
def index():
    """Rota para carregar o formulário de cadastro."""
    return render_template("cadastrar.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    """Rota para processar os dados do formulário de cadastro."""
    # Extrai todos os dados do formulário
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    numero = request.form.get("numero") 

    # Verificação básica para garantir que os campos essenciais não estão vazios
    if not all([nome, email, senha, nascimento]):
        print("Erro: Campos obrigatórios não foram preenchidos.")
        return redirect(url_for('erro_pagina')) 

    # Chama a função de inserção (agora corrigida) do database.py
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
        # Se a inserção for bem-sucedida, redireciona para a página de sucesso
        return redirect(url_for('sucesso_pagina'))
    else:
        # Se a inserção falhar, redireciona para a página de erro
        return redirect(url_for('erro_pagina'))

# Rota de Sucesso
@app.route("/sucesso")
def sucesso_pagina():
    return "<h1>Sucesso!</h1><p>Sua conta foi criada com sucesso.</p><p><a href='/'>Voltar</a></p>"

# Rota de Erro
@app.route("/erro")
def erro_pagina():
    return "<h1>Erro no Cadastro</h1><p>Não foi possível criar sua conta. Verifique os logs do servidor para mais detalhes.</p><p><a href='/'>Tentar novamente</a></p>"

if __name__ == "__main__":
    # O Render usa a variável de ambiente PORT para rodar a aplicação
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

