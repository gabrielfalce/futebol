import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
# Importa todas as funções necessárias do database.py
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image, update_user_profile
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS # Importa o Flask-CORS

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS CRÍTICA E SIMPLIFICADA ===
# O app.py está em: ProjectRoot/telasHTML/ArquivosGerais/ArquivoDB/app.py

APP_DIR = os.path.dirname(os.path.abspath(__file__)) # .../ArquivoDB

# TEMPLATES_DIR é a pasta um nível acima: .../telasHTML/ArquivosGerais
TEMPLATES_DIR = os.path.abspath(os.path.join(APP_DIR, '..'))

# BASE_DIR (ProjectRoot) é 3 níveis acima: .../futebol-1
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..', '..'))

app = Flask(
    __name__,
    # CONFIGURAÇÃO FINAL: Flask procurará templates DENTRO de 'telasHTML/ArquivosGerais'
    template_folder=TEMPLATES_DIR
)
CORS(app) # Habilita CORS para o aplicativo Flask (bom para produção)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")


# === ROTAS DEDICADAS PARA ARQUIVOS ESTÁTICOS (Assets) ===
# Todas as rotas agora usam TEMPLATES_DIR como base para os assets que estão dentro.

# 1. Rota para os assets da tela de Login (telasHTML/ArquivosGerais/telaDeLogin/)
@app.route('/login-assets/<path:filename>')
def login_assets(filename):
    dir_path = os.path.join(TEMPLATES_DIR, 'telaDeLogin')
    return send_from_directory(dir_path, filename)

# 2. Rota para os assets da Tela de Loading (telasHTML/ArquivosGerais/TelaLoading/)
@app.route('/loading-assets/<path:filename>')
def loading_assets(filename):
    dir_path = os.path.join(TEMPLATES_DIR, 'TelaLoading')
    return send_from_directory(dir_path, filename)

# 3. Rota para os assets da TELA INICIAL (telasHTML/ArquivosGerais/TelaInicial/)
@app.route('/inicio-assets/<path:filename>')
def inicio_assets(filename):
    dir_path = os.path.join(TEMPLATES_DIR, 'TelaInicial')
    return send_from_directory(dir_path, filename)

# 4. Rota para os assets da TELA DE CADASTRO (telasHTML/ArquivosGerais/Cadastrar_templates/)
@app.route('/cadastro-assets/<path:filename>')
def cadastro_assets(filename):
    # ATENÇÃO: Verifique se esta pasta está 'Cadastrar_templates' ou 'cadastrar_templates' no servidor!
    dir_path = os.path.join(TEMPLATES_DIR, 'Cadastrar_templates')
    return send_from_directory(dir_path, filename)

# 5. Rota para os assets de Recuperação de Senha (telasHTML/ArquivosGerais/RecuperarSenha/)
@app.route('/senha-assets/<path:filename>')
def senha_assets(filename):
    dir_path = os.path.join(TEMPLATES_DIR, 'RecuperarSenha')
    return send_from_directory(dir_path, filename)

# 6. Rota para os arquivos de UPLOAD de usuários (uploads/ profile_pics)
@app.route('/uploads/<path:path_and_filename>')
def uploaded_files(path_and_filename):
    # O diretório de uploads deve estar na raiz do projeto (BASE_DIR)
    dir_path = os.path.join(BASE_DIR, 'uploads')
    return send_from_directory(dir_path, path_and_filename)


# === FUNÇÕES HELPER ===

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'profile_pics')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === ROTAS DA APLICAÇÃO (render_template CORRIGIDO) ===

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
        
        user = check_user(email, senha)
        
        if user:
            session['user_email'] = user['email']
            session['user_name'] = user['nome']
            session['user_id'] = user['id']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            # Permanece na página de login
    
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template('telaDeLogin/telaLogin.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        # Formato de data de nascimento: DD/MM/AAAA. Precisa converter para AAAA-MM-DD
        data_nasc_str = request.form.get('nascimento')
        numero = request.form.get('numero')

        try:
            # Converte a data de DD/MM/AAAA para AAAA-MM-DD (formato do Supabase/SQL)
            data_nasc_obj = datetime.strptime(data_nasc_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            flash('Formato de data de nascimento inválido. Use DD/MM/AAAA.', 'danger')
            return redirect(url_for('cadastro'))

        # Hash da senha
        senha_hash_bytes = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        senha_hash = senha_hash_bytes.decode('utf-8')
        
        sucesso, mensagem = register_user(nome, email, senha_hash, cidade, posicao, data_nasc_obj, numero)
        
        if sucesso:
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Erro no cadastro: {mensagem}', 'danger')
            
    # CORREÇÃO CRÍTICA: Path relativo a telasHTML/ArquivosGerais/.
    # Mantenha a capitalização exata da sua pasta aqui: 'Cadastrar_templates' ou 'cadastrar_templates'
    return render_template("Cadastrar_templates/cadastrar.html")


@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    lista_de_usuarios = get_all_users()
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template("TelaInicial/TelaInicial.html", usuarios=lista_de_usuarios)


@app.route("/usuario")
def pagina_usuario():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    user_data = get_user_by_email(session['user_email'])
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template("TelaDeUsuario/TelaUser.html", usuario=user_data)


@app.route("/editar_perfil", methods=['GET', 'POST'])
def editar_perfil():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_data = get_user_by_email(session['user_email'])
    
    if request.method == 'POST':
        # Dados do formulário
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        data_nasc_str = request.form.get('nascimento')
        numero = request.form.get('numero')
        
        update_data = {}
        
        if nome and nome != user_data.get('nome'):
            update_data['nome'] = nome
        if cidade and cidade != user_data.get('cidade'):
            update_data['cidade'] = cidade
        if posicao and posicao != user_data.get('posicao'):
            update_data['posicao'] = posicao
        if numero and numero != user_data.get('numero'):
            update_data['numero'] = numero

        # Lógica de atualização da data de nascimento (conversão DD/MM/AAAA -> YYYY-MM-DD)
        if data_nasc_str:
            try:
                # O usuário pode enviar a data no formato 'DD/MM/AAAA'
                data_nasc_obj = datetime.strptime(data_nasc_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                if data_nasc_obj != user_data.get('nascimento'):
                    update_data['nascimento'] = data_nasc_obj
            except ValueError:
                flash('Formato de data inválido. Use DD/MM/AAAA.', 'danger')
                return redirect(url_for('editar_perfil'))
        
        if update_data:
            if update_user_profile(session['user_email'], **update_data):
                flash('Perfil atualizado com sucesso!', 'success')
                return redirect(url_for('pagina_usuario'))
            else:
                flash('Erro ao atualizar o perfil.', 'danger')
                return redirect(url_for('editar_perfil'))

    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template("TelaDeUsuario/editar_perfil.html", usuario=user_data)


@app.route("/upload_profile_image", methods=['POST'])
def upload_profile_image():
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    if 'profile_image' not in request.files:
        flash('Nenhum arquivo enviado.', 'danger')
        return redirect(url_for('editar_perfil'))

    file = request.files['profile_image']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('editar_perfil'))

    if file and allowed_file(file.filename):
        # Gera um nome de arquivo seguro e único
        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = secure_filename(f"{session['user_id']}_{timestamp}.{ext}")
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        
        # Caminho relativo para salvar no DB e usar na rota /uploads
        relative_path = os.path.join('profile_pics', new_filename).replace('\\', '/')
        
        sucesso = update_user_profile_image(session['user_email'], relative_path)
        if sucesso:
            flash('Imagem de perfil atualizada com sucesso!', 'success')
        else:
            flash('Erro ao salvar o caminho da imagem no banco de dados.', 'danger')
        
        return redirect(url_for('pagina_usuario'))
    else:
        flash('Formato de arquivo inválido! Use PNG, JPG, JPEG ou GIF.', 'danger')
        return redirect(url_for('editar_perfil'))


@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template('TelaLoading/Telaloading.html')


@app.route("/logout")
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('login'))


@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template("RecuperarSenha/esqueci_senha.html")


@app.route("/chat/<int:destinatario_id>")
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template("TelaChat/chat.html", destinatario_id=destinatario_id)


@app.route("/feed")
def pagina_feed():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # CORREÇÃO: Path relativo a telasHTML/ArquivosGerais/
    return render_template("TelaFeed/feed.html")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)