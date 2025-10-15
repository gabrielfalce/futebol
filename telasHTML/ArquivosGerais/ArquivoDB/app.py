import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import inserir_usuario, check_user, get_all_users
import bcrypt
from datetime import datetime

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

# --- Rotas ---

@app.route("/")
def index():
    return render_template("Cadastrar_templates/cadastrar.html") 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        user_data = check_user(email, senha)
        
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    return render_template('TelaDeLogin/login.html') 

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    lista_de_usuarios = get_all_users()
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios)

@app.route("/loading")
def tela_de_loading():
    return render_template("TelaLoading/Telaloading.html")

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
        return redirect(url_for('index'))
        
    # --- Validação e Conversão da Data de Nascimento ---
    try:
        # Interpreta a string como DD/MM/AAAA
        data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
        # Converte para o formato ISO AAAA-MM-DD para o banco
        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
        # Validação adicional: garantir que a data é razoável (ex.: não no futuro)
        if data_obj > datetime.now():
            flash("Erro: A data de nascimento não pode ser no futuro.", 'danger')
            return redirect(url_for('index'))
    except ValueError:
        flash("Erro: A data de nascimento deve ser no formato DD/MM/AAAA (ex: 15/09/2007).", 'danger')
        return redirect(url_for('index'))

    # Hash da senha usando bcrypt
    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())

    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade, 
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero
    )

    if sucesso:
        flash(mensagem, 'success')
        return redirect(url_for('login'))
    else:
        flash(mensagem, 'danger')
        return redirect(url_for('index')) 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
