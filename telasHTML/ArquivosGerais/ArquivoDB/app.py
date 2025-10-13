import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import inserir_usuario, check_user, get_all_users # Funções Corretas
import bcrypt # Para hashing da senha
from datetime import datetime # NOVO: Importa para formatar a data

# --- Configuração de Caminhos e Flask ---

# Sobe um nível (..) do ArquivoDB para chegar em ArquivosGerais, que é a RAIZ dos templates
app_dir = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.abspath(os.path.join(app_dir, '..')) 

app = Flask(
    __name__,
    template_folder=template_root, # A raiz dos templates é 'ArquivosGerais'
    # Define a pasta STATIC dentro de ArquivosGerais
    static_folder=os.path.join(template_root, 'STATIC'), 
    static_url_path='/static'
)
app.secret_key = 'uma_chave_muito_secreta_e_dificil_de_adivinhar' # Chave para usar sessões e flash messages

# --- Rotas ---

# Rota principal (Cadastro)
@app.route("/")
def index():
    # Caminho corrigido para a pasta 'Cadastrar_templates' (com underscore)
    return render_template("Cadastrar_templates/cadastrar.html") 

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        # A função check_user cuida do hashing e comparação
        user_data = check_user(email, senha)
        
        if user_data:
            session['user_email'] = email
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('pagina_inicial'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
            
    # Caminho corrigido: 'TelaDeLogin/login.html'
    return render_template('TelaDeLogin/login.html') 


# Rota para a tela inicial
@app.route("/inicio")
def pagina_inicial():
    if 'user_email' not in session:
        flash('Você precisa fazer login para aceder a esta página.', 'warning')
        return redirect(url_for('login'))
        
    lista_de_usuarios = get_all_users()
    # Caminho corrigido: 'TelaInicial.html'
    return render_template("TelaInicial.html", usuarios=lista_de_usuarios)


# Rota de loading
@app.route("/loading")
def tela_de_loading():
    # Caminho corrigido: 'TelaLoading/Telaloading.html'
    return render_template("TelaLoading/Telaloading.html")


# Rota de cadastro (POST)
@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha_texto_puro = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento_str = request.form.get("nascimento") # Pega a data como string (DD/MM/AAAA)
    numero = request.form.get("numero")

    if not all([nome, email, senha_texto_puro, cidade, posicao, nascimento_str, numero]):
        flash("Erro no cadastro: Todos os campos são obrigatórios.", 'danger')
        return redirect(url_for('index'))
        
    # --- CORREÇÃO DA DATA DE NASCIMENTO ---
    try:
        # 1. Tenta interpretar a string como DD/MM/AAAA (formato brasileiro)
        data_obj = datetime.strptime(nascimento_str, '%d/%m/%Y')
        # 2. Converte o objeto datetime para o formato ISO AAAA-MM-DD
        data_nascimento_iso = data_obj.strftime('%Y-%m-%d')
    except ValueError:
        flash("Erro: O formato da data de nascimento deve ser dd/mm/aaaa.", 'danger')
        return redirect(url_for('index'))
    # --- FIM DA CORREÇÃO DA DATA ---


    # Hash da senha usando bcrypt
    senha_hash = bcrypt.hashpw(senha_texto_puro.encode('utf-8'), bcrypt.gensalt())

    sucesso, mensagem = inserir_usuario(
        nome=nome, email=email, senha_hash=senha_hash, cidade=cidade, 
        posicao=posicao, nascimento=data_nascimento_iso, numero=numero # Passa a data formatada
    )

    if sucesso:
        flash(mensagem, 'success')
        return redirect(url_for('login'))
    else:
        # Se falhar no Supabase (e-mail duplicado, etc.), a mensagem do database.py será usada
        flash(mensagem, 'danger')
        return redirect(url_for('index')) 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
