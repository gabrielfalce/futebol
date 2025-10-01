from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from database import inserir_usuario 

# Configuração do Flask:
# 1. 'template_folder' aponta para onde estão os HTMLs ('Cadastrar templates')
# 2. 'static_folder' aponta para onde está o seu CSS (a pasta 'static')
app = Flask(
    __name__,
    template_folder="Cadastrar templates", 
    static_folder="static"                 
)

# Rota Estática Customizada para a Imagem
# ATENÇÃO: A URL '/image_assets/' mapeia para a pasta 'CriaçãoDeConta', 
# que está no mesmo nível que 'app.py'.
@app.route('/image_assets/<path:filename>')
def image_assets(filename):
    IMAGE_FOLDER = 'CriaçãoDeConta'
    # Esta função busca o arquivo na pasta 'CriaçãoDeConta'
    return send_from_directory(IMAGE_FOLDER, filename)


# Rota principal (/)
@app.route("/")
def index():
    return render_template("cadastrar.html")

# Rota de Cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        # Estes são os campos que seu database.py espera
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        
        # Lembrete: O cadastro falhará se SUPABASE_URL/KEY não estiverem no Render.
        sucesso = inserir_usuario(nome, email, senha)

        if sucesso:
            return render_template("sucesso.html") 
        else:
            return render_template("erro.html")

    return render_template("cadastrar.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
