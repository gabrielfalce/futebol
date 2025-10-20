import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from database import inserir_usuario, check_user, get_all_users, get_user_by_email, update_user_profile_image
import bcrypt
from datetime import datetime
from supabase import create_client, Client
from postgrest.exceptions import APIError



# --- CONFIGURAÇÃO DE LOGGING PROFISSIONAL ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURAÇÃO DE SUPABASE ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- CONFIGURAÇÃO DO FLASK ---
app_dir = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.abspath(os.path.join(app_dir, '..'))

app = Flask(
    __name__,
    template_folder=template_root,
    static_folder=os.path.join(template_root, 'STATIC') 
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", 'uma_chave_muito_secreta_e_dificil_de_adivinhar')

# --- ROTAS PARA ARQUIVOS ESTÁTICOS ---
@app.route('/Cadastrar_templates/<path:filename>')
def serve_cadastrar_static(filename):
    return send_from_directory(os.path.join(template_root, 'Cadastrar_templates'), filename)

@app.route('/telaDeLogin/<path:filename>')
def serve_login_static(filename):
    return send_from_directory(os.path.join(template_root, 'telaDeLogin'), filename)

@app.route('/TelaInicial/<path:filename>')
def serve_inicial_static(filename):
    return send_from_directory(os.path.join(template_root, 'TelaInicial'), filename)

@app.route('/TelaLoading/<path:filename>')
def serve_loading_static(filename):
    return send_from_directory(os.path.join(template_root, 'TelaLoading'), filename)

@app.route('/TelaDeUsuario/<path:filename>')
def serve_usuario_static(filename):
    return send_from_directory(os.path.join(template_root, 'TelaDeUsuario'), filename)

@app.route('/TelaChat/<path:filename>')
def serve_chat_static(filename):
    return send_from_directory(os.path.join(template_root, 'TelaChat'), filename)

@app.route('/feed')
def pagina_feed():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    return render_template('TelaFeed/feed.html')


@app.route('/TelaFeed/<path:filename>')
def serve_feed_static(filename):
    return send_from_directory(os.path.join(template_root, 'TelaFeed'), filename)


# --- FILTRO JINJA ---
@app.template_filter('format_date')
def format_date(date_str):
    if not date_str: return ""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except (ValueError, TypeError): return date_str

# --- ROTAS PRINCIPAIS ---
@app.route("/")
def index():
    if 'user_email' in session: return redirect(url_for('pagina_inicial'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session: return redirect(url_for('pagina_inicial'))
    if request.method == 'POST':
        email, senha = request.form.get('email'), request.form.get('senha')
        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'danger')
            return render_template('telaDeLogin/telaLogin.html')
        user_data = check_user(email, senha)
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            return render_template('telaDeLogin/telaLogin.html')
    return render_template('telaDeLogin/telaLogin.html')

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user_data = supabase.table('usuarios').select('id').eq('email', session['user_email']).single().execute().data
        if user_data:
            session['user_id'] = user_data['id']
        else:
            flash('Sessão inválida, por favor faça login novamente.', 'danger')
            session.clear()
            return redirect(url_for('login'))
    except Exception as e:
        logging.error(f"Erro ao buscar ID do usuário na página inicial: {e}")
        flash('Ocorreu um erro ao carregar seus dados. Tente novamente.', 'danger')
        return redirect(url_for('login'))

    lista_de_usuarios = get_all_users()
    return render_template("TelaInicial/TelaInicial.html", usuarios=lista_de_usuarios)

@app.route("/usuario")
def pagina_usuario():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
    user_data = get_user_by_email(session['user_email'])
    if user_data: return render_template("TelaDeUsuario/TelaUser.html", usuario=user_data)
    else:
        flash('Erro: Dados do usuário não encontrados. Por favor, faça login novamente.', 'danger')
        session.pop('user_email', None)
        return redirect(url_for('login'))

@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template("TelaLoading/Telaloading.html")

@app.route("/cadastro")
def cadastro():
    return render_template("Cadastrar_templates/cadastrar.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    # Pega todos os dados do formulário, incluindo o novo campo
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao")
    nascimento_str = request.form.get("nascimento")
    numero = request.form.get("numero")
    numero_camisa = request.form.get("numero_camisa") # NOVO CAMPO

    # Validação para garantir que todos os campos foram preenchidos
    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento_str, numero, numero_camisa]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('cadastro'))
        
    try:
        # A data pode vir no formato AAAA-MM-DD do input type="date" ou DD/MM/AAAA do texto
        try:
            data_obj = datetime.strptime(nascimento_str, '%Y-%m-%d')
        except ValueError:
            data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
        
        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        flash("Erro: A data de nascimento deve estar no formato DD/MM/AAAA ou ser selecionada no calendário.", 'danger')
        return redirect(url_for('cadastro'))

    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
    
    # Chama a função de inserir, agora passando também o numero_camisa
    # (Precisamos atualizar a função inserir_usuario em database.py)
    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade,
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero,
        numero_camisa=numero_camisa # NOVO PARÂMETRO
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

# --- ROTA DE UPLOAD ---
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
        supabase_admin.storage.from_('profile_images').upload(path=file_name, file=file_content, file_options={"content-type": file.content_type})
        image_url = supabase.storage.from_('profile_images').get_public_url(file_name)
        sucesso, mensagem = update_user_profile_image(user_email, image_url)
        if not sucesso: return jsonify({'success': False, 'message': mensagem}), 500
        return jsonify({'success': True, 'image_url': image_url})
    except Exception as e:
        logging.critical(f"ERRO CRÍTICO EM /upload_image: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erro interno do servidor ao processar a imagem.'}), 500

# --- ROTAS DO CHAT ---
@app.route('/chat/<int:destinatario_id>')
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    remetente = supabase.table('usuarios').select('id, nome').eq('email', session['user_email']).single().execute().data
    if not remetente: return redirect(url_for('login'))
    destinatario = supabase.table('usuarios').select('id, nome, profile_image_url').eq('id', destinatario_id).single().execute().data
    if not destinatario:
        flash('Usuário para chat não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    return render_template('TelaChat/chat.html', remetente=remetente, destinatario=destinatario, supabase_url=supabase_url, supabase_key=supabase_key)

@app.route('/api/chat/historico/<int:destinatario_id>')
def get_historico_chat(destinatario_id):
    if 'user_email' not in session:
        return jsonify({"error": "Não autorizado"}), 401
    remetente_id = session.get('user_id')
    if not remetente_id:
        remetente_data = supabase.table('usuarios').select('id').eq('email', session['user_email']).single().execute().data
        if not remetente_data: return jsonify({"error": "Remetente não encontrado"}), 404
        remetente_id = remetente_data['id']
    
    query1 = supabase.table('mensagens').select('*').eq('remetente_id', remetente_id).eq('destinatario_id', destinatario_id)
    query2 = supabase.table('mensagens').select('*').eq('remetente_id', destinatario_id).eq('destinatario_id', remetente_id)
    
    response1 = query1.execute()
    response2 = query2.execute()
    mensagens = (response1.data or []) + (response2.data or [])
    mensagens.sort(key=lambda m: m['created_at'])
    
    return jsonify(mensagens)

# --- API PARA POSTS COM PAGINAÇÃO ---
@app.route('/api/posts')
def get_posts():
    if 'user_email' not in session:
        return jsonify({"error": "Não autorizado"}), 401
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({"error": "Parâmetros 'page' e 'limit' devem ser números."}), 400

    offset = (page - 1) * limit

    try:
        response = supabase.table('posts').select('''
            *,
            autor:usuarios ( nome, profile_image_url )
        ''').order('created_at', desc=True).range(offset, offset + limit - 1).execute()

        return jsonify(response.data or [])
    except Exception as e:
        logging.error(f"Erro ao buscar posts: {e}")
        return jsonify({"error": "Erro interno ao buscar posts."}), 500


# --- ROTAS DE RECUPERAÇÃO DE SENHA ---

@app.route('/esqueci-senha', methods=['GET', 'POST'] )
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Por favor, insira um e-mail.', 'danger')
            return redirect(url_for('esqueci_senha'))
        
        try:
            # Esta é a função mágica do Supabase
            supabase.auth.reset_password_for_email(email)
            flash('Se o e-mail estiver cadastrado, um link para redefinição de senha foi enviado.', 'success')
        except Exception as e:
            # Não informamos o erro exato para não vazar se um e-mail existe ou não
            logging.error(f"Tentativa de reset de senha para {email} falhou: {e}")
            flash('Se o e-mail estiver cadastrado, um link para redefinição de senha foi enviado.', 'info')

        return redirect(url_for('login'))
        
    return render_template('RecuperarSenha/esqueci_senha.html')

@app.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        if not nova_senha or len(nova_senha) < 6:
            flash('A senha precisa ter no mínimo 6 caracteres.', 'danger')
            return render_template('RecuperarSenha/redefinir_senha.html')

        try:
            # O Supabase usa o token da URL para identificar o usuário
            user = supabase.auth.get_user()
            if user:
                supabase.auth.update_user({'password': nova_senha})
                flash('Senha redefinida com sucesso! Você já pode fazer login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Link de redefinição inválido ou expirado. Tente novamente.', 'danger')
                return redirect(url_for('esqueci_senha'))
        except Exception as e:
            logging.error(f"Erro ao redefinir senha: {e}")
            flash('Ocorreu um erro ao redefinir sua senha. O link pode ter expirado.', 'danger')
            return redirect(url_for('esqueci_senha'))

    return render_template('RecuperarSenha/redefinir_senha.html')


# --- ROTAS DE EDIÇÃO DE PERFIL ---

@app.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Pega os dados do formulário
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        numero_telefone = request.form.get('numero_telefone') # Novo campo
        numero_camisa = request.form.get('numero_camisa')   # Novo campo

        # Cria o dicionário apenas com os campos que o usuário preencheu
        update_data = {}
        if nome: update_data['nome'] = nome
        if cidade: update_data['cidade'] = cidade
        if posicao: update_data['posicao'] = posicao
        if numero_telefone: update_data['numero'] = numero_telefone # Salva na coluna 'numero'
        if numero_camisa: update_data['numero_camisa'] = numero_camisa # Salva na nova coluna

        if update_data:
            try:
                supabase.table('usuarios').update(update_data).eq('email', session['user_email']).execute()
                flash('Perfil atualizado com sucesso!', 'success')
            except Exception as e:
                logging.error(f"Erro ao atualizar perfil de {session['user_email']}: {e}")
                flash('Ocorreu um erro ao atualizar seu perfil.', 'danger')
        else:
            flash('Nenhum dado foi alterado.', 'info')
        
        return redirect(url_for('pagina_usuario'))

    # Certifique-se de que get_user_by_email busca a nova coluna também
    user_data = get_user_by_email(session['user_email'])
    if not user_data:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    return render_template('TelaDeUsuario/editar_perfil.html', usuario=user_data)
    
# --- EXECUÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
