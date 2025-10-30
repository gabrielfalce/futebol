import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from dotenv import load_dotenv
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image, update_user_profile, get_user_by_id
import bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename

load_dotenv()

# === CONFIGURAÇÃO DE DIRETÓRIOS ===
# CORREÇÃO: Ajustando BASE_DIR para o nível superior onde 'telasHTML' e 'app.py' estão.
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
UPLOAD_FOLDER = os.path.join(BASE_DIR, UPLOAD_FOLDER_RELATIVE)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === ROTAS DEDICADAS PARA ARQUIVOS ESTÁTICOS ===
# Rotas dedicadas para servir estáticos de pastas específicas

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

# 3. Rota para os assets da Tela Inicial
@app.route('/inicio-assets/<path:filename>')
def inicio_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaInicial')
    return send_from_directory(dir_path, filename)
    
# 4. Rota para os assets da Tela de Cadastro
@app.route('/cadastro-assets/<path:filename>')
def cadastro_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'Cadastrar_templates')
    return send_from_directory(dir_path, filename)

# 5. Rota para os assets da Tela de Recuperação de Senha
@app.route('/recuperar-assets/<path:filename>')
def recuperar_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'RecuperarSenha')
    return send_from_directory(dir_path, filename)

# 6. Rota para os assets da Tela do Usuário/Perfil e Edição/Chat
@app.route('/user-assets/<path:filename>')
def user_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaDeUsuario')
    return send_from_directory(dir_path, filename)

# 7. Rota para os assets do Feed
@app.route('/feed-assets/<path:filename>')
def feed_assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML', 'ArquivosGerais', 'TelaFeed')
    return send_from_directory(dir_path, filename)
    
# Rota Genérica de Assets (Fallback, pode ser usada para imagens de perfil/placeholder)
@app.route('/assets/<path:filename>')
def assets(filename):
    dir_path = os.path.join(BASE_DIR, 'telasHTML')
    return send_from_directory(dir_path, filename)
    
# Rota de Imagens de Perfil (Diretório de UPLOAD)
@app.route(f'/{UPLOAD_FOLDER_RELATIVE}/<path:filename>')
def uploaded_profile_pics(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# === ROTAS DO FLASK ===

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        user_data = check_user(email, senha)
        
        if user_data:
            session['user_email'] = user_data['email']
            session['user_id'] = user_data['id'] 
            session['user_name'] = user_data['nome'] 
            flash('Login realizado com sucesso! Aguarde o carregamento.', 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            
    # CORREÇÃO: Usando barras normais (/) no render_template
    return render_template('telasHTML/ArquivosGerais/telaDeLogin/telaLogin.html') 

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # CORREÇÃO: Ajustando a ordem dos campos de acordo com o database.py e cadastrar.html
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cidade = request.form.get('cidade')
        posicao = request.form.get('posicao')
        data_nasc_input = request.form.get('nascimento') # DD/MM/AAAA ou AAAA-MM-DD
        numero = request.form.get('numero') # Telefone
        
        # 1. Validação de formato de data e conversão para AAAA-MM-DD
        try:
            # Tenta converter DD/MM/AAAA
            if '/' in data_nasc_input:
                data_nasc_obj = datetime.strptime(data_nasc_input, '%d/%m/%Y').date()
            # Tenta converter AAAA-MM-DD
            elif '-' in data_nasc_input:
                data_nasc_obj = datetime.strptime(data_nasc_input, '%Y-%m-%d').date()
            else:
                flash('Formato de data de nascimento inválido. Use DD/MM/AAAA.', 'danger')
                return redirect(url_for('cadastro'))

            data_nasc = data_nasc_obj.isoformat() # Formato 'AAAA-MM-DD'

        except ValueError:
            flash('Data de nascimento inválida. Verifique o formato.', 'danger')
            return redirect(url_for('cadastro'))

        # 2. Hash da Senha
        senha_bytes = senha.encode('utf-8')
        salt = bcrypt.gensalt()
        senha_hash_bytes = bcrypt.hashpw(senha_bytes, salt)
        senha_hash = senha_hash_bytes.decode('utf-8') # Armazena como string

        # 3. Registro no Banco de Dados
        sucesso, mensagem = register_user(nome, email, senha_hash, cidade, posicao, data_nasc, numero)

        if sucesso:
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(mensagem, 'danger') 
            return redirect(url_for('cadastro'))

    # CORREÇÃO: Usando barras normais (/) no render_template
    return render_template('telasHTML/ArquivosGerais/Cadastrar_templates/cadastrar.html')

@app.route("/inicial")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
    
    # 1. Obter a lista de todos os usuários
    all_users = get_all_users()
    
    # 2. Obter os dados do usuário logado (para navegação ou contexto)
    current_user = get_user_by_email(session.get('user_email'))
    
    # 3. Filtrar para não mostrar o usuário logado na lista
    if current_user and all_users:
        all_users = [user for user in all_users if user['id'] != current_user['id']]
    
    # 4. Processar a URL da imagem de perfil para cada usuário
    for user in all_users:
        if user.get('foto_perfil'):
            # Cria a URL que aponta para a rota de upload
            user['profile_image_url'] = url_for('uploaded_profile_pics', filename=os.path.basename(user['foto_perfil']))
        else:
            # Placeholder
            user['profile_image_url'] = url_for('user_assets', filename='imagens/user-icon-placeholder.png')

    # CORREÇÃO: Trocado '\\' por '/' e passada a lista de usuários para o template
    return render_template('telasHTML/ArquivosGerais/TelaInicial/TelaInicial.html', users=all_users, current_user=current_user)

@app.route("/perfil")
def pagina_usuario():
    if 'user_email' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
        
    email = session['user_email']
    usuario = get_user_by_email(email)
    
    if not usuario:
        flash('Erro ao carregar dados do usuário.', 'danger')
        return redirect(url_for('logout'))

    # Processamento das URLs de Imagem
    if usuario.get('foto_perfil'):
        usuario['foto_perfil_url'] = url_for('uploaded_profile_pics', filename=os.path.basename(usuario['foto_perfil']))
    else:
        usuario['foto_perfil_url'] = url_for('user_assets', filename='imagens/user-icon-placeholder.png')

    if usuario.get('foto_capa'):
        usuario['foto_capa_url'] = url_for('user_assets', filename=usuario['foto_capa'])
    else:
        usuario['foto_capa_url'] = url_for('user_assets', filename='imagens/hM94BRC.jpeg')

    # CORREÇÃO: Usando barras normais (/)
    return render_template('telasHTML/ArquivosGerais/TelaDeUsuario/TelaUser.html', usuario=usuario)

@app.route("/perfil/editar", methods=['GET', 'POST'])
def editar_perfil():
    if 'user_email' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'danger')
        return redirect(url_for('login'))
    
    email = session['user_email']
    usuario = get_user_by_email(email)

    if not usuario:
        flash('Erro ao carregar dados do usuário.', 'danger')
        return redirect(url_for('logout'))
        
    if request.method == 'POST':
        update_data = {}
        campos = ['nome', 'cidade', 'posicao', 'numero_camisa', 'nascimento', 'numero']
        
        for campo in campos:
            valor = request.form.get(campo)
            if valor is not None:
                if campo == 'nascimento' and valor:
                    # CORREÇÃO: Converte a data do formulário (DD/MM/AAAA) para o formato do DB (AAAA-MM-DD)
                    try:
                        if '/' in valor:
                            data_nasc_obj = datetime.strptime(valor, '%d/%m/%Y').date()
                            update_data[campo] = data_nasc_obj.isoformat()
                        elif '-' in valor:
                            update_data[campo] = valor 
                        else:
                            flash('Formato de data de nascimento inválido. Use DD/MM/AAAA.', 'danger')
                            return redirect(url_for('editar_perfil'))

                    except ValueError:
                        flash('Formato de data de nascimento inválido. Use DD/MM/AAAA.', 'danger')
                        return redirect(url_for('editar_perfil'))

                # Se for outro campo e o valor tiver mudado
                elif campo != 'nascimento' and str(usuario.get(campo)) != valor:
                    update_data[campo] = valor

        if update_data:
            sucesso = update_user_profile(email, **update_data)
            if sucesso:
                flash('Perfil atualizado com sucesso!', 'success')
            else:
                flash('Erro ao atualizar o perfil. Tente novamente.', 'danger')
        else:
            flash('Nenhuma alteração detectada.', 'info')

        return redirect(url_for('pagina_usuario'))

    # CORREÇÃO: Trocado '\\' por '/' e passado o objeto 'usuario'
    return render_template('telasHTML/ArquivosGerais/TelaDeUsuario/editar_perfil.html', usuario=usuario)

@app.route("/upload_profile_image", methods=['POST'])
def upload_profile_image():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    if 'profile_image' not in request.files:
        flash('Nenhum arquivo enviado.', 'danger')
        return redirect(url_for('editar_perfil'))
        
    file = request.files['profile_image']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('editar_perfil'))

    if file and allowed_file(file.filename):
        # Cria um nome seguro e único para o arquivo
        filename = secure_filename(f"{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            flash('Erro interno ao salvar a imagem.', 'danger')
            return redirect(url_for('editar_perfil'))

        # Caminho relativo que será salvo no DB
        relative_path = os.path.join(UPLOAD_FOLDER_RELATIVE, filename).replace('\\', '/')
        
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
    # CORREÇÃO: Usando barras normais (/)
    return render_template('telasHTML/ArquivosGerais/TelaLoading/Telaloading.html') 

@app.route("/logout")
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    # TODO: Implementar lógica de envio de e-mail de recuperação
    if request.method == 'POST':
        email = request.form.get('email')
        if get_user_by_email(email):
            flash(f'Link de recuperação de senha enviado para {email}. (Funcionalidade de e-mail desabilitada)', 'success')
            return redirect(url_for('login'))
        else:
            flash('Este e-mail não está cadastrado.', 'danger')

    # CORREÇÃO: Usando barras normais (/)
    return render_template("telasHTML/RecuperarSenha/esqueci_senha.html")

@app.route("/redefinir_senha", methods=['GET', 'POST'])
def redefinir_senha():
    # Placeholder para a rota de formulário simples:
    if request.method == 'POST':
        # Senha seria atualizada aqui após validação de token
        flash('Senha redefinida com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    # CORREÇÃO: Usando barras normais (/)
    return render_template("telasHTML/RecuperarSenha/redefinir_senha.html")

@app.route("/chat/<int:destinatario_id>")
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    remetente = get_user_by_email(session.get('user_email'))
    if not remetente:
         flash('Erro ao carregar seu perfil.', 'danger')
         return redirect(url_for('logout'))

    destinatario = get_user_by_id(destinatario_id)
    
    if not destinatario:
        flash('Destinatário não encontrado.', 'danger')
        return redirect(url_for('pagina_inicial'))

    # Prepara a URL da imagem do destinatário
    if destinatario.get('foto_perfil'):
        destinatario['profile_image_url'] = url_for('uploaded_profile_pics', filename=os.path.basename(destinatario['foto_perfil']))
    else:
        destinatario['profile_image_url'] = url_for('user_assets', filename='imagens/user-icon-placeholder.png')


    # CORREÇÃO: Trocado '\\' por '/' e passada a info de remetente/destinatário
    return render_template(
        "telasHTML/ArquivosGerais/TelaChat/chat.html", 
        destinatario=destinatario,
        remetente=remetente
    )


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
            "image_url": url_for('feed_assets', filename='uniforme.jpg'), # Mock image
            "likes": 15, 
            "comments": 5,
            "timestamp": "1 hora atrás"
        }
    ]
    
    return jsonify(mock_posts)


if __name__ == "__main__":
    app.run(debug=True)