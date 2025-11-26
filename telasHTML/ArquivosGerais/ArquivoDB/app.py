import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import (
    register_user, check_user, get_all_users, get_user_by_email,
    update_user_profile_image, update_user_profile, get_user_by_id, update_password,
    create_post, get_posts_by_user, get_all_posts, get_post_by_id, supabase,
    create_message,
    get_chat_history
)
import bcrypt
from datetime import datetime, timedelta   
from werkzeug.utils import secure_filename
from functools import wraps
import uuid

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Definir template_folder para a pasta 'telasHTML' (dois níveis acima).
# Se app.py está em /telasHTML/ArquivosGerais/ArquivoDB, o TEMPLATE_FOLDER será /telasHTML
TEMPLATE_FOLDER = os.path.abspath(os.path.join(APP_DIR, '..', '..'))

# Para uploads, o caminho para o projeto raiz
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..', '..'))

app = Flask(
    __name__,
    template_folder=TEMPLATE_FOLDER
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")

# Diretório para uploads de fotos de perfil
UPLOAD_FOLDER_RELATIVE = 'telasHTML/ArquivosGerais/TelaDeUsuario/imagens/profile_pics'
# Diretório para uploads de imagens de posts
POST_UPLOAD_FOLDER_RELATIVE = 'telasHTML/ArquivosGerais/TelaFeed/imagens/post_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# === FUNÇÕES AUXILIARES ===

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator de verificação de login que também valida o usuário no banco."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se há user_id na sessão
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login', next=request.path))
        # Valida existência do usuário no banco
        try:
            user = get_user_by_id(session.get('user_id'))
            if not user:
                # sessão inválida — limpa e força novo login
                session.clear()
                flash('Sessão inválida. Faça login novamente.', 'danger')
                return redirect(url_for('login', next=request.path))
        except Exception:
            # Em caso de erro ao acessar o banco, trate como sessão inválida
            session.clear()
            flash('Erro ao validar sessão. Faça login novamente.', 'danger')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('strftime')
def _jinja2_filter_strftime(date_str, fmt='%d/%m/%Y às %H:%M'):
    """Filtro Jinja para formatar datas (formato ISO do Supabase)."""
    if not date_str:
        return ''
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(fmt)
    except ValueError:
        return 'Data Inválida'

# === ROTAS DE ASSETS (CSS/JS/IMAGENS) ===
# Usar caminhos absolutos baseados em TEMPLATE_FOLDER para evitar 404s por working directory.

@app.route('/static/login/<path:filename>')
def login_assets(filename):
    # corrigido: arquivo de login está em TEMPLATE_FOLDER/ArquivosGerais/telaDeLogin
    directory = os.path.join(TEMPLATE_FOLDER, 'ArquivosGerais', 'telaDeLogin')
    return send_from_directory(directory, filename)

@app.route('/static/cadastro/<path:filename>')
def cadastro_assets(filename):
    # apontar para ArquivosGerais/Cadastrar_templates (caminho real)
    directory = os.path.join(TEMPLATE_FOLDER, 'ArquivosGerais', 'Cadastrar_templates')
    return send_from_directory(directory, filename)
    
@app.route('/static/chat/<path:filename>')
def chat_assets(filename):
    directory = os.path.join(TEMPLATE_FOLDER, 'ArquivosGerais', 'TelaChat')
    return send_from_directory(directory, filename)

@app.route('/static/user_assets/<path:filename>')
def user_assets(filename):
    # Esta rota serve arquivos que estão diretamente em ArquivosGerais
    # ou em subpastas de ArquivosGerais (como TelaDeUsuario, TelaInicial, etc.)
    directory = os.path.join(TEMPLATE_FOLDER, 'ArquivosGerais')
    return send_from_directory(directory, filename)

@app.route('/static/inicio/<path:filename>')
def inicio_assets(filename):
    directory = os.path.join(TEMPLATE_FOLDER, 'ArquivosGerais', 'TelaInicial')
    return send_from_directory(directory, filename)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Rota para servir imagens de perfil."""
    # BASE_DIR é o diretório raiz do projeto no Render
    upload_path = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
    return send_from_directory(upload_path, filename)

@app.route('/post_uploads/<path:filename>')
def post_uploaded_file(filename):
    """Rota para servir imagens de posts."""
    post_upload_path = os.path.join(BASE_DIR, POST_UPLOAD_FOLDER_RELATIVE)
    return send_from_directory(post_upload_path, filename)

# === ROTAS DE AUTENTICAÇÃO E PERFIL ===

@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('pagina_inicial'))
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    # preserva o next vindo da query string (se houver)
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        remember = request.form.get('remember')  # checkbox: 'on' quando marcado
        user = check_user(email, senha)

        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_nome'] = user['nome']
            # lembrar-me: torna a sessão permanente
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            flash(f'Bem-vindo, {user["nome"]}!', 'success')
            # redireciona para next se existir, senão para pagina_inicial
            if next_url:
                return redirect(next_url)
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
            return render_template("ArquivosGerais/telaDeLogin/telaLogin.html", email=email, next=next_url)
    # GET: renderiza a página de login (passando next para o template)
    return render_template("ArquivosGerais/telaDeLogin/telaLogin.html", next=next_url)

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    form_data = request.form
    if request.method == 'POST':
        nome = form_data.get('nome')
        email = form_data.get('email')
        senha = form_data.get('senha')
        cidade = form_data.get('cidade')
        posicao = form_data.get('posicao')
        nascimento = form_data.get('nascimento')
        numero_camisa = form_data.get('numero_camisa')
        numero_telefone = form_data.get('numero_telefone')

        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
        else:
            # CORREÇÃO CRÍTICA: A função register_user retorna 2 valores, não 3.
            # O código original (com o if False else) foi removido por ser redundante e a atribuição corrigida.
            success, message = register_user(nome, email, senha, cidade, posicao, nascimento, numero_camisa, numero_telefone)
            
            if success:
                flash(message, 'success')
                # alteração mínima: ao criar conta, autenticar automaticamente e redirecionar para pagina_inicial
                # obter o usuário criado para popular sessão (tenta buscar pelo email)
                try:
                    new_user = get_user_by_email(email)
                    if new_user:
                        session['user_id'] = new_user.get('id')
                        session['user_email'] = new_user.get('email')
                        session['user_nome'] = new_user.get('nome')
                        session.permanent = True  # opcionais: definir como permanente para "lembrar-me" padrão
                except Exception:
                    # se falhar ao buscar, simplesmente redireciona para login (com flash já aplicado)
                    return redirect(url_for('login'))
                return redirect(url_for('pagina_inicial'))
            else:
                flash(message, 'danger')

    # caminho corrigido para o template real
    return render_template("ArquivosGerais/Cadastrar_templates/cadastrar.html", form_data=form_data)

# ================== ESQUECI SENHA (mostra link na tela) ==================
@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Digite um e-mail válido.', 'danger')
            return redirect(url_for('esqueci_senha'))

        resposta = supabase.table('usuarios').select('email').eq('email', email).execute()
        if not resposta.data:
            flash('Se o e-mail estiver cadastrado, o link foi gerado.', 'info')
            return redirect(url_for('login'))

        # Gera token
        import random
        import string
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
        expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        supabase.table('password_resets').upsert({
            'email': email,
            'token': token,
            'expires_at': expires,
            'used': False
        }, on_conflict='email').execute()

        reset_link = f"https://futebol-1.onrender.com/redefinir_senha/{token}"
        flash(f'Link gerado! Copie:\n{reset_link}', 'success')
        return redirect(url_for('login'))

    return render_template('ArquivosGerais/RecuperarSenha/esqueci_senha.html')

# ================== REDEFINIR SENHA COM TOKEN ==================
@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    # GET → mostra a tela
    if request.method == 'GET':
        # Verifica se o token existe e ainda é válido
        resp = supabase.table('password_resets')\
            .select('email', 'expires_at', 'used')\
            .eq('token', token).single().execute()

        if not resp.data:
            flash('Link inválido.', 'danger')
            return redirect(url_for('login'))

        dados = resp.data
        expires_at = datetime.fromisoformat(dados['expires_at'].replace('Z', '+00:00'))

        if dados['used'] or datetime.utcnow() > expires_at:
            flash('Este link expirou ou já foi usado.', 'danger')
            return redirect(url_for('login'))

        # Tudo ok → mostra a tela com o token na URL
        return render_template(
            'ArquivosGerais/RecuperarSenha/redefinir_senha.html',
            token=token  # opcional, mas deixa caso queira usar no JS depois
        )

    # POST → salva a nova senha
    nova_senha = request.form.get('nova_senha')

    if not nova_senha or len(nova_senha) < 6:
        flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
        return redirect(url_for('redefinir_senha', token=token))

    # Busca o token
    resp = supabase.table('password_resets')\
        .select('email', 'expires_at', 'used')\
        .eq('token', token).single().execute()

    if not resp.data:
        flash('Token inválido.', 'danger')
        return redirect(url_for('login'))

    dados = resp.data
    expires_at = datetime.fromisoformat(dados['expires_at'].replace('Z', '+00:00'))

    if dados['used'] or datetime.utcnow() > expires_at:
        flash('Este link já expirou ou foi usado.', 'danger')
        return redirect(url_for('login'))

    # Tudo certo → atualiza a senha
    hashed = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    supabase.table('usuarios')\
        .update({'senha': hashed})\
        .eq('email', dados['email'])\
        .execute()

    # Marca o token como usado
    supabase.table('password_resets')\
        .update({'used': True})\
        .eq('token', token)\
        .execute()

    flash('Senha alterada com sucesso! Agora você pode fazer login com a nova senha.', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))


# === ROTAS DA APLICAÇÃO ===

@app.route("/pagina_inicial")
@login_required
def pagina_inicial():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)

    posts = get_all_posts()
    users = get_all_users()

    return render_template("ArquivosGerais/TelaInicial/TelaInicial.html", user=user, posts=posts, users=users)


@app.route('/feed')
@login_required
def feed():
    posts = get_all_posts()  # Use sua função do database.py
    user = get_user_by_id(session['user_id'])
    return render_template("ArquivosGerais/TelaFeed/feed.html", posts=posts, user=user)

@app.route("/perfil/<int:user_id>")
@login_required
def perfil(user_id):
    user_data = get_user_by_id(user_id)
    posts = get_posts_by_user(user_id) 
    
    if not user_data:
        flash("Usuário não encontrado.", 'danger')
        return redirect(url_for('pagina_inicial'))
        
    is_current_user = user_id == session.get('user_id')
    
    return render_template(
        "ArquivosGerais/TelaDeUsuario/TelaUser.html", 
        user=user_data, 
        is_current_user=is_current_user,
        posts=posts
    )

@app.route("/upload_profile_image", methods=['POST'])
@login_required
def upload_profile_image():
    user_id = session.get('user_id')
    user_email = session.get('user_email')
    
    if 'profile_image' not in request.files:
        flash('Nenhum arquivo enviado.', 'danger')
        return redirect(url_for('perfil', user_id=user_id))
    
    file = request.files['profile_image']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('perfil', user_id=user_id))

    if file and allowed_file(file.filename):
        # 1. Salvar o arquivo localmente
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        
        # Caminho absoluto para salvar o arquivo
        upload_folder_abs = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
        os.makedirs(upload_folder_abs, exist_ok=True)
        file_path = os.path.join(upload_folder_abs, filename)
        file.save(file_path)
        
        # 2. Atualizar o caminho no banco de dados
        # O caminho salvo no banco é o caminho da rota do Flask para servir o arquivo
        profile_image_url_path = url_for('uploaded_file', filename=filename)
        
        if update_user_profile_image(user_email, profile_image_url_path):
            flash('Foto de perfil atualizada com sucesso!', 'success')
        else:
            flash('Falha ao atualizar o banco de dados.', 'danger')
            
    else:
        flash('Tipo de arquivo não permitido.', 'danger')
        
    return redirect(url_for('perfil', user_id=user_id))

@app.route("/editar_perfil", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        bio = request.form.get('bio')
        
        # Lógica de upload de imagem (se houver)
        profile_image_url = None
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '' and allowed_file(file.filename):
                # 1. Salvar o arquivo localmente
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                upload_folder_abs = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
                os.makedirs(upload_folder_abs, exist_ok=True)
                file_path = os.path.join(upload_folder_abs, filename)
                file.save(file_path)
                
                # 2. Definir o caminho para o banco de dados
                profile_image_url = url_for('uploaded_file', filename=filename)
        
        if update_user_profile(user_id, nome, bio, profile_image_url):
            # Atualiza o nome na sessão se ele foi alterado
            if nome:
                session['user_nome'] = nome
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('perfil', user_id=user_id))
        else:
            flash('Falha ao atualizar o perfil.', 'danger')
            
    # GET
    return render_template("ArquivosGerais/TelaDeUsuario/editar_perfil.html", user=user)

@app.route("/criar_post", methods=['POST'])
@login_required
def criar_post():
    user_id = session.get('user_id')
    legenda = request.form.get('legenda')
    
    if not legenda and 'post_image' not in request.files:
        flash('O post deve ter uma legenda ou uma imagem.', 'danger')
        return redirect(url_for('pagina_inicial'))
        
    imagem_url = None
    if 'post_image' in request.files:
        file = request.files['post_image']
        if file.filename != '' and allowed_file(file.filename):
            # 1. Salvar o arquivo localmente
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            post_upload_folder_abs = os.path.join(BASE_DIR, POST_UPLOAD_FOLDER_RELATIVE)
            os.makedirs(post_upload_folder_abs, exist_ok=True)
            file_path = os.path.join(post_upload_folder_abs, filename)
            file.save(file_path)
            
            # 2. Definir o caminho para o banco de dados
            imagem_url = url_for('post_uploaded_file', filename=filename)
            
    success, message_or_id = create_post(user_id, legenda, imagem_url)
    
    if success:
        flash('Post criado com sucesso!', 'success')
    else:
        flash(f'Falha ao criar post: {message_or_id}', 'danger')
        
    return redirect(url_for('pagina_inicial'))


@app.route('/api/posts', methods=['GET'])
@login_required
def api_posts():
    posts = get_all_posts()
    return jsonify(posts)

# === ROTAS DE CHAT ===

@app.route("/send_message/historico/<int:destinatario_id>")
@login_required
def chat_historico(destinatario_id):
    remetente_id = session.get("user_id")
    historico = get_chat_history(remetente_id, destinatario_id)
    return jsonify(historico)


@app.route("/api/chat/historico/<int:destinatario_id>")
@login_required
def api_chat_historico(destinatario_id):
    remetente_id = session.get('user_id')
    historico = get_chat_history(remetente_id, destinatario_id)

    return jsonify(historico), 200


@app.route("/chat/<int:destinatario_id>")
@login_required
def chat(destinatario_id):
    remetente_id = session.get('user_id')
    
    # 1. Obter dados do destinatário
    destinatario = get_user_by_id(destinatario_id)
    if not destinatario:
        flash("Usuário de chat não encontrado.", 'danger')
        return redirect(url_for('pagina_inicial'))
        
    # 2. Obter histórico de mensagens
    historico = get_chat_history(remetente_id, destinatario_id)
    
    return render_template('ArquivosGerais/TelaChat/chat.html',
     destinatario=destinatario,
    SUPABASE_URL=os.environ.get("SUPABASE_URL"),
    SUPABASE_ANON_KEY=os.environ.get("SUPABASE_KEY")

)



@app.route("/send_message", methods=['POST'])
@login_required
def send_message():
    remetente_id = session.get('user_id')
    
    data = request.get_json()
    destinatario_id = data.get('destinatario_id')
    content = data.get('content')

    if not destinatario_id or not content:
        return jsonify({'success': False, 'message': 'Dados incompletos.'}), 400

    success, message_or_id = create_message(remetente_id, destinatario_id, content)

    return jsonify({'success': success, 'id': message_or_id})

    
    if success:
        # Retorna a mensagem recém-criada para ser adicionada dinamicamente
        # Aqui você pode buscar a mensagem completa do banco se necessário, 
        # mas para simplificar, retornamos o que foi enviado
        return jsonify({
            'success': True, 
            'message': {
                'id': message_or_id,
                'remetente_id': remetente_id,
                'conteudo': content,
                'created_at': datetime.now().isoformat() # Usar hora do servidor
            }
        }), 200
    else:
        return jsonify({'success': False, 'message': message_or_id}), 500


if __name__ == "__main__":
    # O Render usa Gunicorn, então esta parte é mais para desenvolvimento local
    app.run(debug=True)
