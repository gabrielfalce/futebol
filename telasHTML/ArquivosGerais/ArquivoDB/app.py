import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from dotenv import load_dotenv
from database import inserir_usuario, check_user, get_all_users, get_user_by_email, update_user_profile_image
import bcrypt
from datetime import datetime
from supabase import create_client, Client
from postgrest.exceptions import APIError

# Carrega variáveis de ambiente do .env
load_dotenv()

# --- CONFIGURAÇÃO DE LOGGING PROFISSIONAL ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURAÇÃO DE SUPABASE ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")
if not url or not key or not service_key:
    raise ValueError("SUPABASE_URL, SUPABASE_KEY e SUPABASE_SERVICE_KEY devem estar definidos nas variáveis de ambiente.")
supabase: Client = create_client(url, key)
logging.info("Sucesso: Cliente Supabase inicializado.")

# --- CONFIGURAÇÃO DO FLASK ---
app_dir = os.path.dirname(os.path.abspath(__file__))

# CORREÇÃO 1: Simplificada a inicialização do Flask.
# As pastas de templates e estáticos serão gerenciadas pelas rotas.
# O caminho para `template_folder` foi ajustado para apontar para a pasta `telasHTML`.
app = Flask(
    __name__,
    template_folder=os.path.join(app_dir, 'telasHTML')
)
app.secret_key = os.environ.get("SUPABASE_SERVICE_KEY")
if not app.secret_key:
    raise ValueError("SUPABASE_SERVICE_KEY deve estar definido nas variáveis de ambiente.")


# --- CORREÇÃO 2: ROTAS PARA SERVIR ARQUIVOS ESTÁTICOS DE PASTAS ESPECÍFICAS ---
# Estas rotas dizem ao Flask como encontrar os arquivos CSS e de imagem.

# Rota para arquivos na pasta 'ArquivosGerais' (e subpastas)
@app.route('/assets/gerais/<path:filename>')
def assets_gerais(filename):
    directory = os.path.join(app.root_path, 'telasHTML', 'ArquivosGerais')
    return send_from_directory(directory, filename)

# --- FILTRO JINJA ---
@app.template_filter('format_date')
def format_date(date_str):
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return date_str

# --- ROTAS PRINCIPAIS ---
@app.route("/")
def index():
    if 'user_email' in session:
        return redirect(url_for('pagina_inicial'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('pagina_inicial'))
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'danger')
            return render_template('ArquivosGerais/telaDeLogin/telaLogin.html') # Caminho ajustado
        
        user_data = check_user(email, senha)
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            return render_template('ArquivosGerais/telaDeLogin/telaLogin.html') # Caminho ajustado
    return render_template('ArquivosGerais/telaDeLogin/telaLogin.html') # Caminho ajustado

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = supabase.auth.get_user()
        if not user or user.user.email != session['user_email']:
            flash('Sessão inválida, por favor faça login novamente.', 'danger')
            session.clear()
            return redirect(url_for('login'))

        user_data = supabase.table('usuarios').select('id').eq('email', session['user_email']).single().execute().data
        if user_data:
            session['user_id'] = user_data['id']
        else:
            flash('Sessão inválida, por favor faça login novamente.', 'danger')
            session.clear()
            return redirect(url_for('login'))

        lista_de_usuarios = get_all_users()
        return render_template("ArquivosGerais/TelaInicial/TelaInicial.html", usuarios=lista_de_usuarios) # Caminho ajustado
    except APIError as e:
        logging.error(f"Erro ao buscar ID do usuário na página inicial: {e}")
        flash('Ocorreu um erro ao carregar seus dados. Tente novamente.', 'danger')
        return redirect(url_for('login'))
    except Exception as e:
        logging.critical(f"Erro inesperado em /inicio: {e}", exc_info=True)
        flash('Erro interno do servidor. Tente novamente.', 'danger')
        return redirect(url_for('login'))

@app.route("/usuario")
def pagina_usuario():
    if 'user_email' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    user_data = get_user_by_email(session['user_email'])
    if user_data:
        return render_template("ArquivosGerais/TelaDeUsuario/TelaUser.html", usuario=user_data) # Caminho ajustado
    else:
        flash('Erro: Dados do usuário não encontrados. Por favor, faça login novamente.', 'danger')
        session.pop('user_email', None)
        session.pop('user_id', None)
        return redirect(url_for('login'))

@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("ArquivosGerais/TelaLoading/Telaloading.html") # Caminho ajustado

@app.route("/cadastro")
def cadastro():
    return render_template("Cadastrar_templates/cadastrar.html") # Caminho ajustado

# ... (o restante do seu código permanece igual) ...
# O código de /cadastrar, /logout, /feed, /upload_image, /chat, etc. não precisa de alteração.

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao")
    nascimento_str = request.form.get("nascimento")
    numero = request.form.get("numero")
    numero_camisa = request.form.get("numero_camisa")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento_str, numero, numero_camisa]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('cadastro'))

    if len(senha_texto_puro) < 8:
        flash("Erro: A senha deve ter no mínimo 8 caracteres.", 'danger')
        return redirect(url_for('cadastro'))

    try:
        for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
            try:
                data_obj = datetime.strptime(nascimento_str, fmt)
                break
            except ValueError:
                continue
        else:
            flash("Erro: A data de nascimento deve estar no formato AAAA-MM-DD ou DD/MM/AAAA.", 'danger')
            return redirect(url_for('cadastro'))

        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
    except Exception as e:
        logging.error(f"Erro ao processar data de nascimento: {e}")
        flash("Erro: Formato de data inválido.", 'danger')
        return redirect(url_for('cadastro'))

    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
    
    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade,
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero,
        numero_camisa=numero_camisa
    )

    if sucesso:
        session['user_email'] = email
        flash(mensagem, 'success')
        return redirect(url_for('tela_de_loading'))
    else:
        flash(mensagem, 'danger')
        return redirect(url_for('cadastro'))

@app.route("/logout")
def logout():
    session.pop('user_email', None)
    session.pop('user_id', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

@app.route('/feed')
def pagina_feed():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('ArquivosGerais/TelaFeed/feed.html') # Caminho ajustado

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    user_email = session['user_email']
    try:
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not service_key:
            logging.critical("ERRO DE CONFIGURAÇÃO: A variável SUPABASE_SERVICE_KEY não foi definida.")
            return jsonify({'success': False, 'message': 'Erro de configuração do servidor.'}), 500
        
        supabase_admin = create_client(url, service_key)
        file_content = file.read()
        file_name = f"public/{user_email.replace('@', '_')}_{int(datetime.now().timestamp())}.jpg"
        
        upload_response = supabase_admin.storage.from_('profile_images').upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        if not upload_response:
            return jsonify({'success': False, 'message': 'Falha ao fazer upload da imagem.'}), 500
        
        image_url = supabase.storage.from_('profile_images').get_public_url(file_name)
        
        old_image_url = get_user_by_email(user_email).get('profile_image_url')
        if old_image_url:
            old_file_name = old_image_url.split('/')[-1]
            try:
                supabase_admin.storage.from_('profile_images').remove([f"public/{old_file_name}"])
            except Exception as e:
                logging.warning(f"Não foi possível remover a imagem antiga: {e}")
        
        sucesso, mensagem = update_user_profile_image(user_email, image_url)
        if not sucesso:
            return jsonify({'success': False, 'message': mensagem}), 500
        return jsonify({'success': True, 'image_url': image_url})
    except APIError as e:
        logging.error(f"Erro ao fazer upload da imagem para o Supabase: {e}")
        return jsonify({'success': False, 'message': 'Erro ao fazer upload da imagem.'}), 500
    except Exception as e:
        logging.critical(f"Erro inesperado em /upload_image: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erro interno do servidor ao processar a imagem.'}), 500

@app.route('/chat/<int:destinatario_id>')
def pagina_chat(destinatario_id):
    if destinatario_id <= 0:
        flash('ID de destinatário inválido.', 'danger')
        return redirect(url_for('pagina_inicial'))
    
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    try:
        remetente = supabase.table('usuarios').select('id, nome').eq('email', session['user_email']).single().execute().data
        if not remetente:
            return redirect(url_for('login'))
        
        destinatario = supabase.table('usuarios').select('id, nome, profile_image_url').eq('id', destinatario_id).single().execute().data
        if not destinatario:
            flash('Usuário para chat não encontrado.', 'danger')
            return redirect(url_for('pagina_inicial'))
        
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        return render_template('ArquivosGerais/TelaChat/chat.html', remetente=remetente, destinatario=destinatario, supabase_url=supabase_url, supabase_key=supabase_key) # Caminho ajustado
    except APIError as e:
        logging.error(f"Erro ao buscar dados do chat: {e}")
        flash('Erro ao carregar dados do chat.', 'danger')
        return redirect(url_for('pagina_inicial'))

@app.route('/api/chat/historico/<int:destinatario_id>')
def get_historico_chat(destinatario_id):
    if destinatario_id <= 0:
        return jsonify({"error": "ID de destinatário inválido"}), 400
    
    if 'user_email' not in session:
        return jsonify({"error": "Não autorizado"}), 401
    
    remetente_id = session.get('user_id')
    if not remetente_id:
        try:
            remetente_data = supabase.table('usuarios').select('id').eq('email', session['user_email']).single().execute().data
            if not remetente_data:
                return jsonify({"error": "Remetente não encontrado"}), 404
            remetente_id = remetente_data['id']
        except APIError as e:
            logging.error(f"Erro ao buscar remetente: {e}")
            return jsonify({"error": "Erro ao buscar dados do remetente."}), 500
    
    try:
        query1 = supabase.table('mensagens').select('*').eq('remetente_id', remetente_id).eq('destinatario_id', destinatario_id)
        query2 = supabase.table('mensagens').select('*').eq('remetente_id', destinatario_id).eq('destinatario_id', remetente_id)
        
        response1 = query1.execute()
        response2 = query2.execute()
        mensagens = (response1.data or []) + (response2.data or [])
        mensagens.sort(key=lambda m: m['created_at'])
        
        return jsonify(mensagens)
    except APIError as e:
        logging.error(f"Erro ao buscar histórico de chat: {e}")
        return jsonify({"error": "Erro ao buscar mensagens."}), 500

@app.route('/api/posts')
def get_posts():
    if 'user_email' not in session:
        return jsonify({"error": "Não autorizado"}), 401
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        if page < 1 or limit < 1:
            return jsonify({"error": "Parâmetros 'page' e 'limit' devem ser números positivos."}), 400
    except ValueError:
        return jsonify({"error": "Parâmetros 'page' e 'limit' devem ser números."}), 400

    offset = (page - 1) * limit

    try:
        response = supabase.table('posts').select('''
            *,
            autor:usuarios ( nome, profile_image_url )
        ''').order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        return jsonify(response.data or [])
    except APIError as e:
        logging.error(f"Erro ao buscar posts: {e}")
        return jsonify({"error": "Erro ao buscar posts."}), 500
    except Exception as e:
        logging.critical(f"Erro inesperado em /api/posts: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar posts."}), 500

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Por favor, insira um e-mail.', 'danger')
            return redirect(url_for('esqueci_senha'))
        
        try:
            supabase.auth.reset_password_for_email(email)
            flash('Se o e-mail estiver cadastrado, um link para redefinição de senha foi enviado.', 'success')
        except APIError as e:
            logging.error(f"Tentativa de reset de senha para {email} falhou: {e}")
            flash('Se o e-mail estiver cadastrado, um link para redefinição de senha foi enviado.', 'info')
        except Exception as e:
            logging.critical(f"Erro inesperado em /esqueci-senha: {e}", exc_info=True)
            flash('Erro interno do servidor. Tente novamente.', 'danger')
        
        return redirect(url_for('login'))
    
    return render_template('RecuperarSenha/esqueci_senha.html')

@app.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'GET':
        token = request.args.get('access_token')
        if not token:
            flash('Link de redefinição inválido ou expirado.', 'danger')
            return redirect(url_for('esqueci_senha'))
        return render_template('RecuperarSenha/redefinir_senha.html')

    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        if not nova_senha or len(nova_senha) < 6:
            flash('A senha precisa ter no mínimo 6 caracteres.', 'danger')
            return render_template('RecuperarSenha/redefinir_senha.html')

        try:
            response = supabase.auth.update_user({'password': nova_senha})
            if response and response.user:
                session.pop('user_email', None)
                session.pop('user_id', None)
                flash('Senha redefinida com sucesso! Por favor, faça login com a nova senha.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Link de redefinição inválido ou expirado.', 'danger')
                return redirect(url_for('esqueci_senha'))
        except APIError as e:
            logging.error(f"Erro ao redefinir senha: {e}")
            flash('Erro ao redefinir a senha. Tente novamente ou solicite um novo link.', 'danger')
            return redirect(url_for('esqueci_senha'))
        except Exception as e:
            logging.critical(f"Erro inesperado em /redefinir-senha: {e}", exc_info=True)
            flash('Erro interno do servidor. Tente novamente mais tarde.', 'danger')
            return redirect(url_for('esqueci_senha'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
