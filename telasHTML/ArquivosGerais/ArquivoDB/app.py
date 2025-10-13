import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import inserir_usuario, check_user, get_all_users # Funções Corretas
import bcrypt # Para hashing da senha

# --- Configuração de Caminhos e Flask ---

# Sobe um nível (..) do ArquivoDB para chegar em ArquivosGerais, que é a RAIZ dos templates
app_dir = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.abspath(os.path.join(app_dir, '..')) 

app = Flask(
    __name__,
    template_folder=template_root, # A raiz dos templates é 'ArquivosGerais'
    # Define a pasta STATIC dentro de ArquivosGerais
    static_folder=os.path.join(template_root, 'STATIC'), 
    static_url_path='/static'
)
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar' # Chave para usar sessões e flash messages

# --- Rotas ---

# Rota principal (Cadastro)
@app.route("/")
def index():
    # Caminho corrigido: 'Cadastrar_templates' (com underscore, se essa for a pasta no seu GitHub)
    return render_template("Cadastrar_templates/cadastrar.html") 

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        # A função check_user cuida do hashing e comparação
        user_data = check_user(email, senha)
        
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    # Caminho corrigido: 'TelaDeLogin/login.html'
    return render_template('TelaDeLogin/login.html') 


# Rota para a tela inicial
@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    lista_de_usuarios = get_all_users()
    # Caminho corrigido: 'TelaInicial.html'
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios)


# Rota de loading
@app.route("/loading")
def tela_de_loading():
    # Caminho corrigido: 'TelaLoading/Telaloading.html'
    return render_template("TelaLoading/Telaloading.html")


# Rota de cadastro (POST)
@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") # Campo do formulário
    numero = request.form.get("numero")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('index'))

    # Hash da senha usando bcrypt
    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())

    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero # Passa 'nascimento'
    )

    if sucesso:
        flash(mensagem, 'success')
        return redirect(url_for('login'))
    else:
        flash(mensagem, 'danger')
        return redirect(url_for('index')) 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    # Para o Render usar o Gunicorn, use esta porta, mas para testar localmente, o Flask pode usar 5000.
    app.run(host='0.0.0.0', port=port, debug=True)
