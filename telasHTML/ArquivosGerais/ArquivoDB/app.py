import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import (
    register_user, check_user, get_all_users, get_user_by_email,
    update_user_profile_image, update_user_profile, get_user_by_id, update_password,
    create_post, get_posts_by_user, get_all_posts, get_post_by_id, supabase,
    create_message, # Adicionado para salvar mensagens
    get_chat_history # Adicionado para buscar histórico
)
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
import uuid # Para gerar nomes de arquivo únicos

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Ajuste o caminho BASE_DIR conforme a estrutura do seu projeto se necessário
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

# === FUNÇÕES AUXILIARES ===

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator de verificação de login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('strftime')
def _jinja2_filter_strftime(date_str, fmt='%d/%m/%Y às %H:%M'):
    """Filtro Jinja para formatar datas (formato ISO do Supabase)."""
    if not date_str:
        return ''
    try:
        # Lida com o formato ISO 8601 (com ou sem 'Z' para UTC)
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(fmt)
    except ValueError:
        return 'Data Inválida'

# === ROTAS DE ASSETS (CSS/JS/IMAGENS) ===

@app.route('/static/login/<path:filename>')
def login_assets(filename):
    return send_from_directory('telasHTML/Login', filename)

@app.route('/static/cadastro/<path:filename>')
def cadastro_assets(filename):
    return send_from_directory('telasHTML/Cadastro', filename)
    
@app.route('/static/chat/<path:filename>')
def chat_assets(filename):
    return send_from_directory('telasHTML/ArquivosGerais/TelaChat', filename)

@app.route('/static/user_assets/<path:filename>')
def user_assets(filename):
    return send_from_directory('telasHTML/ArquivosGerais', filename)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Rota para servir imagens de perfil."""
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
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = check_user(email, senha)

        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_nome'] = user['nome']
            flash(f'Bem-vindo, {user["nome"]}!', 'success')
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
            return render_template("telaDeLogin/telaLogin.html", email=email)
            
    return render_template("telaDeLogin/telaLogin.html")

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
            success, message = register_user(nome, email, senha, cidade, posicao, nascimento, numero_camisa, numero_telefone)
            if success:
                flash(message, 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'danger')

    return render_template("telasHTML/Cadastro/cadastrar.html", form_data=form_data)

@app.route("/esqueci_senha")
def esqueci_senha():
    # Rota básica de recuperação de senha (apenas renderiza o template)
    # A funcionalidade real de envio de e-mail deve ser implementada aqui
    return render_template("telasHTML/RecuperarSenha/esqueci_senha.html")

@app.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        # Assume que o email vem da query string ou de um campo oculto
        email = request.args.get('email') or request.form.get('email') 
        
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
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))


# === ROTAS DA APLICAÇÃO ===

@app.route("/pagina_inicial")
@login_required
def pagina_inicial():
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    # Carrega posts para o feed
    posts = get_all_posts() 
    
    return render_template("telasHTML/ArquivosGerais/TelaPrincipal/index.html", user=user, posts=posts)


@app.route("/perfil/<int:user_id>")
@login_required
def perfil(user_id):
    user_data = get_user_by_id(user_id)
    posts = get_posts_by_user(user_id) # Busca os posts específicos do usuário
    
    if not user_data:
        flash("Usuário não encontrado.", 'danger')
        return redirect(url_for('pagina_inicial'))
        
    is_current_user = user_id == session.get('user_id')
    
    return render_template(
        "telasHTML/ArquivosGerais/TelaDeUsuario/usuario.html", 
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
        # Gera um nome de arquivo único
        filename_base = str(uuid.uuid4())
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{filename_base}.{extension}")
        
        # Define o caminho de salvamento local
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        # O caminho URL que será salvo no banco de dados e usado no frontend
        # Note: 'uploads/' deve corresponder à rota @app.route('/uploads/<path:filename>')
        profile_image_url_path = f"uploads/{filename}" 
        
        if update_user_profile_image(user_email, profile_image_url_path):
            flash('Foto de perfil atualizada com sucesso!', 'success')
        else:
            flash('Falha ao salvar o caminho da imagem no banco de dados.', 'danger')
            
    else:
        flash('Tipo de arquivo não permitido.', 'danger')
        
    return redirect(url_for('perfil', user_id=user_id))

# Rota para edição de perfil (exceto imagem, que tem sua própria rota)
@app.route("/editar_perfil", methods=['POST'])
@login_required
def editar_perfil():
    user_id = session.get('user_id')
    nome = request.form.get('nome')
    bio = request.form.get('bio') 
    
    if update_user_profile(user_id, nome, bio, None): # None para a URL da imagem (usamos rota separada)
        flash('Perfil atualizado com sucesso!', 'success')
    else:
        flash('Falha ao atualizar o perfil.', 'danger')

    return redirect(url_for('perfil', user_id=user_id))

# === ROTAS DE POSTS ===

@app.route("/create_post", methods=['POST'])
@login_required
def api_create_post():
    autor_id = session.get('user_id')
    legenda = request.form.get('legenda', '')
    imagem_url = None
    
    if 'post_image' in request.files:
        file = request.files['post_image']
        if file.filename != '' and allowed_file(file.filename):
            filename_base = str(uuid.uuid4())
            extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{filename_base}.{extension}")
            
            save_path = os.path.join(app.config['POST_UPLOAD_FOLDER'], filename)
            file.save(save_path)
            # Note: 'post_uploads/' deve corresponder à rota @app.route('/post_uploads/<path:filename>')
            imagem_url = f"post_uploads/{filename}" 

    success, result = create_post(autor_id, legenda, imagem_url)
    
    if success:
        flash('Post criado com sucesso!', 'success')
        return redirect(url_for('pagina_inicial'))
    else:
        flash(f'Falha ao criar post: {result}', 'danger')
        return redirect(url_for('pagina_inicial'))


# === ROTAS DE CHAT ===

# 1. Rota principal do chat (renderiza o HTML)
@app.route("/chat/<int:destinatario_id>")
@login_required
def chat(destinatario_id):
    destinatario = get_user_by_id(destinatario_id)
    if not destinatario:
        flash("Usuário de destino não encontrado.", 'danger')
        return redirect(url_for('pagina_inicial'))

    # Garante que a chave 'anon' é usada para o frontend (melhor prática de segurança)
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_KEY") # Usando SUPABASE_KEY como ANON key se não houver ANON_KEY
    
    return render_template(
        "telasHTML/ArquivosGerais/TelaChat/chat.html",
        destinatario=destinatario,
        SUPABASE_URL=supabase_url,
        SUPABASE_ANON_KEY=supabase_anon_key, # Passado para o JS
        # O user_id é pego da session pelo Jinja no chat.html
    )

# 2. ROTA API CHAT - PARA ENVIAR MENSAGENS (via POST)
@app.route("/api/chat/send_message", methods=['POST'])
@login_required
def api_send_message():
    remetente_id = session.get('user_id') 
    
    data = request.get_json()
    destinatario_id = data.get('destinatario_id')
    content = data.get('content') # Nome usado pelo frontend (chat.js)

    if not all([remetente_id, destinatario_id, content]):
        return jsonify({'success': False, 'error': 'Dados incompletos para envio.'}), 400

    try:
        destinatario_id = int(destinatario_id)
        
        # Chama a função de banco de dados (que usa o campo 'conteudo')
        success, result = create_message(remetente_id, destinatario_id, content)

        if success:
            return jsonify({'success': True, 'message_id': result}), 201
        else:
            return jsonify({'success': False, 'error': result}), 500
            
    except ValueError:
        return jsonify({'success': False, 'error': 'ID de destinatário inválido.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro interno do servidor: {str(e)}'}), 500


# 3. ROTA API CHAT - PARA CARREGAR HISTÓRICO (via GET)
@app.route("/api/chat/historico/<int:destinatario_id>", methods=['GET'])
@login_required
def api_get_chat_history(destinatario_id):
    remetente_id = session.get('user_id')
    
    if not remetente_id:
        return jsonify({'success': False, 'error': 'Usuário não autenticado.'}), 401

    try:
        # Busca o histórico entre o usuário logado e o destinatário
        messages = get_chat_history(remetente_id, destinatario_id)
        
        # Retorna a lista de mensagens como JSON
        return jsonify(messages), 200

    except Exception as e:
        print(f"ERRO ao buscar histórico de chat: {e}")
        return jsonify({'success': False, 'error': 'Falha ao buscar histórico de chat.'}), 500


# === EXECUÇÃO DA APLICAÇÃO ===

if __name__ == '__main__':
    # Configuração para servir uploads localmente durante o desenvolvimento
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
    app.config['POST_UPLOAD_FOLDER'] = os.path.join(BASE_DIR, POST_UPLOAD_FOLDER_RELATIVE)

    # Cria diretórios se não existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['POST_UPLOAD_FOLDER'], exist_ok=True)
    
    # Executa a aplicação Flask
    app.run(debug=True)
