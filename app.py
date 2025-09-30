from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario

app = Flask(__name__)

# Rota principal (exibe o formulário)
@app.route("/")
def home():
    return render_template("cadastrar.html")


# Rota para processar o formulário
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]
    cidade = request.form["cidade"]
    numero = request.form["numero"]
    posicao = request.form["posicao"]
    nascimento = request.form["nascimento"]

    print(f"Processando cadastro: nome={nome}, email={email}, cidade={cidade}, numero={numero}, posicao={posicao}, nascimento={nascimento}")  # Debug

    if inserir_usuario(nome, email, senha, cidade, numero, posicao, nascimento):
        return redirect(url_for("sucesso"))
    else:
        return "Erro no cadastro. Tente novamente."


# Rota de sucesso após cadastro
@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")


# Para rodar localmente (no Render o gunicorn chama app:app)
if __name__ == "__main__":
    app.run(debug=True)
