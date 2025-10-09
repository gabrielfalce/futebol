import os # NOVO: Necessário para manipular caminhos de arquivo
from flask import Flask, render_template, request, redirect, url_for, flash, session
# Importa as novas funções de busca (necessário que estejam em database (2).py)
from database import register_user, check_user, get_all_users, search_users 

# --- CORREÇÃO DO CAMINHO CRÍTICA ---
# app.py está em 'telasHTML/STATIC'. 
# basedir é a pasta atual (STATIC).
basedir = os.path.dirname(__file__) 
# template_base sobe um nível (..) para 'telasHTML'.
template_base = os.path.join(basedir, '..') 

# Configuração da aplicação Flask
app = Flask(__name__, 
            template_folder=template_base,  # Base: telasHTML
            static_folder=basedir)          # Estático: telasHTML/STATIC
# -----------------------------------

# Chave secreta para mensagens flash e sessões
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar'

# Rota principal que redireciona para o cadastro
@app.route('/')
def index():
    return redirect(url_for('cadastrar'))

# Rota para a página de cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cidade = request.form['cidade']
        numero = request.form['numero']
        posicao = request.form['posicao']
        data_nasc = request.form['nascimento']

        success, message = register_user(nome, email, senha, cidade, numero, posicao, data_nasc)

        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
    
    # Caminho correto em relação à pasta 'telasHTML'
    return render_template('STATIC/Cadastrar_templates/cadastrar.html')

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if check_user(email, senha):
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    # Caminho correto em relação à pasta 'telasHTML'
    return render_template('STATIC/Login_templates/login.html')

# Rota para a tela inicial (protegida) e com exibição de usuários
@app.route('/tela_inicial', methods=['GET'])
def tela_inicial():
    if 'user_email' in session:
        # Busca todos os usuários cadastrados
        # Esta função precisa estar no seu database.py
        usuarios = get_all_users() 
        
        # Caminho correto em relação à pasta 'telasHTML'
        return render_template('TelaInicial.html', 
                               usuarios=usuarios, 
                               user_email=session['user_email'])
    else:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))

# Nova Rota para a Busca
@app.route('/search', methods=['GET'])
def search():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        # Busca usuários filtrados
        usuarios = search_users(search_query) # Esta função precisa estar no seu database.py
    else:
        # Mostra todos os usuários se a busca for vazia
        usuarios = get_all_users()
        
    return render_template('TelaInicial.html', 
                           usuarios=usuarios, 
                           user_email=session['user_email'])


# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
