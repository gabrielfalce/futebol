from flask import Flask, render_template, request, redirect, url_for
# Importa a função de banco de dados.
from database import inserir_usuario 

# Configuração do Flask:
# Assume-se que você renomeou a pasta de templates para 'templates' 
# e que esta está no mesmo nível que app.py e a pasta 'STATIC'.
app = Flask(
    __name__,
    template_folder="templates", # Pasta Padrão e Segura (sem espaços)
    static_folder="STATIC"       # Pasta para CSS, JS, Imagens
)

# Rota principal (/)
@app.route("/")
def index():
    # CORRIGIDO: Usa o nome exato do arquivo (com 'C' maiúsculo)
    return render_template("cadastrar.html")

# Rota de Cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        # Pega os dados do formulário
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Tenta inserir no banco de dados (função importada de 'database')
        # Este passo só funcionará após você configurar as variáveis de ambiente do Supabase.
        sucesso = inserir_usuario(nome, email, senha)

        if sucesso:
            # Garanta que 'sucesso.html' está na pasta 'templates'
            return render_template("sucesso.html") 
        else:
            # Garanta que 'erro.html' está na pasta 'templates'
            return render_template("erro.html")

    # Para requisições GET ou falhas, exibe o formulário.
    # CORRIGIDO: Usa o nome exato do arquivo (com 'C' maiúsculo)
    return render_template("Cadastrar.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
