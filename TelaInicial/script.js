// =======================
// INICIALIZAÇÃO E VARIÁVEIS GLOBAIS
// =======================
document.addEventListener('DOMContentLoaded', function () {
    // --- Seleção de Elementos DOM ---
    const adicionarUsuarioBtn = document.getElementById('adicionarUsuarioBtn');
    const usuariosContainer = document.getElementById('usuarios-container');
    const searchInput = document.querySelector('.search-input');
    const alertaContainer = document.getElementById('alerta-container');

    // --- Dados Iniciais dos Usuários ---
    let usuarios = [
        {
            nome: 'matheson',
            idade: '25 anos',
            cidade: 'mesopotamia',
            foto: 'iconeUser.png'
        }
    ];

    // --- Limite Máximo de Usuários ---
    const LIMITE_USUARIOS = 3;

    // =======================
    // EVENTOS PRINCIPAIS
    // =======================
    adicionarUsuarioBtn.addEventListener('click', adicionarUsuario);      // Adiciona usuário ao clicar
    adicionarUsuarioBtn.addEventListener('click', AnimationEffect);       // Animação do botão ao clicar
    searchInput.addEventListener('input', filtrarUsuarios);               // Filtra usuários ao digitar

    // Renderização inicial dos usuários
    renderizarUsuarios();

    // =======================
    // FUNÇÃO: Renderizar Usuários na Tela
    // =======================
    function renderizarUsuarios(usuariosParaRenderizar = usuarios) {
        usuariosContainer.innerHTML = '';

        usuariosParaRenderizar.forEach(usuario => {
            const usuarioHTML = `
                <div class="usuario-card">
                    <img class="usuario-foto" src="${usuario.foto}" alt="Foto do usuário">
                    <div class="usuario-info">
                        <h3 class="usuario-nome">${usuario.nome}</h3>
                        <p class="usuario-idade">${usuario.idade}</p>
                        <p class="usuario-cidade">${usuario.cidade}</p>
                    </div>
                </div>
            `;
            usuariosContainer.insertAdjacentHTML('beforeend', usuarioHTML);
        });

        atualizarAlerta();
        atualizarEstadoBotao();
    }

    // =======================
    // FUNÇÃO: Adicionar Novo Usuário
    // =======================
    function adicionarUsuario() {
        if (usuarios.length >= LIMITE_USUARIOS) {
            mostrarAlerta(
                `Limite máximo de usuários atingido! Utilize a barra de pesquisa para encontrar usuários.`,
                'error'
            );
            return;
        }

        const novoUsuario = {
            nome: `Usuário ${usuarios.length + 1}`,
            idade: `${Math.floor(Math.random() * 80) + 1} anos`,
            cidade: ['mesopotamia', 'curitiba', 'roma', 'atenas'][Math.floor(Math.random() * 4)],
            foto: 'iconeUser.png'
        };

        usuarios.unshift(novoUsuario);
        renderizarUsuarios();

        // Animação no novo card
        const cards = document.querySelectorAll('.usuario-card');
        if (cards.length > 0) {
            cards[0].style.transform = 'scale(1.05)';
            setTimeout(() => {
                cards[0].style.transform = '';
            }, 300);
        }
    }

    // =======================
    // FUNÇÃO: Atualizar Estado do Botão de Adicionar
    // =======================
    function atualizarEstadoBotao() {
        if (usuarios.length >= LIMITE_USUARIOS) {
            adicionarUsuarioBtn.disabled = true;
            adicionarUsuarioBtn.style.opacity = '0.5';
            adicionarUsuarioBtn.style.cursor = 'not-allowed';
            adicionarUsuarioBtn.title = 'Limite máximo de usuários atingido';
        } else {
            adicionarUsuarioBtn.disabled = false;
            adicionarUsuarioBtn.style.opacity = '1';
            adicionarUsuarioBtn.style.cursor = 'pointer';
            adicionarUsuarioBtn.title = 'Adicionar novo usuário';
        }
    }

    // =======================
    // FUNÇÃO: Filtrar Usuários pelo Campo de Pesquisa
    // =======================
    function filtrarUsuarios() {
        const termo = searchInput.value.toLowerCase();
        const usuariosFiltrados = usuarios.filter(usuario =>
            usuario.nome.toLowerCase().includes(termo) ||
            usuario.cidade.toLowerCase().includes(termo) ||
            usuario.idade.includes(termo)
        );
        renderizarUsuarios(usuariosFiltrados);
    }

    // =======================
    // FUNÇÃO: Atualizar Alerta Fixo Abaixo dos Cards
    // =======================
    function atualizarAlerta() {
        if (usuarios.length >= LIMITE_USUARIOS) {
            alertaContainer.innerHTML = `
                <div class="alerta alerta-error">
                    Limite máximo de ${LIMITE_USUARIOS} usuários atingido! Utilize a barra de pesquisa para encontrar usuários.
                </div>
            `;
        } else {
            alertaContainer.innerHTML = '';
        }
    }

    // =======================
    // FUNÇÃO: Mostrar Alerta Centralizado na Tela (Temporário)
    // =======================
    function mostrarAlerta(mensagem, tipo) {
        const alerta = document.createElement('div');
        alerta.className = `alerta alerta-${tipo}`;
        alerta.textContent = mensagem;
        document.body.appendChild(alerta);

        setTimeout(() => {
            alerta.classList.add('fade-out');
            setTimeout(() => alerta.remove(), 500);
        }, 3000);
    }

    // =======================
    // FUNÇÃO: Animação do Botão de Adicionar Usuário
    // =======================
    function AnimationEffect() {
        if (usuarios.length >= LIMITE_USUARIOS) return;
        adicionarUsuarioBtn.style.transform = 'scale(1.1) rotate(90deg)';
        setTimeout(() => {
            adicionarUsuarioBtn.style.transform = 'scale(1) rotate(0)';
        }, 300);
    }
});


