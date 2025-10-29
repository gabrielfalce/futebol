import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from dotenv import load_dotenv
from database import register_user, check_user, get_all_users, get_user_by_email, update_user_profile_image
import bcrypt
from datetime import datetime

load_dotenv()

# --- CONFIGURAÇÃO PADRÃO E ROBUSTA DO FLASK ---
# O app.py está em '.../ArquivoDB'.
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# A pasta que contém TUDO (templates e assets) é a 'ArquivosGerais'.
# Ela está um nível acima do app.py.
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, '..'))

app = Flask(
    __name__,
    template_folder=BASE_DIR,  # Define 'ArquivosGerais' como a pasta de templates
    static_folder=BASE_DIR,    # Define a mesma 'ArquivosGerais' como a pasta de arquivos estáticos
    static_url_path='/static'  # A URL para os assets será, por exemplo, /static/TelaDeLogin/style.css
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "minha_ultima_chave_secreta_agora_vai")

# --- ROTAS DA APLICAÇÃO ---
# Os caminhos dentro de render_template() são relativos à pasta 'ArquivosGerais'.

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
    # O Flask vai procurar 'TelaDeLogin/telaLogin.html' dentro da pasta 'ArquivosGerais'
    return render_template('TelaDeLogin/telaLogin.html')

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
            # Tenta múltiplos formatos de data
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

@app.route("/loading")
def tela_de_loading():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('TelaLoading/Telaloading.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('Sessão encerrada com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route("/esqueci_senha", methods=['GET', 'POST'])
def esqueci_senha():
    # Adicione a lógica de POST aqui se necessário
    return render_template("RecuperarSenha/esqueci_senha.html")

@app.route("/chat/<int:destinatario_id>")
def pagina_chat(destinatario_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # Adicione a lógica para buscar dados do usuário aqui
    return render_template("TelaChat/chat.html", destinatario_id=destinatario_id)

@app.route("/feed")
def pagina_feed():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template("TelaFeed/feed.html")

# Rota para editar perfil (exemplo)
@app.route("/editar_perfil")
def editar_perfil():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # Aqui você renderizaria um template de edição
    return "Página de Edição de Perfil (a ser criada)"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
