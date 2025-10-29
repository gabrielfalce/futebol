import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from dotenv import load_dotenv
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image
import bcrypt
from datetime import datetime
from jinja2.exceptions import TemplateNotFound

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO DE CAMINHOS PARA RENDER COM ROOT DIRECTORY ---
# Esta lógica foi feita especificamente para a sua configuração no Render,
# onde o "Root Directory" é 'telasHTML/ArquivosGerais/ArquivoDB'.
try:
    # O __file__ se refere a este arquivo (app.py), que está dentro de 'ArquivoDB'
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Para encontrar a pasta 'telasHTML', precisamos "subir" dois níveis de diretório:
    # 1. De 'ArquivoDB' para 'ArquivosGerais'
    # 2. De 'ArquivosGerais' para 'telasHTML'
    TEMPLATE_DIR = os.path.abspath(os.path.join(APP_DIR, '..', '..'))

    # Uma verificação para garantir que o caminho encontrado está correto
    if not os.path.isdir(TEMPLATE_DIR) or 'telasHTML' not in os.path.basename(TEMPLATE_DIR):
         raise FileNotFoundError("Lógica de subida de diretório falhou em encontrar 'telasHTML'.")

except Exception as e:
    print(f"Erro crítico ao configurar os caminhos: {e}")
    # Em um ambiente de produção, é crucial parar a execução se os caminhos estiverem errados.
    raise

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=None  # Desativamos o 'static' padrão, pois usaremos nossa própria rota.
)

# Configura a chave secreta a partir de variáveis de ambiente para segurança
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "uma_chave_padrao_para_desenvolvimento_local")


# --- ROTA DE ARQUIVOS ESTÁTICOS (UNIVERSAL) ---
# Serve qualquer arquivo (CSS, JS, imagem) de qualquer subpasta dentro de 'telasHTML'
@app.route('/assets/<path:filename>')
def assets(filename):
    # Por segurança, verificamos se o caminho não tenta "subir" diretórios com '..'
    if '..' in filename or filename.startswith('/'):
        return "Caminho inválido", 400
    return send_from_directory(TEMPLATE_DIR, filename)


# --- ROTAS DA APLICAÇÃO ---

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

    return render_template('ArquivosGerais/TelaDeLogin/telaLogin.html')

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
            data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
            data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
        except ValueError:
            flash("Erro: A data de nascimento deve estar no formato DD/MM/AAAA.", 'danger')
            return redirect(url_for('cadastro'))

        senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())
        sucesso, mensagem = register_user(
            nome=nome, email=email, senha_hash=senha_hash.decode('utf-8'), cidade=cidade,
            posicao=posicao, data_nasc=data_nascimento_iso, numero=numero
        )

        if sucesso:
            session['user_email'] = email
            flash(mensagem, 'success')
            return redirect(url_for('tela_de_loading'))
        else:
            flash(mensagem, 'danger')
            return redirect(url_for('cadastro'))

    return render_template("ArquivosGerais/Cadastrar_templates/cadastrar.html")

@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    try:
        lista_de_usuarios = get_all_users()
        return render_template("ArquivosGerais/TelaInicial/TelaInicial.html", usuarios=lista_de_usuarios)
    except Exception as e:
        flash(f'Ocorreu um erro ao carregar os usuários: {e}', 'danger')
        return render_template("ArquivosGerais/TelaInicial/TelaInicial.html", usuarios=[])

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
        session.clear()
        return redirect(url_for('login'))

@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('ArquivosGerais/TelaLoading/Telaloading.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route("/esqueci_senha")
def esqueci_senha():
    return render_template("ArquivosGerais/RecuperarSenha/esqueci_senha.html")

@app.route("/chat/<int:destinatario_id>")
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("ArquivosGerais/TelaChat/chat.html", destinatario_id=destinatario_id)

@app.route("/feed")
def pagina_feed():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("ArquivosGerais/TelaFeed/feed.html")

# --- Ponto de Execução da Aplicação ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
