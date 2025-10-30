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
# Ajuste o BASE_DIR para apontar para a raiz do projeto se 'telasHTML' estiver em um nível acima.
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..', '..')) 

app = Flask(
    __name__,
    template_folder=BASE_DIR
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")

# Diretório para uploads de fotos de perfil (relativo ao BASE_DIR)
UPLOAD_FOLDER_RELATIVE = 'telasHTML/ArquivosGerais/TelaDeUsuario/imagens/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
# Usado por algumas telas para imagens de perfil, etc.
@app.route('/serve_static_files/<path:filename>')
def serve_static_files(filename):
    # O diretório raiz para esta rota será 'telasHTML/'
    dir_path = os.path.join(BASE_DIR, 'telasHTML')
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
            return redirect(url_for('login'))
            
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
            
            # CORREÇÃO CRÍTICA: Define 'nascimento_str' antes de usá-lo na conversão
            nascimento_str = request.form['nascimento']
            
            # Coleta do campo 'numero' (correto)
            numero = request.form['numero'] 

            # Lógica de conversão de data (DD/MM/AAAA para AAAA-MM-DD)
            nascimento_formatado = datetime.strptime(nascimento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        
            # Chamada à função register_user
            success, message = register_user(nome, email, senha, cidade, posicao, nascimento_formatado, numero)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('tela_loading', next_page='login', message_category='success'))
            else:
                flash(message, 'danger')
                return redirect(url_for('cadastro'))

        except ValueError:
            # Captura erro se o formato da data estiver incorreto
            flash('Formato de data de nascimento inválido. Use DD/MM/AAAA.', 'danger')
            return redirect(url_for('cadastro'))
        
        except Exception as e:
            # Exceções gerais (inclui erros do banco de dados não capturados dentro de register_user)
            print(f"ERRO geral no cadastro: {e}")
            flash('Ocorreu um erro inesperado ao tentar cadastrar o usuário.', 'danger')
            return redirect(url_for('cadastro'))

    return render_template("telasHTML/ArquivosGerais/Cadastrar_templates/cadastrar.html")


@app.route("/loading/<next_page>")
def tela_loading(next_page):
    # Parâmetros opcionais para customizar a mensagem/tempo
    message_category = request.args.get('message_category', 'success')
    message = request.args.get('message')
    
    # O tempo de loading pode ser passado por query param ou ser fixo
    # Se 'message' for passado, sobrescreve o flash
    if message:
        flash(message, message_category)

    # Redireciona para a rota 'next_page'
    next_url = url_for(next_page)
    
    # Renderiza a tela de loading passando o destino e um tempo (em ms)
    return render_template("telasHTML/ArquivosGerais/TelaLoading/Telaloading.html", 
                           next_url=next_url, 
                           tempo_loading=2500) # 2.5 segundos


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
    # Obtém todos os usuários para exibição
    users = get_all_users()
    
    # Filtra o próprio usuário da lista
    current_user_email = session.get('user_email')
    users = [user for user in users if user.get('email') != current_user_email]
    
    return render_template("telasHTML/ArquivosGerais/TelaInicial/TelaInicial.html", users=users)


@app.route("/perfil/<int:user_id>")
@login_required
def pagina_usuario(user_id=None):
    if user_id is None or user_id == session.get('user_id'):
        # Exibir perfil do usuário logado
        user_email = session.get('user_email')
        usuario = get_user_by_email(user_email)
        is_owner = True
    else:
        # Exibir perfil de outro usuário
        usuario = get_user_by_id(user_id)
        is_owner = False
        
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    return render_template("telasHTML/ArquivosGerais/TelaDeUsuario/TelaUser.html", 
                           usuario=usuario, 
                           is_owner=is_owner)


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
        
        # Campos de texto
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        
        if nome:
            update_data['nome'] = nome
            
        if cidade:
            update_data['cidade'] = cidade
            
        if posicao:
            update_data['posicao'] = posicao
            
        # Tratamento do upload de arquivo (Foto de Perfil)
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Cria o caminho de destino no sistema de arquivos
                full_upload_dir = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
                os.makedirs(full_upload_dir, exist_ok=True)
                file_path = os.path.join(full_upload_dir, filename)
                
                file.save(file_path)
                
                # Salva o caminho RELATIVO ao BASE_DIR para o banco de dados
                db_path = os.path.join(UPLOAD_FOLDER_RELATIVE, filename).replace('\\', '/')
                update_data['foto_perfil'] = db_path
                session['user_profile_image'] = db_path # Atualiza a sessão (se necessário)

        # Atualiza os dados no banco
        if update_data:
            success = update_user_profile(user_email, **update_data)
            if success:
                flash('Perfil atualizado com sucesso!', 'success')
            else:
                flash('Falha ao atualizar o perfil.', 'danger')
        else:
             flash('Nenhuma alteração detectada.', 'info')
             
        # Redireciona para a própria página GET para evitar reenvio de formulário
        return redirect(url_for('editar_perfil'))

    # Rota GET
    return render_template("telasHTML/ArquivosGerais/TelaDeUsuario/editar_perfil.html", usuario=usuario)


@app.route("/feed")
@login_required
def pagina_feed():
    # Renderiza a tela do feed (o conteúdo será carregado via API)
    return render_template("telasHTML/ArquivosGerais/TelaFeed/feed.html")


@app.route("/api/posts", methods=['GET'])
@login_required
def api_posts():
    # API de mock para o feed (substituiria por uma chamada ao Supabase)
    mock_posts = [
        # ... (seu mock de posts) ...
    ]
    return jsonify(mock_posts)


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

    return render_template("telasHTML/ArquivosGerais/TelaChat/chat.html", 
                           remetente=remetente, 
                           destinatario=destinatario)


@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        # Lógica de Supabase para enviar link de redefinição de senha por email
        flash(f'Se o e-mail {email} estiver cadastrado, um link de redefinição de senha foi enviado.', 'success')
        # Na aplicação real, aqui você chamaria a API de auth do Supabase
        return redirect(url_for('login'))
        
    return render_template("telasHTML/RecuperarSenha/esqueci_senha.html")


@app.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    # Esta rota é um placeholder, pois a lógica de redefinição de senha
    # depende de tokens de URL enviados pelo Supabase (ou serviço de email).
    
    if request.method == 'POST':
        # Aqui você receberia a nova senha e o token/email do formulário
        nova_senha = request.form.get('nova_senha')
        email = request.args.get('email') # Assumindo que o email vem na URL
        
        # Exemplo de lógica para atualizar a senha no banco
        if email and nova_senha and len(nova_senha) >= 6:
            if update_password(email, nova_senha): # Função hipotética no database.py
                flash('Sua senha foi redefinida com sucesso. Faça o login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Falha ao redefinir a senha. Tente novamente.', 'danger')
        else:
            flash('Senha inválida ou falta de informações.', 'danger')

    return render_template("telasHTML/RecuperarSenha/redefinir_senha.html")


if __name__ == '__main__':
    app.run(debug=True)