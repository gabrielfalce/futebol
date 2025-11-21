import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import (
    register_user, check_user, get_all_users, get_user_by_email,
    update_user_profile_image, update_user_profile, get_user_by_id, update_password,
    create_post, get_posts_by_user, get_all_posts, get_post_by_id, supabase
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

# Buckets do Supabase
PROFILE_BUCKET = 'profile_images'
POST_BUCKET = 'post-images'

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

@app.route('/serve_static_files/<path:filename>')
def serve_static_files(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML')
    return send_from_directory(dir_path, filename)

@app.route('/post-images/<path:filename>')
def post_images(filename):
    dir_path = os.path.join(BASE_DIR, POST_UPLOAD_FOLDER_RELATIVE)
    return send_from_directory(dir_path, filename)

# === ROTAS PRINCIPAIS ===
@app.route('/')
def login():
    return render_template('telasHTML/ArquivosGerais/telaDeLogin/telaLogin.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        user = check_user(email, senha)
        if user:
            session['user_email'] = user['email']
            session['user_id'] = user['id']
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Credenciais inválidas.', 'danger')
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # CORREÇÃO: Extrair todos os campos do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        nascimento = request.form.get('nascimento')
        numero_camisa = request.form.get('numero_camisa')
        numero_telefone = request.form.get('numero_telefone')
        
        # CORREÇÃO: Chamar register_user com todos os argumentos
        success, message = register_user(
            nome, email, senha, cidade, posicao, nascimento, numero_camisa, numero_telefone
        )
        
        if success:
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            # CORREÇÃO: Tratar a mensagem de erro e repassar os dados do formulário
            flash(message, 'danger')
            return render_template(
                'telasHTML/ArquivosGerais/Cadastrar_templates/cadastrar.html',
                form_data=request.form
            )
    
    # CORREÇÃO: Garante que 'form_data' seja passado em requisições GET
    return render_template(
        'telasHTML/ArquivosGerais/Cadastrar_templates/cadastrar.html',
        form_data={}
    )

@app.route('/loading/pagina_inicial')
def loading():
    return render_template('telasHTML/ArquivosGerais/TelaLoading/Telaloading.html')

@app.route('/inicio')
@login_required
def pagina_inicial():
    users = get_all_users()
    return render_template('telasHTML/ArquivosGerais/TelaInicial/TelaInicial.html', users=users)

# ROTA DE PERFIL - CORRIGIDA
@app.route('/perfil/<int:user_id>')
@login_required
def pagina_usuario(user_id):
    user = get_user_by_id(user_id)
    # Variável is_owner é crucial para o TelaUser.html
    is_owner = session.get('user_id') == user_id
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))
    posts = get_posts_by_user(user_id)
    return render_template(
        'telasHTML/ArquivosGerais/TelaDeUsuario/TelaUser.html', 
        usuario=user, # CORRIGIDO: Nome da variável para corresponder ao HTML
        publicacoes=posts, # CORRIGIDO: Nome da variável para corresponder ao HTML
        is_owner=is_owner # Variável crucial para exibir botões de edição
    )


@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    user_id = session['user_id']
    if request.method == 'POST':
        nome = request.form.get('nome')
        bio = request.form.get('bio')
        profile_image = request.files.get('profile_image')

        profile_image_url = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            bucket_path = f"users/{user_id}/{filename}"
            try:
                supabase.storage.from_(PROFILE_BUCKET).upload(
                    bucket_path,
                    profile_image.read(),
                    file_options={"content-type": profile_image.content_type}
                )
                public_url = supabase.storage.from_(PROFILE_BUCKET).get_public_url(bucket_path)
                profile_image_url = public_url
            except Exception as e:
                flash('Erro ao fazer upload da imagem.', 'danger')
                print(e)

        success = update_user_profile(user_id, nome, bio, profile_image_url)
        if success:
            flash('Perfil atualizado com sucesso!', 'success')
        else:
            flash('Erro ao atualizar perfil.', 'danger')
        
        return redirect(url_for('pagina_usuario', user_id=user_id))

    user = get_user_by_id(user_id)
    return render_template('telasHTML/ArquivosGerais/TelaDeUsuario/editar_perfil.html', user=user)

@app.route('/feed')
@login_required
def pagina_feed():
    # O feed.html carrega o conteúdo via AJAX na rota /api/posts
    return render_template("telasHTML/ArquivosGerais/TelaFeed/feed.html")

@app.route('/api/posts', methods=['GET', 'POST'])
@login_required
def api_posts():
    if request.method == 'POST':
        legenda = request.form.get('legenda', '')
        autor_id = session['user_id']
        imagem_url = None

        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename != '' and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    bucket_path = f"users/{autor_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    supabase.storage.from_(POST_BUCKET).upload(
                        bucket_path,
                        file.read(),
                        file_options={"content-type": file.content_type}
                    )
                    public_url = supabase.storage.from_(POST_BUCKET).get_public_url(bucket_path)
                    imagem_url = public_url
                except Exception as e:
                    print(f"ERRO no upload do post: {e}")
                    return jsonify({'success': False, 'error': 'Falha no upload da imagem.'}), 500

        success, result = create_post(autor_id, legenda, imagem_url)
        
        if success:
            post_id = result
            new_post_data = get_post_by_id(post_id)
            if new_post_data:
                return jsonify({'success': True, 'post': new_post_data}), 201
            else:
                return jsonify({'success': False, 'error': 'Post criado, mas não pôde ser recuperado.'}), 500
        else:
            return jsonify({'success': False, 'error': result}), 500

    elif request.method == 'GET':
        posts = get_all_posts()
        return jsonify(posts)

# ROTA DO CHAT
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

    return render_template(
        "telasHTML/ArquivosGerais/TelaChat/chat.html",
        remetente=remetente,
        destinatario=destinatario,
        SUPABASE_URL=os.environ.get("SUPABASE_URL"),
        SUPABASE_ANON_KEY=os.environ.get("SUPABASE_ANON_KEY")
    )

# NOVA ROTA API CHAT - PARA CARREGAMENTO DE HISTÓRICO VIA JS (REINTRODUZIDA)
@app.route("/api/chat/historico/<int:destinatario_id>")
@login_required
def api_chat_historico(destinatario_id):
    remetente_id = session.get('user_id')
    
    if not remetente_id:
        return jsonify({'success': False, 'error': 'Usuário não autenticado.'}), 401

    # Ordena os IDs para garantir a chave de conversa consistente
    id1 = min(remetente_id, destinatario_id)
    id2 = max(remetente_id, destinatario_id)
    
    try:
        # Consulta mensagens onde (remetente=id1 E destinatário=id2) OU (remetente=id2 E destinatário=id1)
        # CORREÇÃO: Envolver a expressão em parênteses externos para forçar a continuação de linha e evitar SyntaxError
        response = (
            supabase.from_('mensagens').select('*').or_(
                f'and(remetente_id.eq.{id1},destinatario_id.eq.{id2}),and(remetente_id.eq.{id2},destinatario_id.eq.{id1})'
            ).order('created_at', asc=True).execute()
        )
        
        data = response.data
        if not data:
            return jsonify([]), 200
            
        return jsonify(data), 200

    except Exception as e:
        print(f"Erro ao buscar histórico de chat: {e}")
        return jsonify({'success': False, 'error': f'Falha no servidor ao carregar histórico: {str(e)}'}), 500


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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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