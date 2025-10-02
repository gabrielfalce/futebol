# Localização: telasHTML/STATIC/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from database import inserir_usuario, buscar_usuarios
import bcrypt

# --- Configuração para servir arquivos manualmente ---

# Define o caminho absoluto para a pasta 'telasHTML'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# A configuração do Flask fica mais simples, pois vamos controlar os arquivos
app = Flask(
    __name__,
    template_folder=project_root
)
app.secret_key = 'sua-chave-secreta-aqui'

# --- ROTAS MANUAIS PARA ARQUIVOS ESTÁTICOS ---

# Rota para servir o CSS da página de cadastro
@app.route('/estilo.css')
def serve_cadastro_css():
    # Procura o arquivo na pasta 'Cadastrar templates'
    return send_from_directory(os.path.join(project_root, 'STATIC', 'Cadastrar templates'), 'estilo.css')

# Rota para servir imagens da pasta 'CriaçãoDeConta'
@app.route('/CriaçãoDeConta/<path:filename>')
def serve_criacao_conta_images(filename):
    return send_from_directory(os.path.join(project_root, 'STATIC', 'CriaçãoDeConta'), filename)

# --- Rotas da Aplicação (sem alterações na lógica) ---

@app.route("/")
def index():
    return render_template("STATIC/Cadastrar templates/cadastrar.html")

# ... (O resto do seu app.py, sem nenhuma alteração) ...

@app.route("/loading")
def tela_de_loading():
    return render_template("Telaloading.html")

@app.route("/inicio")
def pagina_inicial():
    lista_de_usuarios = buscar_usuarios()
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios)

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    numero = request.form.get("numero")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.")
        return redirect(url_for('index'))

    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())

    sucesso = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero
    )

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        flash("Erro ao salvar no banco de dados. Verifique se o e-mail já foi cadastrado.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
