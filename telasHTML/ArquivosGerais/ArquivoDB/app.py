import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image, update_user_profile, get_user_by_id, update_password
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# O BASE_DIR agora aponta para a pasta 'telasHTML' (dois níveis acima, assumindo app.py está em .../ArquivosGerais/ArquivoDB/)
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..')) 

app = Flask(
    __name__,
    # A pasta 'telasHTML' é o template_folder
    template_folder=BASE_DIR
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")

# Diretório para uploads de fotos de perfil (relativo a 'telasHTML')
UPLOAD_FOLDER_RELATIVE = 'ArquivosGerais/TelaDeUsuario/imagens/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

# ====================================================================
# === DECORADOR DE AUTENTICAÇÃO ===
# ====================================================================

def login_required(f):
    """
    Decorador para proteger rotas. Redireciona para o login se o usuário não estiver na sessão.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ====================================================================
# === ROTAS PARA SERVIR ARQUIVOS ESTÁTICOS (ASSETS) ===
# ====================================================================
# OBSERVAÇÃO: Todos os caminhos agora são relativos a 'telasHTML'

@app.route('/login-assets/<path:filename>')
def login_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'LoginECadastro/login-assets'), filename)

@app.route('/cadastro-assets/<path:filename>')
def cadastro_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'LoginECadastro/cadastro-assets'), filename)

@app.route('/loading-assets/<path:filename>')
def loading_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'ArquivosGerais/Loading'), filename)

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'ArquivosGerais'), filename)

@app.route('/inicio-assets/<path:filename>')
def inicio_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'ArquivosGerais/TelaInicial/assets'), filename)

@app.route('/feed-assets/<path:filename>')
def feed_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'ArquivosGerais/TelaFeed'), filename)

@app.route('/user-assets/<path:filename>')
def user_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'ArquivosGerais/TelaDeUsuario'), filename)

@app.route('/static-user-files/<path:filename>')
def serve_static_files(filename):
    asset_dir = os.path.join(BASE_DIR, 'ArquivosGerais/TelaDeUsuario')
    return send_from_directory(asset_dir, filename)

@app.route('/recuperar-senha-assets/<path:filename>')
def serve_recuperar_senha_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'RecuperarSenha'), filename)

# ====================================================================
# === ROTAS PRINCIPAIS ===
# ====================================================================

@app.route("/", methods=['GET'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('pagina_inicial'))

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = check_user(email, senha)
        
        if user:
            session['user_email'] = email
            flash(f"Bem-vindo(a), {user['nome']}!", 'success')
            return redirect(url_for('loading_page', next_page='inicio', message_category='success'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/LoginECadastro/telaLogin.html")


@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cidade = request.form['cidade']
        posicao = request.form['posicao']
        nascimento = request.form['nascimento']
        numero = request.form['numero']
        
        try:
            if '/' in nascimento:
                day, month, year = map(int, nascimento.split('/'))
                nascimento = f"{year:04d}-{month:02d}-{day:02d}"
            datetime.strptime(nascimento, '%Y-%m-%d')
        except ValueError:
            flash("Formato de data de nascimento inválido. Use AAAA-MM-DD ou DD/MM/AAAA.", 'danger')
            return redirect(url_for('cadastro'))

        success, message = register_user(nome, email, senha, cidade, posicao, nascimento, numero)

        if success:
            # Correção de login automático
            session['user_email'] = email
            flash(message, 'success')
            return redirect(url_for('loading_page', next_page='inicio', message_category='success')) 
        else:
            flash(message, 'danger')
            return redirect(url_for('cadastro'))

    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/LoginECadastro/cadastrar.html")


@app.route("/logout")
def logout():
    session.pop('user_email', None)
    flash('Você foi desconectado(a).', 'success')
    return redirect(url_for('login'))


@app.route("/loading/<next_page>")
def loading_page(next_page):
    message_category = request.args.get('message_category', 'info')
    
    if next_page == 'inicio' and 'user_email' not in session:
        return redirect(url_for('login'))
        
    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/Loading/loading.html", next_page=next_page, message_category=message_category)


@app.route("/inicio")
@login_required
def pagina_inicial():
    users = get_all_users()
    
    user_email = session.get('user_email')
    logged_user = get_user_by_email(user_email)
    
    if logged_user is None:
        return redirect(url_for('logout'))

    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/TelaInicial/TelaInicial.html", users=users, logged_user=logged_user)


@app.route("/perfil/<int:user_id>")
@login_required
def pagina_usuario(user_id=None):
    user_email = session.get('user_email')
    current_user = get_user_by_email(user_email)
    
    if user_id is None or user_id == current_user['id']:
        usuario = current_user
        is_owner = True
    else:
        usuario = get_user_by_id(user_id)
        is_owner = False
    
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/TelaDeUsuario/TelaUser.html", usuario=usuario, is_owner=is_owner)


@app.route("/feed")
@login_required
def pagina_feed():
    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/TelaFeed/feed.html")


# ====================================================================
# === ROTAS DE RECUPERAÇÃO DE SENHA (PLACEHOLDERS) ===
# ====================================================================

@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        
        flash(f'Se o e-mail {email} estiver cadastrado, um link de redefinição de senha foi enviado.', 'success')
        return redirect(url_for('login'))
        
    # O diretório 'RecuperarSenha' não está dentro de 'ArquivosGerais', então o caminho fica:
    return render_template("RecuperarSenha/esqueci_senha.html")


@app.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        email = request.args.get('email') 
        
        if email and nova_senha and len(nova_senha) >= 6:
            if update_password(email, nova_senha):
                flash('Sua senha foi redefinida com sucesso. Faça o login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Falha ao redefinir a senha. Tente novamente.', 'danger')
        else:
            flash('Senha inválida ou falta de informações.', 'danger')
        
        # O diretório 'RecuperarSenha' não está dentro de 'ArquivosGerais', então o caminho fica:
        return render_template("RecuperarSenha/redefinir_senha.html")

    # O diretório 'RecuperarSenha' não está dentro de 'ArquivosGerais', então o caminho fica:
    return render_template("RecuperarSenha/redefinir_senha.html")

# ====================================================================
# === ROTAS DE EDIÇÃO DE PERFIL E UPLOAD ===
# ====================================================================

@app.route("/editar_perfil", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    user_email = session.get('user_email')
    usuario = get_user_by_email(user_email)
    
    if not usuario:
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        # 1. Tratar Upload de Imagem de Perfil
        if 'foto_perfil' in request.files:
            file = request.files['foto_perfil']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{usuario['id']}_profile_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[-1]}")
                
                save_path = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE, filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                
                relative_path = f"imagens/profile_pics/{filename}"
                if update_user_profile_image(user_email, relative_path):
                    flash('Foto de perfil atualizada com sucesso!', 'success')
                else:
                    flash('Erro ao salvar o caminho da foto no banco de dados.', 'danger')

        # 2. Tratar Dados do Formulário (Update de Texto)
        update_data = {}
        updatable_fields = ['nome', 'cidade', 'posicao', 'nascimento', 'numero'] 
        
        for field in updatable_fields:
            if field in request.form and request.form[field] != usuario.get(field):
                update_data[field] = request.form[field]

        if update_data:
            if update_user_profile(user_email, **update_data):
                flash('Informações de perfil atualizadas com sucesso!', 'success')
            else:
                flash('Erro ao atualizar informações de perfil no banco de dados.', 'danger')
        
        return redirect(url_for('editar_perfil'))

    usuario = get_user_by_email(user_email)
    
    # CORREÇÃO CRÍTICA: Adicionado 'ArquivosGerais/'
    return render_template("ArquivosGerais/TelaDeUsuario/editar_perfil.html", usuario=usuario)


# ====================================================================
# === API ENDPOINTS (DADOS PARA TELAS) ===
# ====================================================================

@app.route("/api/posts", methods=['GET'])
@login_required
def api_posts():
    # Esta função deve retornar dados reais de posts do seu Supabase.
    mock_posts = [
        {
            "id": 1, 
            "author_id": 101, 
            "author_name": "Gabriel Diniz", 
            "author_avatar": url_for('user_assets', filename='imagens/user-icon-placeholder.png'),
            "content": "Grande vitória hoje! O time jogou demais. #futebol #vitoria",
            "image_url": None,
            "likes": 5, 
            "comments": 2,
            "timestamp": "2 minutos atrás"
        },
        {
            "id": 2, 
            "author_id": 102, 
            "author_name": "Maria Silva", 
            "author_avatar": url_for('user_assets', filename='imagens/user-icon-placeholder.png'),
            "content": "Novo uniforme para a próxima temporada! O que acharam?",
            "image_url": url_for('user_assets', filename='imagens/WallpaperTest.jpg'), 
            "likes": 12, 
            "comments": 5,
            "timestamp": "1 hora atrás"
        }
    ]
    return jsonify(mock_posts)

if __name__ == '__main__':
    os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE), exist_ok=True)
    app.run(debug=True, port=8000)