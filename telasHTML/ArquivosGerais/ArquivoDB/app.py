import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile, get_user_by_id, update_password
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Assumindo que a pasta 'telasHTML' é a raiz do projeto (dois níveis acima de app.py)
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..')) 

app = Flask(
    __name__,
    template_folder=BASE_DIR  # Define a pasta raiz para os templates
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")

# Diretório para uploads (relativo a BASE_DIR)
UPLOAD_FOLDER_RELATIVE = 'ArquivosGerais/TelaDeUsuario/imagens/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

# Decorador para exigir login em rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# === ROTAS DEDICADAS PARA ARQUIVOS ESTÁTICOS (ASSETS) ===

@app.route('/login-assets/<path:filename>')
def login_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'telaDeLogin')
    return send_from_directory(dir_path, filename)

@app.route('/loading-assets/<path:filename>')
def loading_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'TelaLoading')
    return send_from_directory(dir_path, filename)

@app.route('/cadastro-assets/<path:filename>')
def cadastro_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'Cadastrar_templates')
    return send_from_directory(dir_path, filename)

@app.route('/inicio-assets/<path:filename>')
def inicio_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'TelaInicial')
    return send_from_directory(dir_path, filename)

@app.route('/user-assets/<path:filename>')
def user_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'TelaDeUsuario')
    return send_from_directory(dir_path, filename)
    
@app.route('/feed-assets/<path:filename>')
def feed_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'TelaFeed')
    return send_from_directory(dir_path, filename)

@app.route('/chat-assets/<path:filename>')
def chat_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'ArquivosGerais', 'TelaChat')
    return send_from_directory(dir_path, filename)

@app.route('/recuperar-senha-assets/<path:filename>')
def recuperar_senha_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'RecuperarSenha')
    return send_from_directory(dir_path, filename)

@app.route('/serve_static_files/<path:filename>')
def serve_static_files(filename):
    """Serve arquivos da raiz do projeto, útil para imagens de perfil."""
    return send_from_directory(BASE_DIR, filename)

# === ROTAS DO APLICATIVO ===

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user_data = check_user(email, senha)
        if user_data:
            session['user_email'] = email
            session['user_id'] = user_data.get('id')
            session['user_name'] = user_data.get('nome')
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('tela_loading', next_page='pagina_inicial'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))
    return render_template("ArquivosGerais/telaDeLogin/telaLogin.html")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            cidade = request.form['cidade']
            posicao = request.form['posicao']
            nascimento_str = request.form['nascimento']
            # CORREÇÃO: Pega o valor do formulário que corresponde à 'numero_camisa'
            numero_camisa = request.form['numero']

            try:
                nascimento_formatado = datetime.strptime(nascimento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                nascimento_formatado = nascimento_str
            
            # Passa 'numero_camisa' para a função de registro
            success, message = register_user(nome, email, senha, cidade, posicao, nascimento_formatado, numero_camisa)
            
            if success:
                user_data = check_user(email, senha)
                if user_data:
                    session['user_email'] = email
                    session['user_id'] = user_data.get('id')
                    session['user_name'] = user_data.get('nome')
                    flash(message, 'success')
                    return redirect(url_for('tela_loading', next_page='pagina_inicial'))
                else:
                    flash('Cadastro realizado, mas falha no login automático. Faça o login.', 'warning')
                    return redirect(url_for('login'))
            else:
                flash(message, 'danger')
                return redirect(url_for('cadastro'))
        except Exception as e:
            print(f"ERRO geral no cadastro: {e}")
            flash('Ocorreu um erro inesperado ao tentar cadastrar.', 'danger')
            return redirect(url_for('cadastro'))
    return render_template("ArquivosGerais/Cadastrar_templates/cadastrar.html")

@app.route("/loading/<next_page>")
def tela_loading(next_page):
    return render_template("ArquivosGerais/TelaLoading/Telaloading.html", next_url=url_for(next_page), tempo_loading=2500)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route("/inicio")
@login_required
def pagina_inicial():
    users = get_all_users()
    current_user_email = session.get('user_email')
    if users:
        users = [user for user in users if user.get('email') != current_user_email]
    else:
        users = []
    return render_template("ArquivosGerais/TelaInicial/TelaInicial.html", users=users)

@app.route("/perfil/", defaults={'user_id': None})
@app.route("/perfil/<int:user_id>")
@login_required
def pagina_usuario(user_id):
    is_owner = user_id is None or user_id == session.get('user_id')
    if is_owner:
        usuario = get_user_by_email(session.get('user_email'))
    else:
        usuario = get_user_by_id(user_id)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))
    return render_template("ArquivosGerais/TelaDeUsuario/TelaUser.html", usuario=usuario, is_owner=is_owner)

@app.route("/editar_perfil", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    user_email = session.get('user_email')
    usuario = get_user_by_email(user_email)
    if not usuario:
        flash('Erro ao carregar dados do usuário.', 'danger')
        return redirect(url_for('pagina_inicial'))

    if request.method == 'POST':
        update_data = {}
        if request.form.get('nome'): update_data['nome'] = request.form.get('nome')
        if request.form.get('cidade'): update_data['cidade'] = request.form.get('cidade')
        if request.form.get('posicao'): update_data['posicao'] = request.form.get('posicao')
        # CORREÇÃO: Mapeia o campo 'numero' do formulário para a coluna 'numero_camisa'
        if request.form.get('numero'): update_data['numero_camisa'] = request.form.get('numero')

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                full_upload_dir = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
                os.makedirs(full_upload_dir, exist_ok=True)
                file.save(os.path.join(full_upload_dir, filename))
                db_path = os.path.join(UPLOAD_FOLDER_RELATIVE, filename).replace('\\', '/')
                # CORREÇÃO: O nome da coluna para a imagem é 'profile_image_url'
                update_data['profile_image_url'] = db_path

        if update_data:
            if update_user_profile(user_email, **update_data):
                flash('Perfil atualizado com sucesso!', 'success')
            else:
                flash('Falha ao atualizar o perfil.', 'danger')
        else:
            flash('Nenhuma alteração detectada.', 'info')
        return redirect(url_for('editar_perfil'))

    return render_template("ArquivosGerais/TelaDeUsuario/editar_perfil.html", usuario=usuario)

@app.route("/feed")
@login_required
def pagina_feed():
    return render_template("ArquivosGerais/TelaFeed/feed.html")

@app.route("/chat/<int:destinatario_id>")
@login_required
def chat_with_user(destinatario_id):
    if session.get('user_id') == destinatario_id:
        flash('Você não pode conversar consigo mesmo.', 'danger')
        return redirect(url_for('pagina_inicial'))
    remetente = get_user_by_id(session.get('user_id'))
    destinatario = get_user_by_id(destinatario_id)
    if not remetente or not destinatario:
        flash('Usuário para chat não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))
    return render_template("ArquivosGerais/TelaChat/chat.html", remetente=remetente, destinatario=destinatario)

@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        flash(f'Se o e-mail {email} estiver cadastrado, um link de redefinição de senha foi enviado.', 'info')
        return redirect(url_for('login'))
    return render_template("RecuperarSenha/esqueci_senha.html")

@app.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    email = request.args.get('email') # Simulação, idealmente usaria um token seguro
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        if email and nova_senha and len(nova_senha) >= 6:
            if update_password(email, nova_senha):
                flash('Sua senha foi redefinida com sucesso. Faça o login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Falha ao redefinir a senha. Tente novamente.', 'danger')
        else:
            flash('Senha inválida ou informações ausentes.', 'danger')
    return render_template("RecuperarSenha/redefinir_senha.html", email=email)

if __name__ == '__main__':
    # Garante que o diretório de uploads existe ao rodar localmente
    os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE), exist_ok=True)
    app.run(debug=True)
