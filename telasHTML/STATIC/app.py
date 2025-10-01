from flask import Flask, render_template, request, redirect, url_for
from database import inserir_usuario 

# Configuração do Flask:
# template_folder agora usa o nome EXATO da sua pasta.
# ATENÇÃO: Se o Render tiver problemas com o espaço, esta será a causa.
app = Flask(
    __name__,
    template_folder="Cadastrar templates", # Usa o nome exato com espaço e letra maiúscula
    static_folder="STATIC"                 # Pasta para arquivos estáticos
)

# Rota principal (/)
@app.route("/")
def index():
    # CORREÇÃO FINAL: Usa o nome 'cadastrar.html' (tudo em minúsculas)
    # para corresponder ao que o Render está procurando no log.
    return render_template("cadastrar.html")

# Rota de Cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Aviso: Configure as variáveis SUPABASE_URL/KEY no Render.
        sucesso = inserir_usuario(nome, email, senha)

        if sucesso:
            # Garanta que 'sucesso.html' está na pasta "Cadastrar templates"
            return render_template("sucesso.html") 
        else:
            # Garanta que 'erro.html' está na pasta "Cadastrar templates"
            return render_template("erro.html")

    # Garante a consistência do nome do arquivo
    return render_template("cadastrar.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

### O que acontece agora?

1.  **Template Folder:** O Flask vai procurar os templates dentro da pasta **`Cadastrar templates`** (o que deve funcionar se o Render aceitar o nome com espaço).
2.  **Template File:** O Flask vai procurar pelo arquivo **`cadastrar.html`** (tudo em minúsculas). **Você precisa ter certeza que o nome do arquivo HTML no seu repositório é exatamente `cadastrar.html` (minúsculas).**

Faça o *commit* e o *push* deste último código. Se o erro de `TemplateNotFound` persistir, a causa será o nome da pasta com espaço, e você terá que mudar o nome da pasta (o que pode ser feito localmente e depois *pushado* para o Git, se o Git Web não ajudar).

Boa sorte com o *deploy*! Não esqueça das variáveis do Supabase.
