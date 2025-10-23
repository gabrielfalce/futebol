import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from dotenv import load_dotenv
# Assumindo que 'database' é um módulo seu
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
    logging.critical("ERRO: SUPABASE_URL, SUPABASE_KEY e SUPABASE_SERVICE_KEY devem estar definidos nas variáveis de ambiente.")
    supabase = None
else:
    try:
        supabase: Client = create_client(url, key)
        logging.info("Sucesso: Cliente Supabase inicializado.")
    except Exception as e:
        logging.critical(f"Erro ao inicializar o cliente Supabase: {e}")
        supabase = None

# --- CONFIGURAÇÃO DO FLASK ---
# Pega o diretório onde o app.py está localizado
app_dir = os.path.dirname(os.path.abspath(__file__))

# Define o caminho raiz para os templates ('telasHTML')
# Ajustado para subir dois níveis, conforme sua estrutura implícita
template_dir = os.path.abspath(os.path.join(app_dir, '..', '..'))

app = Flask(
    __name__,
    template_folder=template_dir
)
app.secret_key = os.environ.get("SUPABASE_SERVICE_KEY")
if not app.secret_key:
    raise ValueError("SUPABASE_SERVICE_KEY (usado como app.secret_key) deve estar definido nas variáveis de ambiente.")

# --- ROTA DE ASSETS (UNIVERSAL) ---
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(template_dir, filename)

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

# --- ROTAS PRINCIPAIS (COM CORREÇÃO DE FLUXO) ---

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
            return render_template('ArquivosGerais/telaDeLogin/telaLogin.html')
        
        user_data = check_user(email, senha) 
        
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            # CORREÇÃO: Redireciona para /loading, onde o HTML tem o script de transição
            return redirect(url_for('tela_de_loading')) 
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            return render_template('ArquivosGerais/telaDeLogin/telaLogin.html')
            
    return render_template('ArquivosGerais/telaDeLogin/telaLogin.html')

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    if supabase is None:
        flash('Erro de conexão com o banco de dados.', 'danger')
        session.clear()
        return redirect(url_for('login'))
        
    try:
        # Busca o ID e valida a sessão
        response = supabase.table('usuarios').select('id, nome, profile_image_url').eq('email', session['user_email']).single().execute()
        user_data_db = response.data
        
        if user_data_db:
            session['user_id'] = user_data_db['id']
            lista_de_usuarios = get_all_users() 
            
            return render_template(
                "ArquivosGerais/TelaInicial/TelaInicial.html", 
                usuarios=lista_de_usuarios
            )
        else:
            flash('Dados do usuário não encontrados. Por favor, faça login novamente.', 'danger')
            session.clear()
            return redirect(url_for('login'))

    except APIError as e:
        logging.error(f"Erro ao buscar dados do usuário na página inicial (APIError): {e}")
        flash('Ocorreu um erro ao carregar seus dados. Tente novamente.', 'danger')
        session.clear()
        return redirect(url_for('login'))
    except Exception as e:
        logging.critical(f"Erro inesperado em /inicio: {e}", exc_info=True)
        flash('Erro interno do servidor. Tente novamente.', 'danger')
        session.clear()
        return redirect(url_for('login'))

@app.route("/usuario")
def pagina_usuario():
    if 'user_email' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
        
    user_data = get_user_by_email(session['user_email'])
    
    if user_data:
        return render_template("ArquivosGerais/TelaDeUsuario/TelaUser.html", usuario=user_data)
    else:
        flash('Erro: Dados do usuário não encontrados. Por favor, faça login novamente.', 'danger')
        session.pop('user_email', None)
        session.pop('user_id', None)
        return redirect(url_for('login'))

@app.route("/loading")
def tela_de_loading():
    # ROTA DE LOADING MANTIDA: A correção do loop está no script JS do Telaloading.html
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("ArquivosGerais/TelaLoading/Telaloading.html")

@app.route("/cadastro")
def cadastro():
    return render_template("ArquivosGerais/Cadastrar_templates/cadastrar.html")

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
        data_obj = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
            try:
                data_obj = datetime.strptime(nascimento_str, fmt)
                break
            except ValueError:
                continue
        
        if not data_obj:
            raise ValueError("Formato de data inválido")

        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
        
    except (ValueError, Exception) as e:
        logging.error(f"Erro ao processar data de nascimento: {e}")
        flash("Erro: A data de nascimento deve estar em um formato válido (ex: AAAA-MM-DD ou DD/MM/AAAA).", 'danger')
        return redirect(url_for('cadastro'))

    # Gera o hash da senha
    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
    
    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade,
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero,
        numero_camisa=numero_camisa
    )

    if sucesso:
        session['user_email'] = email
        flash(mensagem, 'success')
        # CORREÇÃO: Redireciona para /loading, onde o HTML tem o script de transição
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
    return render_template('ArquivosGerais/TelaFeed/feed.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    user_email = session['user_email']
    
    if not file.filename:
        return jsonify({'success': False, 'message': 'Nome de arquivo inválido.'}), 400

    if supabase is None or service_key is None:
        logging.critical("ERRO DE CONFIGURAÇÃO: O cliente Supabase ou Service Key não estão definidos.")
        return jsonify({'success': False, 'message': 'Erro de configuração do servidor.'}), 500

    try:
        supabase_admin = create_client(url, service_key) 
        file_content = file.read()
        
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"public/{user_email.replace('@', '_').replace('.', '-')}_{int(datetime.now().timestamp())}.{file_extension}"
        
        # Faz o upload
        supabase_admin.storage.from_('profile_images').upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        # Pega a URL pública
        image_url = supabase.storage.from_('profile_images').get_public_url(file_name)
        
        # Lógica para remover imagem antiga
        user_data = get_user_by_email(user_email)
        old_image_url = user_data.get('profile_image_url') if user_data else None
        
        if old_image_url and 'supabase.co' in old_image_url:
            parts = old_image_url.split('/profile_images/')
            if len(parts) > 1:
                old_file_path_in_bucket = parts[1]
                try:
                    supabase_admin.storage.from_('profile_images').remove([old_file_path_in_bucket])
                except Exception as e:
                    logging.warning(f"Não foi possível remover a imagem antiga '{old_file_path_in_bucket}': {e}")
        
        # Atualiza a URL no banco de dados
        sucesso, mensagem = update_user_profile_image(user_email, image_url)
        if not sucesso:
            return jsonify({'success': False, 'message': mensagem}), 500
            
        return jsonify({'success': True, 'image_url': image_url})
        
    except APIError as e:
        logging.error(f"Erro ao fazer upload da imagem para o Supabase: {e}")
        return jsonify({'success': False, 'message': 'Erro ao fazer upload da imagem ou de API.'}), 500
    except Exception as e:
        logging.critical(f"Erro inesperado em /upload_image: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erro interno do servidor ao processar a imagem.'}), 500

@app.route('/chat/<int:destinatario_id>')
def pagina_chat(destinatario_id):
    if destinatario_id <= 0:
        flash('ID de destinatário inválido.', 'danger')
        return redirect(url_for('pagina_inicial'))
    
    if 'user_email' not in session or not session.get('user_id') or supabase is None:
        flash('Sessão de usuário incompleta ou erro de banco de dados.', 'warning')
        return redirect(url_for('login'))
    
    remetente_id = session['user_id']
    
    try:
        remetente_response = supabase.table('usuarios').select('id, nome').eq('id', remetente_id).single().execute()
        remetente = remetente_response.data
        if not remetente:
            flash('Erro ao carregar dados do remetente.', 'danger')
            return redirect(url_for('pagina_inicial'))
        
        destinatario_response = supabase.table('usuarios').select('id, nome, profile_image_url').eq('id', destinatario_id).single().execute()
        destinatario = destinatario_response.data
        if not destinatario:
            flash('Usuário para chat não encontrado.', 'danger')
            return redirect(url_for('pagina_inicial'))
        
        if remetente_id == destinatario_id:
             flash('Você não pode iniciar um chat consigo mesmo.', 'warning')
             return redirect(url_for('pagina_inicial'))

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        return render_template(
            'ArquivosGerais/TelaChat/chat.html', 
            remetente=remetente, 
            destinatario=destinatario, 
            supabase_url=supabase_url, 
            supabase_key=supabase_key
        )
        
    except APIError as e:
        logging.error(f"Erro ao buscar dados do chat: {e}")
        flash('Erro ao carregar dados do chat.', 'danger')
        return redirect(url_for('pagina_inicial'))

@app.route('/api/chat/historico/<int:destinatario_id>')
def get_historico_chat(destinatario_id):
    if 'user_email' not in session or not session.get('user_id') or supabase is None:
        return jsonify({"error": "Não autorizado"}), 401
    
    remetente_id = session['user_id']
    
    try:
        response_ab = supabase.table('mensagens')\
            .select('*')\
            .or_(
                f'remetente_id.eq.{remetente_id},destinatario_id.eq.{destinatario_id}',
                f'remetente_id.eq.{destinatario_id},destinatario_id.eq.{remetente_id}'
            )\
            .order('created_at', ascending=True)\
            .execute()
            
        mensagens = response_ab.data
        return jsonify(mensagens)
        
    except APIError as e:
        logging.error(f"Erro ao buscar histórico de chat: {e}")
        return jsonify({"error": "Erro ao buscar mensagens."}), 500

@app.route('/api/posts')
def get_posts():
    if 'user_email' not in session or supabase is None:
        return jsonify({"error": "Não autorizado"}), 401
    
    try:
        response = supabase.table('posts').select('*', count='exact').order('created_at', ascending=False).limit(20).execute()
        posts = response.data
        return jsonify(posts)
    except APIError as e:
        logging.error(f"Erro ao buscar posts: {e}")
        return jsonify({"error": "Erro ao buscar posts do feed."}), 500

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("O email é obrigatório.", 'danger')
            return redirect(url_for('esqueci_senha'))
        
        if supabase is None:
            flash('Erro de conexão com o banco de dados.', 'danger')
            return redirect(url_for('esqueci_senha'))

        try:
            supabase.auth.reset_password_for_email(email, url_for('redefinir_senha', _external=True))
            flash('Se o email estiver registrado, um link de redefinição de senha foi enviado.', 'success')
        except Exception as e:
             logging.error(f"Erro ao solicitar redefinição de senha para {email}: {e}")
             flash('Ocorreu um erro ao tentar enviar o email. Tente novamente.', 'danger')
             
        return redirect(url_for('login'))
    
    return render_template('ArquivosGerais/RecuperarSenha/esqueci_senha.html')

@app.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'GET':
        return render_template('ArquivosGerais/RecuperarSenha/redefinir_senha.html')

    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        
        if not nova_senha or len(nova_senha) < 8:
            flash("A nova senha deve ter no mínimo 8 caracteres.", 'danger')
            return render_template('ArquivosGerais/RecuperarSenha/redefinir_senha.html')
        
        if supabase is None:
            flash('Erro de conexão com o banco de dados.', 'danger')
            return redirect(url_for('login'))

        try:
            # O Supabase usa o JWT (que estaria na URL ou cookies/local storage) para identificar o usuário
            # no momento da redefinição.
            supabase.auth.update_user(password=nova_senha)
            flash('Sua senha foi redefinida com sucesso. Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Erro ao redefinir senha: {e}")
            flash('Erro ao redefinir a senha. O link pode ter expirado ou estar inválido.', 'danger')
            return render_template('ArquivosGerais/RecuperarSenha/redefinir_senha.html')

if __name__ == '__main__':
    if not supabase:
        logging.critical("Aplicação não pode ser iniciada: Falha na inicialização do Supabase.")
    else:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
