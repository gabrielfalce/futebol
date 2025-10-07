from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import register_user, check_user

# Configuração da aplicação Flask
# Os templates estão em subdiretórios, então ajustamos os caminhos
app = Flask(__name__, 
            template_folder='telasHTML/STATIC', 
            static_folder='telasHTML/STATIC')

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
            return redirect(url_for('login')) # Redireciona para o login após sucesso
        else:
            flash(message, 'danger') # Mostra o erro (ex: email já existe)
    
    # Renderiza a página de cadastro
    return render_template('Cadastrar templates/cadastrar.html')

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Verifica as credenciais
        if check_user(email, senha):
            session['user_email'] = email # Guarda o email do utilizador na sessão
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    # Renderiza a página de login
    return render_template('Login templates/login.html')

# Rota para a tela inicial (protegida)
@app.route('/tela_inicial')
def tela_inicial():
    # Verifica se o utilizador está logado
    if 'user_email' in session:
        # Se estiver logado, mostra a página
        return render_template('TelaInicial.html', user_email=session['user_email'])
    else:
        # Se não, redireciona para o login
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_email', None) # Remove o utilizador da sessão
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
