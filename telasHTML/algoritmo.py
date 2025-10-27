
quero que complemente esse codigo para ele fazer busca a partir do Id oferecido pelo supabase
pasted_content.txt
Texto · 4.04 KB
Lite
Recebi o arquivo e a sua solicitação. Vou analisar o código fornecido e complementá-lo para realizar a busca por ID usando o Supabase. Entrando no modo agente para iniciar a execução.
Novo conhecimento sugerido
Analisando o código, percebo que preciso inserir uma funcionalidade para buscar dados usando o ID do Supabase. Isso será implementado na próxima fase.

Identifiquei que a busca por ID no Supabase ainda não foi implementada. O próximo passo é criar uma rota que utilize o ID para consultar um usuário específico.

Criei a rota `search_user_by_id` para consultar usuário pelo ID no Supabase. Próximo passo é implementar a lógica de busca dentro dessa rota.

Lite
O código foi complementado com sucesso.
Adicionei a nova rota /search_user_by_id que aceita um user_id via método POST e utiliza o método .eq('id', user_id_int).single() do Supabase para buscar um único registro correspondente ao ID fornecido.
O arquivo app.py completo com a nova funcionalidade está anexado.
Nova Rota Implementada:
Python
# NOVA FUNCIONALIDADE: Busca usuário por ID
@app.route("/search_user_by_id", methods=["POST"])
def search_user_by_id():
    user_id = request.form.get("user_id")
    if user_id:
        try:
            # Tenta converter o ID para inteiro, pois IDs em bancos de dados costumam ser numéricos
            # Se o ID for uma string (UUID, por exemplo), remova a conversão para int()
            try:
                user_id_int = int(user_id)
            except ValueError:
                # Se não for um inteiro, assume que é uma string (como UUID)
                user_id_int = user_id 
                
            # Busca o usuário pelo ID. Usamos '.single()' para esperar um único resultado
            response = supabase.from_('users').select('*').eq('id', user_id_int).single().execute()
            
            # O '.data' do single() retorna o objeto diretamente, não uma lista.
            found_user = response.data
            
            # Colocamos o usuário encontrado em uma lista para manter a consistência com
            # outras rotas de busca no template (se necessário)
            searched_users_by_id = [found_user] if found_user else []

            return render_template("index.html", 
                                   searched_users_by_id=searched_users_by_id, 
                                   user_id=user_id,
                                   message=f"Usuário encontrado com ID: {user_id}" if found_user else f"Nenhum usuário encontrado com ID: {user_id}")
        except Exception as e:
            # Trata o erro de "No rows found" do .single() ou qualquer outro erro
            error_message = f"Erro ao buscar usuário por ID: {e}"
            if "No rows found" in str(e):
                 error_message = f"Nenhum usuário encontrado com ID: {user_id}"
                 return render_template("index.html", searched_users_by_id=[], user_id=user_id, error=error_message)
            return render_template("index.html", searched_users_by_id=[], user_id=user_id, error=error_message)
    return redirect(url_for("index"))
Observações:
Busca por ID: A função utiliza supabase.from_('users').select('*').eq('id', user_id_int).single().execute() para a busca. O método .eq('id', ...) filtra pelo ID, e o .single() garante que apenas um resultado (o esperado para uma busca por ID) seja retornado.
Tratamento de Erro: Foi incluído um tratamento de exceção específico para o caso em que nenhum usuário é encontrado, que é o erro No rows found retornado pela chamada .single().
Tipo de ID: Foi incluída uma conversão para int() com tratamento de erro, pois IDs são comumente numéricos. Se o seu ID for um UUID (string), a função continuará funcionando, pois a variável user_id_int manterá o valor string.
Você precisará adicionar um formulário em seu index.html para enviar o ID para a rota /search_user_by_id.
Exemplo de formulário no index.html:
HTML
<form method="POST" action="/search_user_by_id">
    <input type="text" name="user_id" placeholder="Digite o ID do Usuário">
    <button type="submit">Buscar por ID</button>
</form>
app.py
Código · 6.07 KB

Ver todos os arquivos nesta tarefa
<!-- Localização: telasHTML/TelaInicial.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App de Usuários</title>
    <!-- Usando url_for para garantir que os caminhos funcionem -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='iconeUser.png') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header class="barra-superior">
        <button class="menu-button">
            <img src="{{ url_for('static', filename='TresPontos.png') }}" alt="Menu">
        </button> 
        <div class="search-container">
            <input placeholder="Pesquisar" class="search-input" type="text">
            <img src="{{ url_for('static', filename='lupa.png') }}" alt="Ícone de pesquisa"> 
        </div>
    </header>

    <main class="content">
        <div id="usuarios-container">
            {% if usuarios %}
                {% for usuario in usuarios %}
                    <div class="usuario-card">
                        <img class="usuario-foto" src="{{ url_for('static', filename='iconeUser.png') }}" alt="Foto do usuário">
                        <div class="usuario-info">
                            <h3 class="usuario-nome">{{ usuario.nome }}</h3>
                            <p class="usuario-cidade">{{ usuario.cidade }}</p>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p>Nenhum usuário cadastrado ainda.</p>
            {% endif %}
        </div>
    </main>

    <div class="floating-button-container">
        <div class="floating-button-bar"></div>
        <button id="adicionarUsuarioBtn" class="floating-button">
            <img src="{{ url_for('static', filename='bolaLogo.png') }}" alt="Adicionar usuário">
        </button>
    </div>
    <div class="entadaUserBotao-container">
        <div class="entadaUserBotao-bar"></div>
        <button id="entadaUserBotao" class="entadaUserBotao-button">
            <a href="#"><img src="{{ url_for('static', filename='BotaoUsuario.ico') }}" alt="Botão Usuário"></a>
        </button>
    </div>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>

Tela inicial, muda para fazer isso que falou agora
A rota de busca por ID foi implementada, usando `.eq('id', valor).single()` para garantir um único resultado. Vou adicionar o formulário de pesquisa no HTML.

Adicionei os dois formulários de busca na `header`, ajustei para uma estrutura limpa, e organizei a exibição condicional dos resultados por ID e nome/email.

Incluí os formulários de busca na `header`, organizei a estrutura e configurei exibição condicional por ID e nome/email, preparando para modificar o HTML conforme o plano.

Lite
Perfeito! Eu entendi que você queria a integração da busca por ID também no seu arquivo HTML.
Eu fiz as seguintes modificações no seu arquivo telasHTML/TelaInicial.html (que renomeei para index.html e salvei na pasta templates para que o Flask possa renderizá-lo):
Adicionei o Formulário de Busca por ID na barra superior, ao lado do seu formulário de busca por nome/email, apontando para a nova rota /search_user_by_id.
Implementei a Lógica de Exibição de Resultados usando a sintaxe Jinja2 ({% if ... %}). Agora, a página verifica se há um resultado de busca por ID (searched_users_by_id) e o exibe com mais detalhes (incluindo ID e Email, que são úteis para a busca individual).
O novo código index.html está anexado.
Principais Alterações no index.html:
1. Formulário de Busca por ID (Linhas 18-24):
HTML
<div class="search-container">
    <!-- NOVO: Formulário de busca por ID -->
    <form method="POST" action="/search_user_by_id" style="display: flex; align-items: center; margin-right: 15px;">
        <input placeholder="Buscar por ID" class="search-input" type="text" name="user_id" style="width: 100px;">
        <button type="submit" style="background: none; border: none; padding: 0; cursor: pointer;">
            <img src="{{ url_for('static', filename='lupa.png') }}" alt="Ícone de pesquisa por ID" style="width: 20px; height: 20px; vertical-align: middle;"> 
        </button>
    </form>
    
    <!-- Formulário de busca por nome/email (mantido) -->
    <form method="POST" action="/search_user" style="display: flex; align-items: center;">
        <input placeholder="Pesquisar por Nome/Email" class="search-input" type="text" name="query_term">
        <!-- ... (botão de busca) ... -->
    </form>
</div>
2. Bloco de Exibição de Resultados (Linhas 45-57):
Este novo bloco prioriza a exibição do usuário encontrado pelo ID, mostrando inclusive o ID e Email, que são informações relevantes para a busca individual.
HTML
<div id="usuarios-container">
    {% if searched_users_by_id %}
        <h2>Resultado da Busca por ID</h2>
        {% for usuario in searched_users_by_id %}
            <div class="usuario-card">
                <!-- ... (outras tags) ... -->
                <div class="usuario-info">
                    <h3 class="usuario-nome">{{ usuario.nome }} (ID: {{ usuario.id }})</h3>
                    <p class="usuario-cidade">Cidade: {{ usuario.cidade }}</p>
                    <p class="usuario-email">Email: {{ usuario.email }}</p>
                    <!-- Adicione mais campos conforme necessário -->
                </div>
            </div>
        {% endfor %}
    {% elif searched_users %}
        <!-- ... (Lógica de exibição para busca por nome/email) ... -->
    {% elif usuarios %}
        <!-- ... (Lógica de exibição para todos os usuários) ... -->
    {% else %}
        <p>Nenhum usuário cadastrado ainda.</p>
    {% endif %}
</div>
Certifique-se de que o seu arquivo Python (app.py) esteja usando o nome de template index.html ao chamar render_template. Se você estava usando TelaInicial.html, você precisará renomear o arquivo no seu projeto ou ajustar as chamadas em app.py.
Se precisar de mais alguma alteração, é só me dizer!
Novo conhecimento sugerido
index.html
Código · 4.91 KB

Ver todos os arquivos nesta tarefa
Me de o arquivo todo com a carretção
Atualizei o `index.html` para incluir o formulário de busca por ID, enviando para `/search_user_by_id`. A exibição agora prioriza resultados de busca por ID, mostrando detalhes como ID e email.

Lite
Com certeza! Aqui estão os dois arquivos completos e corrigidos:
1. Arquivo Python (app.py)
Este arquivo contém a nova rota /search_user_by_id que realiza a busca pelo ID no Supabase.
Anexado: /home/ubuntu/app.py
Python
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
import os
import random

app = Flask(__name__)

# Configurações do Supabase (preencha com suas credenciais)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ulbaklykimxpsdrtkqet.supabase.co" )
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVsYmFrbHlraW14cHNkcnRrcWV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjc0MjcsImV4cCI6MjA3MzkwMzQyN30.A3_WLF3cNstQtXcOr2Q3OJCvTYqBQe7wmmXHc_WCqAk")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/random_user")
def random_user():
    try:
        # Busca um usuário aleatório no Supabase
        response = supabase.from_('users').select('*').limit(100).execute()
        users = response.data
        if users:
            random_user_data = random.choice(users)
            return render_template("index.html", random_user=random_user_data)
        return render_template("index.html", random_user=None, message="Nenhum usuário encontrado.")
    except Exception as e:
        return render_template("index.html", random_user=None, error=f"Erro ao buscar usuário aleatório: {e}")

@app.route("/search_user", methods=["POST"])
def search_user():
    query_term = request.form.get("query_term")
    if query_term:
        try:
            # Busca usuários por nome ou email
            response_name = supabase.from_('users').select('*').ilike('nome', f'%{query_term}%').execute()
            response_email = supabase.from_('users').select('*').ilike('email', f'%{query_term}%').execute()
            
            # Combina os resultados e remove duplicatas
            searched_users_name = response_name.data
            searched_users_email = response_email.data
            
            # Usar um conjunto para remover duplicatas baseadas em nome
            unique_users = {user['nome']: user for user in searched_users_name}
            for user in searched_users_email:
                unique_users[user['nome']] = user
            
            searched_users = list(unique_users.values())

            return render_template("index.html", searched_users=searched_users, query_term=query_term)
        except Exception as e:
            return render_template("index.html", searched_users=[], query_term=query_term, error=f"Erro ao buscar usuários: {e}")
    return redirect(url_for("index"))

# NOVA FUNCIONALIDADE: Busca usuário por ID
@app.route("/search_user_by_id", methods=["POST"])
def search_user_by_id():
    user_id = request.form.get("user_id")
    if user_id:
        try:
            # Tenta converter o ID para inteiro, pois IDs em bancos de dados costumam ser numéricos
            # Se o ID for uma string (UUID, por exemplo), remova a conversão para int()
            try:
                user_id_int = int(user_id)
            except ValueError:
                # Se não for um inteiro, assume que é uma string (como UUID)
                user_id_int = user_id 
                
            # Busca o usuário pelo ID. Usamos '.single()' para esperar um único resultado
            # ou erro se mais de um for encontrado (o que não deve ocorrer com ID)
            response = supabase.from_('users').select('*').eq('id', user_id_int).single().execute()
            
            # O '.data' do single() retorna o objeto diretamente, não uma lista.
            found_user = response.data
            
            # Colocamos o usuário encontrado em uma lista para manter a consistência com
            # outras rotas de busca no template (se necessário)
            searched_users_by_id = [found_user] if found_user else []

            return render_template("index.html", 
                                   searched_users_by_id=searched_users_by_id, 
                                   user_id=user_id,
                                   message=f"Usuário encontrado com ID: {user_id}" if found_user else f"Nenhum usuário encontrado com ID: {user_id}")
        except Exception as e:
            # Trata o erro de "No rows found" do .single() ou qualquer outro erro
            error_message = f"Erro ao buscar usuário por ID: {e}"
            if "No rows found" in str(e):
                 error_message = f"Nenhum usuário encontrado com ID: {user_id}"
                 return render_template("index.html", searched_users_by_id=[], user_id=user_id, error=error_message)
            return render_template("index.html", searched_users_by_id=[], user_id=user_id, error=error_message)
    return redirect(url_for("index"))

# Função de recomendação (exemplo: recomenda usuarios na mesma cidade)
@app.route("/recommend_users", methods=["POST"])
def recommend_users():
    user_id_to_recommend_for = request.form.get("user_id") # Assumindo que você passa um ID de usuário para recomendação
    if user_id_to_recommend_for:
        try:
            # Primeiro, obtenha os detalhes do usuário para quem você quer recomendar
            user_response = supabase.from_('users').select('*').eq('id', user_id_to_recommend_for).single().execute()
            current_user = user_response.data

            if current_user and current_user.get('cidade'):
                city = current_user['cidade']
                # Busca outros usuários na mesma cidade, excluindo o próprio usuário
                recommendations_response = supabase.from_('users').select('*').eq('cidade', city).neq('id', user_id_to_recommend_for).execute()
                recommended_users = recommendations_response.data
                return render_template("index.html", recommended_users=recommended_users, current_user_for_rec=current_user)
            else:
                return render_template("index.html", recommended_users=[], message="Não foi possível encontrar o usuário ou a cidade para recomendação.")
        except Exception as e:
            return render_template("index.html", recommended_users=[], error=f"Erro ao recomendar usuários: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
2. Arquivo HTML (index.html)
Este arquivo (que você forneceu como telasHTML/TelaInicial.html) foi adaptado para incluir o formulário de busca por ID e a lógica para exibir os resultados dessa busca. Lembre-se de colocá-lo na pasta templates do seu projeto Flask.
Anexado: /home/ubuntu/templates/index.html
HTML
<!-- Localização: templates/index.html (originalmente telasHTML/TelaInicial.html) -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App de Usuários</title>
    <!-- Usando url_for para garantir que os caminhos funcionem -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='iconeUser.png') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header class="barra-superior">
        <button class="menu-button">
            <img src="{{ url_for('static', filename='TresPontos.png') }}" alt="Menu">
        </button> 
        <div class="search-container">
            <!-- NOVO: Formulário de busca por ID -->
            <form method="POST" action="/search_user_by_id" style="display: flex; align-items: center; margin-right: 15px;">
                <input placeholder="Buscar por ID" class="search-input" type="text" name="user_id" style="width: 100px;">
                <button type="submit" style="background: none; border: none; padding: 0; cursor: pointer;">
                    <img src="{{ url_for('static', filename='lupa.png') }}" alt="Ícone de pesquisa por ID" style="width: 20px; height: 20px; vertical-align: middle;"> 
                </button>
            </form>
            
            <!-- Formulário de busca por nome/email (mantido) -->
            <form method="POST" action="/search_user" style="display: flex; align-items: center;">
                <input placeholder="Pesquisar por Nome/Email" class="search-input" type="text" name="query_term">
                <button type="submit" style="background: none; border: none; padding: 0; cursor: pointer;">
                    <img src="{{ url_for('static', filename='lupa.png') }}" alt="Ícone de pesquisa"> 
                </button>
            </form>
        </div>
    </header>

    <main class="content">
        {% if error %}
            <p style="color: red;">Erro: {{ error }}</p>
        {% endif %}
        {% if message %}
            <p style="color: green;">{{ message }}</p>
        {% endif %}

        <div id="usuarios-container">
            {% if searched_users_by_id %}
                <h2>Resultado da Busca por ID</h2>
                {% for usuario in searched_users_by_id %}
                    <div class="usuario-card">
                        <img class="usuario-foto" src="{{ url_for('static', filename='iconeUser.png') }}" alt="Foto do usuário">
                        <div class="usuario-info">
                            <h3 class="usuario-nome">{{ usuario.nome }} (ID: {{ usuario.id }})</h3>
                            <p class="usuario-cidade">Cidade: {{ usuario.cidade }}</p>
                            <p class="usuario-email">Email: {{ usuario.email }}</p>
                            <!-- Adicione mais campos conforme necessário -->
                        </div>
                    </div>
                {% endfor %}
            {% elif searched_users %}
                <h2>Resultado da Busca por Nome/Email</h2>
                {% for usuario in searched_users %}
                    <div class="usuario-card">
                        <img class="usuario-foto" src="{{ url_for('static', filename='iconeUser.png') }}" alt="Foto do usuário">
                        <div class="usuario-info">
                            <h3 class="usuario-nome">{{ usuario.nome }}</h3>
                            <p class="usuario-cidade">{{ usuario.cidade }}</p>
                        </div>
                    </div>
                {% endfor %}
            {% elif usuarios %}
                <h2>Todos os Usuários</h2>
                {% for usuario in usuarios %}
                    <div class="usuario-card">
                        <img class="usuario-foto" src="{{ url_for('static', filename='iconeUser.png') }}" alt="Foto do usuário">
                        <div class="usuario-info">
                            <h3 class="usuario-nome">{{ usuario.nome }}</h3>
                            <p class="usuario-cidade">{{ usuario.cidade }}</p>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p>Nenhum usuário cadastrado ainda.</p>
            {% endif %}
        </div>
    </main>

    <div class="floating-button-container">
        <div class="floating-button-bar"></div>
        <button id="adicionarUsuarioBtn" class="floating-button">
            <img src="{{ url_for('static', filename='bolaLogo.png') }}" alt="Adicionar usuário">
        </button>
    </div>
    <div class="entadaUserBotao-container">
        <div class="entadaUserBotao-bar"></div>
        <button id="entadaUserBotao" class="entadaUserBotao-button">
            <a href="#"><img src="{{ url_for('static', filename='BotaoUsuario.ico') }}" alt="Botão Usuário"></a>
        </button>
    </div>
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
app.py
Código · 6.07 KB
index.html
Código · 4.91 KB

Ver todos os arquivos nesta tarefa
Tarefa concluída
Como foi este resultado?
Sugestões de acompanhamento
Enviar mensagem para Manus
Todos os arquivos nesta tarefa
Hoje

app.py
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
import os
import random

app = Flask(__name__)

# Configurações do Supabase (preencha com suas credenciais)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ulbaklykimxpsdrtkqet.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVsYmFrbHlraW14cHNkcnRrcWV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjc0MjcsImV4cCI6MjA3MzkwMzQyN30.A3_WLF3cNstQtXcOr2Q3OJCvTYqBQe7wmmXHc_WCqAk")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/random_user")
def random_user():
    try:
        # Busca um usuário aleatório no Supabase
        response = supabase.from_('users').select('*').limit(100).execute()
        users = response.data
        if users:
            random_user_data = random.choice(users)
            return render_template("index.html", random_user=random_user_data)
        return render_template("index.html", random_user=None, message="Nenhum usuário encontrado.")
    except Exception as e:
        return render_template("index.html", random_user=None, error=f"Erro ao buscar usuário aleatório: {e}")

@app.route("/search_user", methods=["POST"])
def search_user():
    query_term = request.form.get("query_term")
    if query_term:
        try:
            # Busca usuários por nome ou email
            response_name = supabase.from_('users').select('*').ilike('nome', f'%{query_term}%').execute()
            response_email = supabase.from_('users').select('*').ilike('email', f'%{query_term}%').execute()
            
            # Combina os resultados e remove duplicatas
            searched_users_name = response_name.data
            searched_users_email = response_email.data
            
            # Usar um conjunto para remover duplicatas baseadas em nome
            unique_users = {user['nome']: user for user in searched_users_name}
            for user in searched_users_email:
                unique_users[user['nome']] = user
            
            searched_users = list(unique_users.values())

            return render_template("index.html", searched_users=searched_users, query_term=query_term)
        except Exception as e:
            return render_template("index.html", searched_users=[], query_term=query_term, error=f"Erro ao buscar usuários: {e}")
    return redirect(url_for("index"))

# NOVA FUNCIONALIDADE: Busca usuário por ID
@app.route("/search_user_by_id", methods=["POST"])
def search_user_by_id():
    user_id = request.form.get("user_id")
    if user_id:
        try:
            # Tenta converter o ID para inteiro, pois IDs em bancos de dados costumam ser numéricos
            # Se o ID for uma string (UUID, por exemplo), remova a conversão para int()
            try:
                user_id_int = int(user_id)
            except ValueError:
                # Se não for um inteiro, assume que é uma string (como UUID)
                user_id_int = user_id 
                
            # Busca o usuário pelo ID. Usamos '.single()' para esperar um único resultado
            # ou erro se mais de um for encontrado (o que não deve ocorrer com ID)
            response = supabase.from_('users').select('*').eq('id', user_id_int).single().execute()
            
            # O '.data' do single() retorna o objeto diretamente, não uma lista.
            found_user = response.data
            
            # Colocamos o usuário encontrado em uma lista para manter a consistência com
            # outras rotas de busca no template (se necessário)
            searched_users_by_id = [found_user] if found_user else []

            return render_template("index.html", 
                                   searched_users_by_id=searched_users_by_id, 
                                   user_id=user_id,
                                   message=f"Usuário encontrado com ID: {user_id}" if found_user else f"Nenhum usuário encontrado com ID: {user_id}")
        except Exception as e:
            # Trata o erro de "No rows found" do .single() ou qualquer outro erro
            error_message = f"Erro ao buscar usuário por ID: {e}"
            if "No rows found" in str(e):
                 error_message = f"Nenhum usuário encontrado com ID: {user_id}"
                 return render_template("index.html", searched_users_by_id=[], user_id=user_id, error=error_message)
            return render_template("index.html", searched_users_by_id=[], user_id=user_id, error=error_message)
    return redirect(url_for("index"))

# Função de recomendação (exemplo: recomenda usuarios na mesma cidade)
@app.route("/recommend_users", methods=["POST"])
def recommend_users():
    user_id_to_recommend_for = request.form.get("user_id") # Assumindo que você passa um ID de usuário para recomendação
    if user_id_to_recommend_for:
        try:
            # Primeiro, obtenha os detalhes do usuário para quem você quer recomendar
            user_response = supabase.from_('users').select('*').eq('id', user_id_to_recommend_for).single().execute()
            current_user = user_response.data

            if current_user and current_user.get('cidade'):
                city = current_user['cidade']
                # Busca outros usuários na mesma cidade, excluindo o próprio usuário
                recommendations_response = supabase.from_('users').select('*').eq('cidade', city).neq('id', user_id_to_recommend_for).execute()
                recommended_users = recommendations_response.data
                return render_template("index.html", recommended_users=recommended_users, current_user_for_rec=current_user)
            else:
                return render_template("index.html", recommended_users=[], message="Não foi possível encontrar o usuário ou a cidade para recomendação.")
        except Exception as e:
            return render_template("index.html", recommended_users=[], error=f"Erro ao recomendar usuários: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
Complementar código para busca por ID no Supabase - Manus