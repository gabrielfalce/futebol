import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import register_user, check_user, get_all_users # Funções Corretas

# 1. Encontra a RAIZ DA APLICAÇÃO (telasHTML/ArquivosGerais)
# Sobe um nível (..) do ArquivoDB para chegar em ArquivosGerais
app_dir = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.abspath(os.path.join(app_dir, '..')) 

app = Flask(
    __name__,
    template_folder=template_root, # A raiz dos templates é ArquivosGerais
    static_folder=os.path.join(template_root, 'STATIC'), 
    static_url_path='/static'
)
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar'


# Rota principal
@app.route("/")
def index():
    # Caminho corrigido: Cadastrar_templates/cadastrar.html
    return render_template("Cadastrar_templates/cadastrar.html")

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... (lógica de login permanece igual) ...
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if check_user(email, senha):
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    return render_template('TelaDeLogin/login.html') # Caminho correto: TelaDeLogin/login.html


# Rota para a tela inicial
@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    lista_de_usuarios = get_all_users()
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios) # Caminho correto: TelaInicial.html


# Rota de cadastro (POST)
@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    numero = request.form.get("numero")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('index'))

    sucesso, mensagem = register_user(
        nome=nome, email=email, senha=senha_texto_puro, cidade=cidade, 
        posicao=posicao, data_nasc=nascimento, numero=numero
    )

    if sucesso:
        flash(mensagem, 'success')
        return redirect(url_for('login'))
    else:
        flash(mensagem, 'danger')
        return redirect(url_for('index')) 

# Rota de loading
@app.route("/loading")
def tela_de_loading():
    return render_template("Telaloading.html") # Caminho correto: Telaloading.html


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
