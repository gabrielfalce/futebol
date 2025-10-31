# <DOCUMENT filename="app.py">
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import (
    register_user, check_user, get_all_users, get_user_by_email,
    update_user_profile_image, update_user_profile, get_user_by_id, update_password,
    create_post, get_posts_by_user, get_all_posts  # NOVAS IMPORTAÇÕES
)
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..', '..')) 

app = Flask(
    __name__,
    template_folder=BASE_DIR
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")

# Diretório para uploads de fotos de perfil
UPLOAD_FOLDER_RELATIVE = 'telasHTML/ArquivosGerais/TelaDeUsuario/imagens/profile_pics'
# Diretório para uploads de imagens de posts
POST_UPLOAD_FOLDER_RELATIVE = 'telasHTML/ArquivosGerais/TelaFeed/imagens/post_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

# Decorador para exigir login
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
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'telaDeLogin')
    return send_from_directory(dir_path, filename)

@app.route('/loading-assets/<path:filename>')
def loading_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaLoading')
    return send_from_directory(dir_path, filename)

@app.route('/cadastro-assets/<path:filename>')
def cadastro_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'Cadastrar_templates')
    return send_from_directory(dir_path, filename)

@app.route('/inicio-assets/<path:filename>')
def inicio_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaInicial')
    return send_from_directory(dir_path, filename)

@app.route('/user-assets/<path:filename>')
def user_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaDeUsuario')
    return send_from_directory(dir_path, filename)
    
@app.route('/feed-assets/<path:filename>')
def feed_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaFeed')
    return send_from_directory(dir_path, filename)

@app.route('/chat-assets/<path:filename>')
def chat_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaChat')
    return send_from_directory(dir_path, filename)

@app.route('/recuperar-senha-assets/<path:filename>')
def recuperar_senha_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'RecuperarSenha')
    return send_from_directory(dir_path, filename)

# Rota genérica para servir arquivos estáticos de dentro do diretório 'telasHTML'
@app.route('/serve_static_files/<path:filename>')
def serve_static_files(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML')
    return send_from_directory(dir_path, filename)

# ROTA PARA SERVIR IMAGENS DE POSTS
@app.route('/post-assets/<path:filename>')
def post_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaFeed', 'imagens', 'post_pics')
    return send_from_directory(dir_path, filename)


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
            return render_template("telasHTML/ArquivosGerais/telaDeLogin/telaLogin.html", email=email)
            
    return render_template("telasHTML/ArquivosGerais/telaDeLogin/telaLogin.html")


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
            
            numero_telefone = request.form.get('numero_telefone')
            numero_camisa = request.form.get('numero_camisa')

            try:
                nascimento_formatado = datetime.strptime(nascimento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                nascimento_formatado = nascimento_str
        
            success, message = register_user(nome, email, senha, cidade, posicao, nascimento_formatado, numero_camisa, numero_telefone)
            
            if success:
                user_data = check_user(email, senha)
                if user_data:
                    session['user_email'] = email
                    session['user_id'] = user_data.get('id')
                    session['user_name'] = user_data.get('nome')
                    flash(message, 'success')
                    return redirect(url_for('tela_loading', next_page='pagina_inicial', message_category='success'))
                else:
                    flash('Cadastro realizado, mas falha no login automático. Faça o login.', 'warning')
                    return redirect(url_for('tela_loading', next_page='login', message_category='warning'))
            else:
                flash(message, 'danger')
                return redirect(url_for('cadastro'))

        except ValueError:
            flash('Formato de data de nascimento inválido. Use DD/MM/AAAA.', 'danger')
            return redirect(url_for('cadastro'))
        
        except Exception as e:
            print(f"ERRO geral no cadastro: {e}")
            flash('Ocorreu um erro inesperado ao tentar cadastrar o usuário.', 'danger')
            return redirect(url_for('cadastro'))

    return render_template("telasHTML/ArquivosGerais/Cadastrar_templates/cadastrar.html")


@app.route("/loading/<next_page>")
def tela_loading(next_page):
    message_category = request.args.get('message_category', 'success')
    message = request.args.get('message')
    
    if message:
        flash(message, message_category)

    next_url = url_for(next_page)
    
    return render_template("telasHTML/ArquivosGerais/TelaLoading/Telaloading.html", 
                           next_url=next_url, 
                           tempo_loading=2500)


@app.route("/logout")
@login_required
def logout():
    session.pop('user_email', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('login'))


@app.route("/inicio")
@login_required
def pagina_inicial():
    users = get_all_users()
    current_user_email = session.get('user_email')
    users = [user for user in users if user.get('email') != current_user_email]
    
    return render_template("telasHTML/ArquivosGerais/TelaInicial/TelaInicial.html", users=users)


@app.route("/perfil/<int:user_id>")
@login_required
def pagina_usuario(user_id=None):
    if user_id is None or user_id == session.get('user_id'):
        user_email = session.get('user_email')
        usuario = get_user_by_email(user_email)
        is_owner = True
    else:
        usuario = get_user_by_id(user_id)
        is_owner = False
        
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    # BUSCA AS PUBLICAÇÕES DO USUÁRIO
    publicacoes = get_posts_by_user(usuario['id']) if usuario else []

    return render_template("telasHTML/ArquivosGerais/TelaDeUsuario/TelaUser.html", 
                           usuario=usuario, 
                           is_owner=is_owner,
                           publicacoes=publicacoes)  # PASSA AS PUBLICAÇÕES


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
        
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        numero = request.form.get('numero')
        
        if nome:
            update_data['nome'] = nome
        if cidade:
            update_data['cidade'] = cidade
        if posicao:
            update_data['posicao'] = posicao
        if numero:
            update_data['numero_camisa'] = numero
            
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                full_upload_dir = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
                os.makedirs(full_upload_dir, exist_ok=True)
                file_path = os.path.join(full_upload_dir, filename)
                file.save(file_path)
                db_path = os.path.join(UPLOAD_FOLDER_RELATIVE, filename).replace('\\', '/')
                update_data['profile_image_url'] = db_path
                session['user_profile_image'] = db_path

        if update_data:
            success = update_user_profile(user_email, **update_data)
            if success:
                flash('Perfil atualizado com sucesso!', 'success')
            else:
                flash('Falha ao atualizar o perfil.', 'danger')
        else:
             flash('Nenhuma alteração detectada.', 'info')
             
        return redirect(url_for('editar_perfil'))

    return render_template("telasHTML/ArquivosGerais/TelaDeUsuario/editar_perfil.html", usuario=usuario)


@app.route("/feed")
@login_required
def pagina_feed():
    posts = get_all_posts()
    return render_template("telasHTML/ArquivosGerais/TelaFeed/feed.html", posts=posts)


# API PARA POSTS (CRIAR + LISTAR)
@app.route("/api/posts", methods=['GET', 'POST'])
@login_required
def api_posts():
    if request.method == 'POST':
        try:
            legenda = request.form.get('legenda', '').strip()
            if not legenda:
                return jsonify({'success': False, 'error': 'Legenda é obrigatória.'}), 400

            autor_id = session.get('user_id')
            imagem_url = None

            if 'postImage' in request.files:
                file = request.files['postImage']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    full_upload_dir = os.path.join(BASE_DIR, POST_UPLOAD_FOLDER_RELATIVE)
                    os.makedirs(full_upload_dir, exist_ok=True)
                    file_path = os.path.join(full_upload_dir, filename)
                    file.save(file_path)
                    imagem_url = os.path.join(POST_UPLOAD_FOLDER_RELATIVE, filename).replace('\\', '/')

            success, result = create_post(autor_id, legenda, imagem_url)
            if success:
                return jsonify({'success': True, 'post_id': result}), 201
            else:
                return jsonify({'success': False, 'error': result}), 500
        except Exception as e:
            print(f"ERRO ao criar post: {e}")
            return jsonify({'success': False, 'error': 'Erro interno do servidor.'}), 500

    elif request.method == 'GET':
        posts = get_all_posts()
        return jsonify(posts)


@app.route("/chat/<int:destinatario_id>")
@login_required
def chat_with_user(destinatario_id):
    remetente_id = session.get('user_id')
    
    if remetente_id == destinatario_id:
        flash('Você não pode conversar consigo mesmo.', 'danger')
        return redirect(url_for('pagina_inicial'))

    remetente = get_user_by_id(remetente_id)
    destinatario = get_user_by_id(destinatario_id)
    
    if not remetente or not destinatario:
        flash('Usuário para chat não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_KEY")

    return render_template("telasHTML/ArquivosGerais/TelaChat/chat.html", 
                           remetente=remetente, 
                           destinatario=destinatario,
                           supabase_url=supabase_url,
                           supabase_anon_key=supabase_anon_key)


@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        flash(f'Se o e-mail {email} estiver cadastrado, um link de redefinição de senha foi enviado.', 'success')
        return redirect(url_for('login'))
        
    return render_template("telasHTML/RecuperarSenha/esqueci_senha.html")


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

    return render_template("telasHTML/RecuperarSenha/redefinir_senha.html")


# FILTRO JINJA: FORMATA DATA NO TEMPLATE
@app.template_filter('strftime')
def _jinja2_filter_strftime(date_str, fmt='%d/%m/%Y às %H:%M'):
    if not date_str:
        return ''
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(fmt)
    except:
        return date_str


if __name__ == '__main__':
    os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, POST_UPLOAD_FOLDER_RELATIVE), exist_ok=True)
    app.run(debug=True)