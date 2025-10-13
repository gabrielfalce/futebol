import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
# CORREÇÃO CRÍTICA: Importando os nomes corretos do database.py
from database import register_user, check_user, get_all_users
import bcrypt

# --- Configuração Robusta de PATHS ---
# 1. Encontra o diretório onde app.py está (ArquivoDB)
base_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Sobe dois níveis (../..) para chegar em 'telasHTML/ArquivosGerais' (raiz dos templates)
template_root = os.path.abspath(os.path.join(base_dir, '..', '..')) 

app = Flask(
    __name__,
    template_folder=template_root,
    # Define a pasta estática como STATIC dentro da raiz dos templates
    static_folder=os.path.join(template_root, 'STATIC'), 
    static_url_path='/static'
)
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar'


# Rota principal (redireciona para o cadastro)
@app.route("/")
def index():
    # CORREÇÃO CRÍTICA: Usa a pasta Cadastrar_templates (SEM ESPAÇOS)
    return render_template("Cadastrar_templates/cadastrar.html")

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if check_user(email, senha):
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    # Assumindo que a tela de login está em 'telasHTML/ArquivosGerais/TelaDeLogin/login.html'
    return render_template('TelaDeLogin/login.html')


# Rota para a tela inicial (exibindo usuários)
@app.route("/inicio")
def pagina_inicial():
    # Proteção de rota: só acessa se estiver logado
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    # CORREÇÃO CRÍTICA: Usando a função correta do database.py (get_all_users)
    lista_de_usuarios = get_all_users()
    # Assume que TelaInicial.html está na raiz dos templates
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios)


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

    # CORREÇÃO CRÍTICA: Usando a função correta do database.py (register_user)
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
    return render_template("Telaloading.html")


if __name__ == '__main__':
    # Configuração para rodar no Render (Gunicorn usa o comando 'gunicorn app:app')
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
