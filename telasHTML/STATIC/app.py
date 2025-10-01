from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario

# Caminhos corrigidos: templates dentro de telasHTML, arquivos estáticos em STATIC
app = Flask(
    __name__,
    template_folder="telasHTML",   # onde ficam os .html
    static_folder="STATIC"         # onde ficam CSS, JS, imagens
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Tenta inserir no banco
        sucesso = inserir_usuario(nome, email, senha)

        if sucesso:
            return render_template("sucesso.html")
        else:
            # Aqui ainda redireciona para erro.html, mas você pode remover se quiser
            return render_template("erro.html")

    return render_template("cadastro.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
