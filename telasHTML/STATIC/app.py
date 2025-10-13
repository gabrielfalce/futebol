import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import register_user, check_user, get_all_users, search_users 

# --- CORREÇÃO ROBUSTA DE PATHS (Essencial para o Render/Flask) ---
# O app.py está dentro de 'telasHTML/STATIC', então o root é a pasta 'telasHTML'.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__, 
            # template_folder aponta para a pasta 'telasHTML'
            template_folder=project_root,  
            # static_folder aponta para a pasta 'telasHTML/STATIC'
            static_folder=os.path.join(project_root, 'STATIC'))
# -------------------------------------------------------------------

# Chave secreta para mensagens flash e sessões
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar'

# Rota principal que redireciona para o cadastro
@app.route('/')
def index():
    # CORREÇÃO DEFINITIVA DO PATH: Usando Cadastrar_templates (com underscore)
    return redirect(url_for('cadastrar'))

# Rota para a página de cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        # Recolhe os dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cidade = request.form['cidade']
        numero = request.form['numero']
        posicao = request.form['posicao']
        data_nasc = request.form['nascimento']

        # Tenta registar o utilizador
        success, message = register_user(nome, email, senha, cidade, numero, posicao, data_nasc)

        if success:
            flash(message, 'success')
            return redirect(url_for('login')) 
        else:
            flash(message, 'danger')
            return render_template('STATIC/Cadastrar_templates/cadastrar.html') # Caso de erro no POST
    
    # Rota GET: Renderiza a página de cadastro
    # CORREÇÃO DEFINITIVA DO PATH: Usando Cadastrar_templates (com underscore)
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
            
    # CORREÇÃO DO PATH: Assumindo que a pasta é 'Login_templates'
    return render_template('STATIC/Login_templates/login.html')

# Rota para a tela inicial (protegida) e com exibição de usuários
@app.route('/tela_inicial', methods=['GET'])
def tela_inicial():
    if 'user_email' in session:
        # Pega a query de busca (se houver)
        search_query = request.args.get('q', '').strip()
        
        if search_query:
            usuarios = search_users(search_query)
        else:
            usuarios = get_all_users()
        
        # Caminho: telasHTML/TelaInicial.html
        return render_template('TelaInicial.html', 
                               usuarios=usuarios, 
                               user_email=session['user_email'])
    else:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Usar porta 8080 ou a variável de ambiente PORT do Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
