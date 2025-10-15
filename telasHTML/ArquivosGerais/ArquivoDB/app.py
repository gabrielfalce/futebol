import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import inserir_usuario, check_user, get_all_users, get_user_by_email
import bcrypt
from datetime import datetime
from jinja2.exceptions import TemplateNotFound

# --- Configuração de Caminhos e Flask ---
app_dir = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.abspath(os.path.join(app_dir, '..')) 

app = Flask(
    __name__,
    template_folder=template_root,
    static_folder=os.path.join(template_root, 'STATIC'), 
    static_url_path='/static'
)
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar'

# --- Filtro para formatar data ---
@app.template_filter('format_date')
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return date_str

# --- Rotas ---

@app.route("/")
def index():
    return redirect(url_for('pagina_inicial'))  # Redireciona para /inicio

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        user_data = check_user(email, senha)
        
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    try:
        return render_template('TelaDeLogin/telaLogin.html')
    except TemplateNotFound:
        print(f"Template 'TelaDeLogin/telaLogin.html' not found in {app.template_folder}")
        flash('Erro interno: Template de login não encontrado.', 'danger')
        return redirect(url_for('index'))

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    lista_de_usuarios = get_all_users()
    return render_template("TelaInicial/TelaInicial.html", usuarios=lista_de_usuarios)

@app.route("/usuario")
def pagina_usuario():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    user_data = get_user_by_email(session['user_email'])
    if user_data:
        return render_template("TelaDeUsuario/TelaUser.html", usuario=user_data)
    else:
        flash('Erro: Dados do usuário não encontrados.', 'danger')
        return redirect(url_for('index'))

@app.route("/loading")
def tela_de_loading():
    return render_template("TelaLoading/Telaloading.html")

@app.route("/cadastro")
def cadastro():
    return render_template("Cadastrar_templates/cadastrar.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento_str = request.form.get("nascimento")
    numero = request.form.get("numero")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento_str, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('cadastro'))
        
    # --- Validação e Conversão da Data de Nascimento ---
    try:
        data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
        if data_obj > datetime.now():
            flash("Erro: A data de nascimento não pode ser no futuro.", 'danger')
            return redirect(url_for('cadastro'))
    except ValueError:
        flash("Erro: A data de nascimento deve ser no formato DD/MM/AAAA (ex: 15/09/2007).", 'danger')
        return redirect(url_for('cadastro'))

    # Hash da senha usando bcrypt
    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())

    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade, 
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero
    )

    if sucesso:
        session['user_email'] = email  # Loga o usuário automaticamente após cadastro
        flash(mensagem, 'success')
        return redirect(url_for('tela_de_loading'))
    else:
        flash(mensagem, 'danger')
        return redirect(url_for('cadastro')) 

@app.route("/api/usuarios", methods=['GET'])
def buscar_usuarios():
    query = request.args.get('q', '').lower()
    usuarios = get_all_users()
    if query:
        usuarios = [u for u in usuarios if query in u['nome'].lower() or query in u['cidade'].lower()]
    return jsonify(usuarios)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
