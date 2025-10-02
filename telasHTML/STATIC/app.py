# Localização: /app.py (na raiz do projeto)

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import inserir_usuario, buscar_usuarios 

# O Flask agora encontra as pastas 'templates' e 'static' automaticamente!
app = Flask(__name__)
app.secret_key = 'uma-chave-secreta-muito-segura-pode-mudar-depois'

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    return render_template("cadastrar.html")

@app.route("/loading")
def tela_de_loading():
    return render_template("Telaloading.html")

@app.route("/inicio")
def pagina_inicial():
    lista_de_usuarios = buscar_usuarios()
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios)

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    # ... (lógica de cadastro, sem alterações) ...
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    numero = request.form.get("numero")

    if not all([nome, email, senha, cidade, posicao, nascimento, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.")
        return redirect(url_for('index'))

    sucesso = inserir_usuario(
        nome=nome, email=email, senha=senha, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero
    )

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        flash("Erro ao salvar no banco de dados. Verifique se o e-mail já foi cadastrado e tente novamente.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
