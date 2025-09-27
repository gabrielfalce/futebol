from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario

app = Flask(__name__)

# Rota principal (exibe o formulário)
@app.route("/")
def home():
    return render_template("cadastro.html")

# Rota para processar o formulário
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]
    
    if inserir_usuario(nome, email, senha):
        return redirect(url_for("sucesso"))
    else:
        return "Erro no cadastro. Tente novamente."

# Rota de sucesso após cadastro
@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

if __name__ == "__main__":
    app.run(debug=True)
