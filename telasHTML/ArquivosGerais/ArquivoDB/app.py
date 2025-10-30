import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
# Assumindo a importação correta de todas as funções do database.py
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image, update_user_profile, get_user_by_id
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Assumindo que a estrutura é /project/src/app.py e os assets em /project/telasHTML/...
# Ajuste o BASE_DIR para apontar para a raiz do projeto se 'telasHTML' estiver em um nível acima.
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..', '..')) 

app = Flask(
    __name__,
    template_folder=BASE_DIR
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_padrao_para_dev")

# Diretório para uploads de fotos de perfil (dentro do caminho que será servido)
UPLOAD_FOLDER_RELATIVE = 'telasHTML/ArquivosGerais/TelaDeUsuario/imagens/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === ROTAS DEDICADAS PARA ARQUIVOS ESTÁTICOS ===
# 1. Rota para os assets da tela de Login
@app.route('/login-assets/<path:filename>')
def login_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'telaDeLogin')
    return send_from_directory(dir_path, filename)

# 2. Rota para os assets da Tela de Loading
@app.route('/loading-assets/<path:filename>')
def loading_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaLoading')
    return send_from_directory(dir_path, filename)

# 3. Rota para os assets da tela de Cadastro
@app.route('/cadastro-assets/<path:filename>')
def cadastro_assets(filename):
    # O caminho deve apontar para o diretório que contém 'estilo.css'
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'Cadastrar_templates')
    return send_from_directory(dir_path, filename)

# 4. Rota para os assets da Tela Inicial
@app.route('/inicio-assets/<path:filename>')
def inicio_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaInicial')
    return send_from_directory(dir_path, filename)

# 5. Rota para os assets da Tela de Usuário e Edição
@app.route('/user-assets/<path:filename>')
def user_assets(filename):
    # Usando o mesmo endpoint para servir arquivos da Tela de Usuário e relacionados
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaDeUsuario')
    return send_from_directory(dir_path, filename)
    
# 6. Rota para os assets do Feed
@app.route('/feed-assets/<path:filename>')
def feed_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaFeed')
    return send_from_directory(dir_path, filename)
    
# 7. Rota para os assets de Chat
@app.route('/chat-assets/<path:filename>')
def chat_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaChat')
    return send_from_directory(dir_path, filename)
    
# 8. Rota para os assets de Recuperação de Senha
@app.route('/recuperar-senha-assets/<path:filename>')
def recuperar_senha_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'RecuperarSenha')
    return send_from_directory(dir_path, filename)


# === ROTAS DO APLICATIVO ===

@app.route("/")
@app.route("/login")
def login():
    # Renderiza a tela de login
    return render_template('telasHTML/ArquivosGerais/telaDeLogin/telaLogin.html')

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cidade = request.form['cidade']
        posicao = request.form['posicao']
        nascimento_str = request.form['nascimento']
        numero = request.form['numero']
        
        # Lógica de validação de data
        try:
            # Tenta converter DD/MM/AAAA para AAAA-MM-DD
            try:
                nascimento = datetime.strptime(nascimento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                # Tenta AAAA-MM-DD
                nascimento = datetime.strptime(nascimento_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            flash('Formato de data inválido. Use DD/MM/AAAA ou AAAA-MM-DD.', 'danger')
            return redirect(url_for('cadastro'))

        if register_user(nome, email, senha, cidade, posicao, nascimento, numero):
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao cadastrar usuário. O e-mail pode já estar em uso.', 'danger')
            return redirect(url_for('cadastro'))
    
    # Rota GET para /cadastro
    return render_template('telasHTML/ArquivosGerais/Cadastrar_templates/cadastrar.html')


@app.route("/pagina_inicial")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
        
    usuarios = get_all_users()
    
    return render_template("telasHTML/ArquivosGerais/TelaInicial/TelaInicial.html", usuarios=usuarios)


@app.route("/pagina_usuario")
def pagina_usuario():
    if 'user_email' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
        
    user_email = session['user_email']
    usuario = get_user_by_email(user_email)
    
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('login'))
        
    return render_template("telasHTML/ArquivosGerais/TelaDeUsuario/TelaUser.html", usuario=usuario)


@app.route("/login", methods=['POST'])
def fazer_login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    if check_user(email, senha):
        session['user_email'] = email
        flash('Login bem-sucedido!', 'success')
        return redirect(url_for('tela_de_loading'))
    else:
        flash('Email ou senha inválidos.', 'danger')
        return redirect(url_for('login'))


@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('telasHTML/ArquivosGerais/TelaLoading/Telaloading.html') 


@app.route("/logout")
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('login'))


@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    # Rota para recuperar a senha. O POST enviaria o e-mail.
    return render_template("telasHTML/RecuperarSenha/esqueci_senha.html")


@app.route("/chat/<int:destinatario_id>")
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    remetente_email = session['user_email']
    remetente = get_user_by_email(remetente_email)
    destinatario = get_user_by_id(destinatario_id)
    
    if not remetente or not destinatario:
        flash('Erro: Remetente ou destinatário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    return render_template("telasHTML/ArquivosGerais/TelaChat/chat.html", remetente=remetente, destinatario=destinatario)


@app.route("/editar_perfil", methods=['GET', 'POST'])
def editar_perfil():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session['user_email']
    usuario = get_user_by_email(user_email)

    if request.method == 'POST':
        # Verifica se o arquivo de imagem de perfil foi enviado
        if 'profile_image' in request.files and request.files['profile_image'].filename != '':
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                # Cria um nome seguro e único para o arquivo
                filename = secure_filename(file.filename)
                
                # Define o caminho completo para salvar
                upload_dir = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Salva o caminho relativo no banco de dados
                profile_image_url = os.path.join(UPLOAD_FOLDER_RELATIVE, filename).replace(os.path.sep, '/')
                update_user_profile_image(user_email, profile_image_url)
                
                flash('Foto de perfil atualizada com sucesso!', 'success')
            else:
                flash('Formato de arquivo inválido! Use PNG, JPG, JPEG ou GIF.', 'danger')
                return redirect(url_for('editar_perfil'))

        # Lógica para atualizar outros dados do perfil
        update_data = {}
        if 'nome' in request.form and request.form['nome'] != usuario['nome']:
            update_data['nome'] = request.form['nome']
        if 'cidade' in request.form and request.form['cidade'] != usuario['cidade']:
            update_data['cidade'] = request.form['cidade']
        if 'posicao' in request.form and request.form['posicao'] != usuario['posicao']:
            update_data['posicao'] = request.form['posicao']
        if 'numero_camisa' in request.form and request.form['numero_camisa'] != str(usuario['numero_camisa']):
            try:
                camisa = int(request.form['numero_camisa'])
                update_data['numero_camisa'] = camisa
            except ValueError:
                 flash('Número da camisa deve ser um número inteiro.', 'danger')
                 return redirect(url_for('editar_perfil'))

        if update_data:
            update_user_profile(user_email, **update_data)
            flash('Perfil atualizado com sucesso!', 'success')
        
        return redirect(url_for('pagina_usuario'))

    # Rota GET
    return render_template("telasHTML/ArquivosGerais/TelaDeUsuario/editar_perfil.html", usuario=usuario)

@app.route("/feed")
def pagina_feed():
    if 'user_email' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
        
    return render_template("telasHTML/ArquivosGerais/TelaFeed/feed.html")


# API ENDPOINT (Placeholder)
@app.route("/api/posts", methods=['GET'])
def api_posts():
    # Exemplo de dados de posts (mock)
    mock_posts = [
        {
            "id": 1, 
            "author_id": 101, 
            "author_name": "Gabriel Diniz", 
            "author_avatar": url_for('user_assets', filename='imagens/user-icon-placeholder.png'),
            "content": "Grande vitória hoje! O time jogou demais. #futebol #vitoria",
            "image_url": None, # Sem imagem neste post
            "likes": 5, 
            "comments": 2,
            "timestamp": "2 minutos atrás"
        },
        {
            "id": 2, 
            "author_id": 102, 
            "author_name": "Maria Silva", 
            "author_avatar": url_for('user_assets', filename='imagens/user-icon-placeholder.png'),
            "content": "Novo uniforme para a próxima temporada! O que acharam?",
            "image_url": url_for('user_assets', filename='imagens/WallpaperTest.jpg'), # Exemplo de imagem
            "likes": 12, 
            "comments": 4,
            "timestamp": "1 hora atrás"
        }
    ]
    return jsonify(mock_posts)


if __name__ == '__main__':
    # Configurado para ser acessível em '0.0.0.0' para ambientes de deploy como o Render
    app.run(debug=True, host='0.0.0.0')