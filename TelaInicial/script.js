// Importa a função para criar o cliente Supabase
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// =======================
// CONFIGURAÇÃO E INICIALIZAÇÃO IMEDIATA
// =======================
const SUPABASE_URL = 'https://ulbaklykimxpsdrtkqet.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVsYmFrbHlraW14cHNkcnRrcWV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjc0MjcsImV4cCI6MjA3MzkwMzQyN30.A3_WLF3cNstQtXcOr2Q3OJCvTYqBQe7wmmXHc_WCqAk'
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY )

// --- Seleção de Elementos DOM ---
// É seguro fazer isso aqui, pois o script é carregado no final do <body>
const usuariosContainer = document.getElementById('usuarios-container');
const searchInput = document.querySelector('.search-input');
const logoutButton = document.getElementById('logout-button');

// --- Armazenamento de Dados ---
let todosOsUsuarios = [];
let usuarioLogado = null;

// =======================
// FUNÇÕES
// =======================

// Busca todos os perfis da tabela 'profiles'
async function fetchUsers() {
    const { data, error } = await supabase.from('profiles').select('*');

    if (error) {
        console.error('Erro ao buscar usuários:', error);
        usuariosContainer.innerHTML = '<p>Erro ao carregar usuários.</p>';
        return;
    }
    
    todosOsUsuarios = data || [];
    renderizarUsuarios();
}

// Realiza o logout do usuário
async function handleLogout(event) {
    event.preventDefault();
    await supabase.auth.signOut();
    window.location.href = '/index.html';
}

// Renderiza os cards de usuário na tela
function renderizarUsuarios(usuariosParaRenderizar = todosOsUsuarios) {
    usuariosContainer.innerHTML = '';
    const outrosUsuarios = usuariosParaRenderizar.filter(u => u.id !== usuarioLogado.id);

    if (outrosUsuarios.length === 0) {
        usuariosContainer.innerHTML = '<p style="text-align: center; color: #aaa; width: 100%;">Nenhum outro usuário encontrado.</p>';
        return;
    }

    outrosUsuarios.forEach(usuario => {
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

// Filtra os usuários com base no que é digitado na barra de busca
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
// PONTO DE ENTRADA PRINCIPAL (IIFE - Immediately Invoked Function Expression)
// =======================
// Esta função anônima é executada imediatamente assim que o script é lido.
(async () => {
    // 1. Protege a Rota: Verifica se há um usuário logado
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();

    if (sessionError || !session) {
        // Se houver erro ou não houver sessão, redireciona para o login
        window.location.href = '/index.html'; 
        return;
    }
    
    usuarioLogado = session.user;

    // 2. Adiciona os eventos aos elementos da página
    searchInput.addEventListener('input', filtrarUsuarios);
    logoutButton.addEventListener('click', handleLogout);

    // 3. Busca os usuários do banco de dados
    // Esta chamada agora é a última coisa a acontecer
    await fetchUsers();
})();
