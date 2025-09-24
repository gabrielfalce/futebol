document.addEventListener ('DOMContentLoaded', function() {
    // Elementos DOM
    const adicionarUsuarioBtn = document.getElementById('adicionarUsuarioBtn');
    const usuariosContainer = document.getElementById('usuarios-container');
    const searchInput = document.querySelector('.search-input');
    
    // Dados dos usuários (poderia ser substituído por uma API)
    let usuarios = [
        {
            nome: 'matheson',
            idade: '25 anos',
            cidade: 'mesopotamia',
            foto: 'iconeUser.png'
        }
    ];
    
    // Constante para limite de usuários
    const LIMITE_USUARIOS = 15;
    
    // Event Listeners
    adicionarUsuarioBtn.addEventListener('click', adicionarUsuario);
    searchInput.addEventListener('input', filtrarUsuarios);
    
    // Função para renderizar usuários
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
        
        // Atualiza o estado do botão
        atualizarEstadoBotao();
    }
    
    // Função para adicionar novo usuário
    function adicionarUsuario() {
        // Verifica se atingiu o limite
        if (usuarios.length >= LIMITE_USUARIOS) {
            mostrarAlerta(`Limite máximo de ${LIMITE_USUARIOS} usuários atingido! Utilize a barra de pesquisa para encontrar usuários.`, 'error');
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
        
        // Animação
        const cards = document.querySelectorAll('.usuario-card');
        if (cards.length > 0) {
            cards[0].style.transform = 'scale(1.05)';
            setTimeout(() => {
                cards[0].style.transform = '';
            }, 300);
        }
    }
    
    // Função para atualizar o estado do botão
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
    
    // Função para filtrar usuários
    function filtrarUsuarios() {
        const termo = searchInput.value.toLowerCase();
        const usuariosFiltrados = usuarios.filter(usuario => 
            usuario.nome.toLowerCase().includes(termo) || 
            usuario.cidade.toLowerCase().includes(termo) ||
            usuario.idade.includes(termo)
        );
        
        renderizarUsuarios(usuariosFiltrados);
    }
    
    // Função para mostrar alerta
    function mostrarAlerta(mensagem, tipo) {
        // Cria elemento de alerta
        const alerta = document.createElement('div');
        alerta.className = `alerta alerta-${tipo}`;
        alerta.textContent = mensagem;

        // Adiciona ao corpo
        document.body.appendChild(alerta);

        // Remove após 3 segundos
        setTimeout(() => {
            alerta.classList.add('fade-out');
            setTimeout(() => alerta.remove(), 500);
        }, 3000);
    }
    
    // Efeito de animação para o botão
    function AnimationEffect() {
        if (usuarios.length >= LIMITE_USUARIOS) return;
        
        adicionarUsuarioBtn.style.transform = 'scale(1.1) rotate(90deg)';
        setTimeout(() => {
            adicionarUsuarioBtn.style.transform = 'scale(1) rotate(0)';
        }, 300);
    }
    
    // Adicionando o efeito ao botão
    adicionarUsuarioBtn.addEventListener('click', AnimationEffect);
    
    // Renderizar inicialmente
    renderizarUsuarios();
});
//  informa usuario usar pesquisa

function mostrarAlerta() {
    if (usuarios.length >= LIMITE_USUARIOS) {
      alert("use a barra de pesquisa para encontrar usuários.");
      return;
    }

}
