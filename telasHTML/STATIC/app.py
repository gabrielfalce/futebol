from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario

# O 'template_folder' AGORA aponta para o nome EXATO da sua pasta: "Cadastrar templates"
# Presumimos que esta pasta está dentro do mesmo diretório que o app.py.
# O 'static_folder' aponta para "STATIC", que também deve estar dentro do diretório do app.py.
#
# Se app.py estiver em '/telasHTML/STATIC/' e a pasta 'Cadastrar templates' estiver
# dentro de 'STATIC', esta configuração está correta.
app = Flask(
    __name__,
    template_folder="Cadastrar templates", # CORREÇÃO: Usando o nome exato que você forneceu
    static_folder="STATIC"                 # Mantendo sua configuração para arquivos estáticos
)

# Rota principal (/)
@app.route("/")
def index():
    # CORREÇÃO: Renderiza 'cadastro.html', pois você não tem 'index.html'
    return render_template("cadastro.html")

# Rota de Cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        sucesso = inserir_usuario(nome, email, senha)

        if sucesso:
            # Garanta que 'sucesso.html' está na pasta 'Cadastrar templates'
            return render_template("sucesso.html") 
        else:
            # Garanta que 'erro.html' está na pasta 'Cadastrar templates'
            return render_template("erro.html")

    return render_template("cadastro.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
