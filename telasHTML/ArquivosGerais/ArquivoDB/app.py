import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from database import inserir_usuario, check_user, get_all_users, get_user_by_email, update_user_profile_image
import bcrypt
from datetime import datetime
from jinja2.exceptions import TemplateNotFound
from supabase import create_client, Client
from postgrest.exceptions import APIError

# --- CONFIGURAÇÃO DE LOGGING PROFISSIONAL ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURAÇÃO DE SUPABASE ---
# Cliente público, usado para a maioria das operações de leitura
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
    nome, email, senha_texto_puro = request.form.get("nome"), request.form.get("email"), request.form.get("senha")
    cidade, posicao, nascimento_str, numero = request.form.get("cidade"), request.form.get("posicao"), request.form.get("nascimento"), request.form.get("numero")
    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento_str, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('cadastro'))
    try:
        data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        flash("Erro: A data de nascimento deve ser no formato DD/MM/AAAA.", 'danger')
        return redirect(url_for('cadastro'))
    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
    sucesso, mensagem = inserir_usuario(nome=nome, email=email, senha_hash=senha_hash, cidade=cidade, posicao=posicao, nascimento=data_nascimento_iso, numero=numero)
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
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

# --- ROTA DE UPLOAD FINAL ---
@app.route('/upload_image', methods=['POST'])
def upload_image():
    logging.info("ROTA /upload_image ACESSADA")
    if 'user_email' not in session:
        logging.error("FALHA DE AUTENTICAÇÃO: Usuário não está na sessão.")
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    if 'file' not in request.files:
        logging.error("FALHA DE UPLOAD: 'file' não encontrado no request.")
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    user_email = session['user_email']
    
    try:
        # Pega a chave de serviço secreta das variáveis de ambiente
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not service_key:
            logging.critical("ERRO DE CONFIGURAÇÃO: A variável SUPABASE_SERVICE_KEY não foi definida no Render.")
            return jsonify({'success': False, 'message': 'Erro de configuração do servidor.'}), 500

        # Cria um cliente Supabase com privilégios de administrador SÓ PARA ESTA OPERAÇÃO
        supabase_admin = create_client(url, service_key)
        logging.info("Cliente Supabase admin inicializado para o upload.")

        file_content = file.read()
        file_name = f"public/{user_email.replace('@', '_')}_{int(datetime.now().timestamp())}.jpg"
        
        logging.info(f"Tentando upload com cliente admin para o arquivo '{file_name}'.")
        
        # USA O CLIENTE ADMIN PARA O UPLOAD, que ignora as regras de RLS
        supabase_admin.storage.from_('profile_images').upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        logging.info("Upload para o Storage bem-sucedido.")
        
        # A URL pública pode ser obtida com o cliente normal (público)
        image_url = supabase.storage.from_('profile_images').get_public_url(file_name)
        logging.info(f"URL pública obtida: {image_url}")
        
        # Atualiza o banco de dados
        sucesso, mensagem = update_user_profile_image(user_email, image_url)
        if not sucesso:
            logging.error(f"Falha ao salvar a URL no banco: {mensagem}")
            return jsonify({'success': False, 'message': mensagem}), 500
        
        logging.info(f"SUCESSO TOTAL para o usuário {user_email}")
        return jsonify({'success': True, 'image_url': image_url})

    except APIError as e:
        logging.critical(f"ERRO DE API SUPABASE: Tipo={type(e).__name__}, Erro={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erro de permissão do servidor: {e.message}'}), e.status_code
    except Exception as e:
        logging.critical(f"ERRO CRÍTICO INESPERADO: Tipo={type(e).__name__}, Erro={str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Erro interno do servidor ao processar a imagem.'}), 500

# Em app.py, adicione estas rotas no final do arquivo, antes do if __name__ == '__main__':

# Rota para servir os arquivos estáticos da pasta do chat
@app.route('/TelaChat/<path:filename>')
def serve_chat_static(filename):
    return send_from_directory(os.path.join(template_root, 'TelaChat'), filename)

# Rota para abrir a página de chat com um usuário específico
@app.route('/chat/<int:destinatario_id>')
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Busca os dados do remetente (usuário logado)
    remetente = supabase.table('usuarios').select('id, nome').eq('email', session['user_email']).single().execute().data
    if not remetente:
        return redirect(url_for('login'))

    # Busca os dados do destinatário
    destinatario = supabase.table('usuarios').select('id, nome, profile_image_url').eq('id', destinatario_id).single().execute().data
    if not destinatario:
        flash('Usuário para chat não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    # Renderiza a página de chat, passando os dados dos dois usuários
    return render_template('TelaChat/chat.html', remetente=remetente, destinatario=destinatario)


# Rota de API para buscar o histórico de mensagens
@app.route('/api/chat/historico/<int:destinatario_id>')
def get_historico_chat(destinatario_id):
    if 'user_email' not in session:
        return jsonify({"error": "Não autorizado"}), 401
    
    # Pega o ID do usuário logado
    remetente_id = supabase.table('usuarios').select('id').eq('email', session['user_email']).single().execute().data['id']

    # Busca mensagens onde o remetente é o logado e o destinatário é o outro, OU vice-versa
    query1 = supabase.table('mensagens').select('*').eq('remetente_id', remetente_id).eq('destinatario_id', destinatario_id)
    query2 = supabase.table('mensagens').select('*').eq('remetente_id', destinatario_id).eq('destinatario_id', remetente_id)
    
    # Combina as duas buscas
    mensagens = query1.execute().data + query2.execute().data
    
    # Ordena as mensagens pela data de criação
    mensagens.sort(key=lambda m: m['created_at'])
    
    return jsonify(mensagens)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # debug=False é o recomendado para produção e para o logging funcionar melhor com Gunicorn
    app.run(host='0.0.0.0', port=port, debug=False)
