from flask import Flask, send_from_directory, render_template
import os

# Caminhos base
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TELAS_DIR = os.path.join(BASE_DIR, "futebol-main", "telasHTML")
STATIC_DIR = os.path.join(TELAS_DIR, "STATIC")

# Inicializa o app Flask
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TELAS_DIR)

# ROTAS PRINCIPAIS DE PÁGINAS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tela_login")
def tela_login():
    return render_template("telaLogin.html")

@app.route("/tela_inicial")
def tela_inicial():
    return render_template("TelaInicial.html")

@app.route("/tela_user")
def tela_user():
    return render_template("TelaUser.html")

@app.route("/tela_loading")
def tela_loading():
    return render_template("Telaloading.html")

# SERVE ARQUIVOS ESTÁTICOS

@app.route('/STATIC/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

# CONFIGURAÇÃO RENDER OU LOCAL

if __name__ == "__main__":
    # O host='0.0.0.0' é necessário no Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
