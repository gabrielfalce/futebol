import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from database import inserir_usuario, check_user, get_all_users, get_user_by_email, update_user_profile_image
import bcrypt
from datetime import datetime
from jinja2.exceptions import TemplateNotFound
from supabase import create_client, Client
from postgrest.exceptions import APIError # Importante para capturar erros específicos do Supabase

# --- Configuração de Supabase ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- Configuração de Caminhos e Flask ---
app_dir = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.abspath(os.path.join(app_dir, '..'))

app = Flask(
    __name__,
    template_folder=template_root,
    static_folder=os.path.join(template_root, 'STATIC') 
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", 'uma_chave_muito_secreta_e_dificil_de_adivinhar')

# --- Rotas para servir arquivos estáticos (CSS, JS, Imagens) ---
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

# --- Filtro Jinja para formatar data ---
@app.template_filter('format_date')
def format_date(date_str):
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return date_str

# --- Rotas Principais da Aplicação ---

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
    
    if user_data:
        return render_template("TelaDeUsuario/TelaUser.html", usuario=user_data)
    else:
        flash('Erro: Dados do usuário não encontrados. Por favor, faça login novamente.', 'danger')
        session.pop('user_email', None)
        return redirect(url_for('login'))

@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("TelaLoading/Telaloading.html")

@app.route("/cadastro")
def cadastro():
    return render_template("Cadastrar_templates/cadastrar.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao")
    nascimento_str = request.form.get("nascimento")
    numero = request.form.get("numero")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento_str, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('cadastro'))
        
    try:
        data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
        if data_obj > datetime.now():
            flash("Erro: A data de nascimento não pode ser no futuro.", 'danger')
            return redirect(url_for('cadastro'))
    except ValueError:
        flash("Erro: A data de nascimento deve ser no formato DD/MM/AAAA.", 'danger')
        return redirect(url_for('cadastro'))

    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade,
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero
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
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

# --- Rota da API para Upload de Imagem (VERSÃO ROBUSTA COM LOGS) ---

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # 1. Segurança: Verificar se o usuário está logado
    if 'user_email' not in session:
        print("--- FALHA DE AUTENTICAÇÃO EM /upload_image: Usuário não está na sessão.")
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    # 2. Validação: Verificar se um arquivo foi enviado
    if 'file' not in request.files:
        print("--- FALHA DE UPLOAD EM /upload_image: 'file' não encontrado no request.")
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400

    user_email = session['user_email']
    
    try:
        # 3. Preparação do Arquivo
        file_content = file.read()
        file.seek(0) 

        safe_email = user_email.replace('@', '_').replace('.', '_')
        file_name = f"public/{safe_email}_{int(datetime.now().timestamp())}.jpg"

        print(f"--- INFO: Tentando upload do arquivo '{file_name}' para o bucket 'profile_images'.")

        # 4. Upload para o Supabase Storage
        supabase.storage.from_('profile_images').upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "false"}
        )

        print(f"--- SUCESSO: Upload para o Storage bem-sucedido.")

        # 5. Obtenção da URL Pública
        image_url = supabase.storage.from_('profile_images').get_public_url(file_name)
        print(f"--- INFO: URL pública obtida: {image_url}")

        # 6. Atualização do Banco de Dados
        sucesso, mensagem = update_user_profile_image(user_email, image_url)
        
        if not sucesso:
            print(f"--- ERRO DB: Falha ao atualizar a URL no banco de dados. Mensagem: {mensagem}")
            return jsonify({'success': False, 'message': f"Erro ao salvar no banco: {mensagem}"}), 500

        print(f"--- SUCESSO FINAL: Imagem do usuário {user_email} atualizada.")
        # 7. Retorno de Sucesso para o Frontend
        return jsonify({'success': True, 'image_url': image_url})

    except APIError as e:
        # Captura especificamente erros da API do Supabase (como violação de RLS)
        print(f"--- ERRO DE API SUPABASE EM /upload_image ---: Status: {e.status_code}, Mensagem: {e.message}")
        return jsonify({'success': False, 'message': f'Erro de permissão do servidor: {e.message}'}), e.status_code

    except Exception as e:
        # Captura todas as outras exceções
        print(f"--- ERRO CRÍTICO EM /upload_image ---: Tipo: {type(e).__name__}, Erro: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno do servidor ao processar a imagem.'}), 500

# --- Execução da Aplicação ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

