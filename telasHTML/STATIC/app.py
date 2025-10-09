from flask import Flask, render_template, request, redirect, url_for, flash, session
# Importe as novas funções
from database import register_user, check_user, get_all_users, search_users

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
@app.route('/tela_inicial', methods=['GET'])
def tela_inicial():
    # Verifica se o utilizador está logado
    if 'user_email' in session:
        # Busca todos os usuários cadastrados
        usuarios = get_all_users()
        
        # Renderiza o template, passando a lista de usuários
        return render_template('TelaInicial.html', 
                               usuarios=usuarios, 
                               user_email=session['user_email'])
    else:
        # Se não, redireciona para o login
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))

# Nova Rota para a Busca
@app.route('/search', methods=['GET'])
def search():
    # Protege a rota de busca
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    # Pega o valor do campo 'Pesquisar' que será passado como parâmetro 'q' na URL
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        # Se há uma query, busca usuários filtrados
        usuarios = search_users(search_query)
    else:
        # Se a query está vazia, mostra todos os usuários
        usuarios = get_all_users()
        
    # Renderiza a mesma tela com os resultados da busca
    return render_template('TelaInicial.html', 
                           usuarios=usuarios, 
                           user_email=session['user_email'])


# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_email', None) # Remove o utilizador da sessão
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
