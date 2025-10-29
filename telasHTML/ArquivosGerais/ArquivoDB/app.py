import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image, update_user_profile
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename

load_dotenv()

# --- CONFIGURAÇÃO AJUSTADA PARA A SUA ESTRUTURA DE ARQUIVOS ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR agora aponta para a pasta que contém todas as outras (TelaDeUsuario, TelaInicial, etc.)
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..')) 

app = Flask(
    __name__,
    template_folder=BASE_DIR, # Continua apontando para a raiz para encontrar os HTMLs
    static_url_path='/assets' # Define um prefixo ÚNICO para arquivos estáticos
)
app.static_folder = BASE_DIR # Diz ao Flask que a pasta estática também é a raiz

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "minha_ultima_chave_secreta_agora_vai")

# --- ROTAS DA APLICAÇÃO (CÓDIGO ORIGINAL MANTIDO) ---

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
            return redirect(url_for('login'))
        user_data = check_user(email, senha)
        if user_data:
            session['user_email'] = user_data['email']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
    return render_template('telaDeLogin/telaLogin.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
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
            data_obj = None
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    data_obj = datetime.strptime(nascimento_str, fmt)
                    break
                except ValueError:
                    pass
            if data_obj is None:
                raise ValueError("Formato de data inválido")
            
            data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
        except ValueError:
            flash("Erro: A data de nascimento deve estar no formato AAAA-MM-DD ou DD/MM/AAAA.", 'danger')
            return redirect(url_for('cadastro'))
        
        senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
        sucesso, mensagem = register_user(
            nome=nome, 
            email=email, 
            senha_hash=senha_hash.decode('utf-8'), 
            cidade=cidade,
            posicao=posicao, 
            data_nasc=data_nascimento_iso, 
            numero=numero
        )
        
        if sucesso:
            session['user_email'] = email
            flash(mensagem, 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash(mensagem, 'danger')
            return redirect(url_for('cadastro'))
    
    return render_template("Cadastrar_templates/cadastrar.html")

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    lista_de_usuarios = get_all_users()
    return render_template("TelaInicial/TelaInicial.html", usuarios=lista_de_usuarios)

@app.route("/usuario")
def pagina_usuario():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    user_data = get_user_by_email(session['user_email'])
    return render_template("TelaDeUsuario/TelaUser.html", usuario=user_data)

@app.route("/editar_perfil", methods=['GET', 'POST'])
def editar_perfil():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_data = get_user_by_email(session['user_email'])
    
    if request.method == 'POST':
        update_data = {
            'nome': request.form.get('nome'),
            'cidade': request.form.get('cidade'),
            'posicao': request.form.get('posicao'),
            'numero_camisa': request.form.get('numero_camisa'),
            'numero': request.form.get('numero_telefone')
        }
        update_data = {k: v for k, v in update_data.items() if v}
        
        if update_data:
            sucesso = update_user_profile(session['user_email'], **update_data)
            if sucesso:
                flash('Perfil atualizado com sucesso!', 'success')
            else:
                flash('Erro ao atualizar perfil.', 'danger')
        else:
            flash('Nenhuma alteração foi feita.', 'info')
        
        return redirect(url_for('pagina_usuario'))
    
    return render_template("TelaDeUsuario/editar_perfil.html", usuario=user_data)

# --- INÍCIO DO CÓDIGO ADICIONADO PARA CORRIGIR O ERRO ---

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Rota para lidar com o upload da imagem de perfil."""
    if 'user_email' not in session:
        return jsonify({'error': 'Não autorizado'}), 401

    if 'profile_image' not in request.files:
        flash('Nenhum arquivo de imagem foi enviado.', 'danger')
        return redirect(url_for('editar_perfil'))

    file = request.files['profile_image']

    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'warning')
        return redirect(url_for('editar_perfil'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Salva a imagem na pasta de onde o app está rodando (ex: 'src/uploads/profile_pics')
        upload_folder = os.path.join(APP_DIR, 'uploads', 'profile_pics')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # O caminho salvo no banco será relativo à pasta 'src', ex: 'uploads/profile_pics/foto.jpg'
        relative_path = os.path.join('uploads', 'profile_pics', filename).replace("\\", "/")
        
        sucesso = update_user_profile_image(session['user_email'], relative_path)
        if sucesso:
            flash('Imagem de perfil atualizada com sucesso!', 'success')
        else:
            flash('Erro ao salvar o caminho da imagem no banco de dados.', 'danger')
        
        return redirect(url_for('pagina_usuario'))
    else:
        flash('Formato de arquivo inválido! Use PNG, JPG, JPEG ou GIF.', 'danger')
        return redirect(url_for('editar_perfil'))

# --- FIM DO CÓDIGO ADICIONADO ---

@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # O template correto parece ser com 'l' minúsculo, como no seu primeiro código
    return render_template('TelaLoading/Telaloading.html') 

@app.route("/logout")
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    return render_template("RecuperarSenha/esqueci_senha.html")

@app.route("/chat/<int:destinatario_id>")
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("TelaChat/chat.html", destinatario_id=destinatario_id)

@app.route("/feed")
def pagina_feed():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("TelaFeed/feed.html")

# Rota para servir arquivos estáticos (MANTIDA E AJUSTADA)
# Agora ela responde em /assets/caminho/para/o/arquivo.css
@app.route('/assets/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
