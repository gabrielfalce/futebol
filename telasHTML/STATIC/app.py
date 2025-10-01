# Localização: telasHTML/STATIC/app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import inserir_usuario 

# --- Configuração do Flask (sem alterações) ---
project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, '..')
static_dir = project_root

app = Flask(
    __name__, 
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path=''
)
app.secret_key = 'uma-chave-secreta-muito-segura-pode-mudar-depois'

# --- Rotas da Aplicação ---

@app.route("/")
def index():
    return render_template("STATIC/Cadastrar templates/cadastrar.html")

@app.route("/loading")
def tela_de_loading():
    return render_template("TelaLoading.html")

@app.route("/inicio")
def pagina_inicial():
    return render_template("TelaInicial.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    """Processa os dados do formulário de cadastro."""
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")
    cidade = request.form.get("cidade")
    posicao = request.form.get("posicao") 
    nascimento = request.form.get("nascimento") 
    numero = request.form.get("numero") 

    # --- VALIDAÇÃO MELHORADA ---
    # Vamos verificar todos os campos e ser mais específicos.
    campos_obrigatorios = {
        "Nome": nome, "Email": email, "Senha": senha, 
        "Cidade": cidade, "Posição": posicao, "Nascimento": nascimento, "Número": numero
    }
    
    campos_vazios = [nome_campo for nome_campo, valor in campos_obrigatorios.items() if not valor]

    if campos_vazios:
        # Imprime uma mensagem de erro detalhada nos logs
        print(f"ERRO DE VALIDAÇÃO: Os seguintes campos estão vazios: {', '.join(campos_vazios)}")
        
        # Envia uma mensagem de erro mais útil para o usuário
        mensagem_erro = f"Erro no cadastro: O(s) campo(s) {', '.join(campos_vazios)} é/são obrigatório(s)."
        flash(mensagem_erro)
        
        return redirect(url_for('index'))

    # Se a validação passar, tenta inserir no banco
    sucesso = inserir_usuario(
        nome=nome, email=email, senha=senha, cidade=cidade, 
        posicao=posicao, nascimento=nascimento, numero=numero
    )

    if sucesso:
        return redirect(url_for('tela_de_loading'))
    else:
        flash("Erro ao salvar no banco de dados. Tente novamente mais tarde.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
