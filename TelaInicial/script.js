// Importa a função para criar o cliente Supabase
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// =======================
// INICIALIZAÇÃO E VARIÁVEIS GLOBAIS
// =======================
const SUPABASE_URL = 'https://ulbaklykimxpsdrtkqet.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVsYmFrbHlraW14cHNkcnRrcWV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjc0MjcsImV4cCI6MjA3MzkwMzQyN30.A3_WLF3cNstQtXcOr2Q3OJCvTYqBQe7wmmXHc_WCqAk'
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY )

// --- Seleção de Elementos DOM ---
const usuariosContainer = document.getElementById('usuarios-container');
const searchInput = document.querySelector('.search-input');
const alertaContainer = document.getElementById('alerta-container');
const logoutButton = document.getElementById('logout-button');

// --- Dados dos Usuários (agora virão do banco) ---
let todosOsUsuarios = [];
let usuarioLogado = null;

// =======================
// FLUXO PRINCIPAL DA PÁGINA
// =======================
// Função principal que roda quando o script é carregado
async function iniciarPagina() {
    // 1. Protege a Rota e obtém a sessão
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
        window.location.href = '/index.html'; 
        return; // Para a execução se não houver sessão
    }
    usuarioLogado = session.user;

    // 2. Busca os usuários do banco de dados
    await fetchUsers();

    // 3. Adiciona os eventos aos elementos da página
    searchInput.addEventListener('input', filtrarUsuarios);
    logoutButton.addEventListener('click', handleLogout);
}

// Chama a função principal para iniciar a página
iniciarPagina();

// =======================
// FUNÇÃO: Buscar Usuários da Supabase
// =======================
async function fetchUsers() {
    usuariosContainer.innerHTML = '<p>Carregando usuários...</p>';

    const { data, error } = await supabase
        .from('profiles')
        .select('*');

    if (error) {
        console.error('Erro ao buscar usuários:', error);
        mostrarAlerta('Erro ao carregar usuários.', 'error');
        return;
    }
    
    // Armazena todos os usuários na variável global
    todosOsUsuarios = data || [];
    
    // Renderiza os usuários na tela
    renderizarUsuarios();
}

// =======================
// FUNÇÃO: Renderizar Usuários na Tela
// =======================
function renderizarUsuarios(usuariosParaRenderizar = todosOsUsuarios) {
    usuariosContainer.innerHTML = '';

    const usuariosFiltrados = usuariosParaRenderizar.filter(u => u.id !== usuarioLogado.id);

    if (usuariosFiltrados.length === 0) {
        usuariosContainer.innerHTML = '<p style="text-align: center; color: #aaa; width: 100%;">Nenhum outro usuário encontrado.</p>';
        return;
    }

    usuariosFiltrados.forEach(usuario => {
        const usuarioHTML = `
            <a href="/TelaChat/chat.html?destinatario_id=${usuario.id}" class="user-card-link">
                <div class="usuario-card">
                    <img class="usuario-foto" src="/TelaDeUsuario/imagens/hM94BRC.jpeg" alt="Foto de ${usuario.nome_completo}">
                    <div class="usuario-info">
                        <h3 class="usuario-nome">${usuario.nome_completo || 'Nome Desconhecido'}</h3>
                        <p class="usuario-cidade">${usuario.cidade || 'N/A'}</p>
                        <p class="usuario-posicao">${usuario.posicao || 'N/A'}</p>
                    </div>
                </div>
            </a>
        `;
        usuariosContainer.insertAdjacentHTML('beforeend', usuarioHTML);
    });
}

// =======================
// FUNÇÃO: Filtrar Usuários (adaptada do seu código)
// =======================
function filtrarUsuarios() {
    const termo = searchInput.value.toLowerCase();
    const usuariosFiltrados = todosOsUsuarios.filter(usuario =>
        (usuario.nome_completo && usuario.nome_completo.toLowerCase().includes(termo)) ||
        (usuario.cidade && usuario.cidade.toLowerCase().includes(termo)) ||
        (usuario.posicao && usuario.posicao.toLowerCase().includes(termo))
    );
    renderizarUsuarios(usuariosFiltrados);
}

// =======================
// FUNÇÃO: Logout
// =======================
async function handleLogout(event) {
    event.preventDefault(); // Previne que o link '#' mude a URL
    await supabase.auth.signOut();
    window.location.href = '/index.html';
}

// =======================
// FUNÇÃO: Mostrar Alerta (adaptada do seu código)
// =======================
function mostrarAlerta(mensagem, tipo) {
    alertaContainer.innerHTML = `<div class="alerta alerta-${tipo}">${mensagem}</div>`;
    setTimeout(() => {
        alertaContainer.innerHTML = '';
    }, 3000);
}
