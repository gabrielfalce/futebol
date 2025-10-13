# No arquivo app.py (seu app (7).py)

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import inserir_usuario, buscar_usuarios # Atenção: seu database.py usa 'inserir_usuario' e 'buscar_usuarios'
import bcrypt

# --- CORREÇÃO ROBUSTA DE PATHS ---
# Sobe dois níveis (../..) a partir de 'telasHTML/ArquivosGerais/ArquivoDB' para chegar em 'telasHTML/ArquivosGerais'
# O path 'project_root' DEVE apontar para a pasta que contém as pastas de templates e arquivos estáticos.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 

app = Flask(
    __name__,
    # template_folder agora é 'telasHTML/ArquivosGerais'
    template_folder=project_root, 
    # A pasta estática é 'telasHTML/ArquivosGerais/STATIC' (ou onde seus estáticos estiverem)
    # **Baseado nas suas pastas, vou assumir que a pasta STATIC é a 'ArquivosGerais' em si ou você moveu.**
    # Se a pasta 'STATIC' não existir, o Flask procura os arquivos dentro de 'template_folder'.
    # Vou manter a configuração do seu app (7).py, mas garantir que o render_template está certo.
    static_folder=os.path.join(project_root, 'STATIC'), 
    static_url_path='/static'
)
app.secret_key = 'sua-chave-secreta-para-main'

# ...

@app.route("/")
def index():
    # CORREÇÃO: Remova o espaço da pasta Cadastrar templates
    # O arquivo correto é 'Cadastrar templates/cadastrar.html' (mas precisa ser renomeado)
    # Se você já renomeou a pasta no seu branch para 'Cadastrar_templates':
    return render_template("Cadastrar_templates/cadastrar.html")
    # Caso você NÃO possa renomear a pasta, use o caminho da estrutura:
    # return render_template("STATIC/Cadastrar templates/cadastrar.html") 
    # **A ÚNICA MANEIRA DE CORRIGIR O TEMPLATENOTFOUND É RENOMEAR A PASTA OU TIRAR O ESPAÇO DA CHAMADA.**

# VOU ASSUMIR QUE VOCÊ VAI RENOMEAR A PASTA NO GITHUB PARA 'Cadastrar_templates'

# ... (Rotas /loading e /inicio)

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    # ... (toda a lógica de POST está OK no seu app (7).py) ...

    # O POST retorna para a tela de index (que renderiza a página de cadastro em caso de erro)
    # Também precisa usar o nome da pasta corrigido, ou renomeá-la
    # return redirect(url_for('index')) # Se falhar, o index renderiza o template

    # Para ser mais explícito, em caso de erro de validação:
    if not sucesso:
        flash("Erro ao salvar no banco de dados. Verifique se o e-mail já foi cadastrado.")
        # CHAME O TEMPLATE CORRIGIDO NOVAMENTE
        return render_template("Cadastrar_templates/cadastrar.html")

    return redirect(url_for('tela_de_loading')) # Se sucesso

# ... (restante do código) ...
