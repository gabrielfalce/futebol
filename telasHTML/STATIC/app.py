from flask import Flask, render_template, request, redirect, url_for

# Importa a função de banco de dados. (Presumimos que 'database.py' existe e está acessível)
from database import inserir_usuario 

# Configuração do Flask:
# - template_folder: "telasHTML" (Os arquivos .html devem estar em telasHTML/STATIC/telasHTML)
# - static_folder: "STATIC" (Os arquivos CSS/JS devem estar em telasHTML/STATIC/STATIC)
#
# NOTA: Esta configuração é válida se o seu app.py estiver no diretório pai de telasHTML/STATIC.
# Se app.py estiver em telasHTML/STATIC/, os caminhos relativos podem precisar de ajuste (ex: template_folder="../telasHTML").
# Mantendo a sua configuração original, mas o caminho no Render é crucial.
app = Flask(
    __name__,
    template_folder="telasHTML",     # Onde o Flask procura por 'render_template'
    static_folder="STATIC"           # Onde o Flask procura por 'url_for('static', ...)'
)

# Rota principal (/)
# Corrigido para carregar "cadastro.html" em vez de "index.html",
# resolvendo o erro 'TemplateNotFound: index.html'.
@app.route("/")
def index():
    # A rota raiz agora mostra a página de cadastro, pois não há 'index.html'
    return render_template("cadastro.html")

# Rota de Cadastro
# Aceita métodos GET (para exibir o formulário) e POST (para processar o envio)
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        # Pega os dados do formulário
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Tenta inserir no banco de dados (função importada de 'database')
        sucesso = inserir_usuario(nome, email, senha)

        if sucesso:
            # Redireciona ou renderiza a página de sucesso
            # É recomendado usar 'redirect' para evitar reenvio de formulário
            return render_template("sucesso.html") 
        else:
            # Redireciona ou renderiza a página de erro
            return render_template("erro.html")

    # Para requisições GET, apenas exibe o formulário
    return render_template("cadastro.html")

if __name__ == "__main__":
    # Configuração de execução para o ambiente de desenvolvimento e produção (Render)
    app.run(host="0.0.0.0", port=5000, debug=True)
