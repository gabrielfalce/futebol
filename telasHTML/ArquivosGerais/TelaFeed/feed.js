// Aguarda o DOM estar completamente carregado para executar o script
document.addEventListener('DOMContentLoaded', () => {

    // Seleciona os elementos principais da página
    const feedContainer = document.getElementById('feed-container');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Variáveis para controlar a paginação e o carregamento
    let currentPage = 1;
    let isLoading = false;
    const postsPerPage = 10; // Quantos posts carregar por vez

    // Função para formatar a data (ex: "19 de Outubro de 2025, 23:05")
    function formatarData(isoString) {
        if (!isoString) return '';
        const data = new Date(isoString);
        return data.toLocaleString('pt-BR', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Função para criar o HTML de um único card de post
    function criarPostCard(post) {
        // Define uma imagem padrão caso o autor não tenha foto de perfil
        const avatarUrl = post.autor.profile_image_url || '/TelaDeUsuario/imagens/user-icon-placeholder.png';

        // Cria o elemento do card
        const card = document.createElement('div');
        card.className = 'post-card';

        // Constrói o HTML interno do card
        card.innerHTML = `
            <div class="post-header">
                <img src="${avatarUrl}" alt="Avatar de ${post.autor.nome}" class="author-avatar">
                <div class="author-info">
                    <p class="author-name">${post.autor.nome}</p>
                    <p class="post-timestamp">${formatarData(post.created_at)}</p>
                </div>
            </div>
            <div class="post-content">
                <p>${post.conteudo}</p>
            </div>
            ${post.imagem_url ? `<img src="${post.imagem_url}" alt="Imagem do post" class="post-image">` : ''}
        `;
        // A linha acima adiciona a tag <img> apenas se a 'imagem_url' existir

        return card;
    }

    // Função principal para carregar os posts da API
    async function carregarPosts() {
        // Previne múltiplos carregamentos ao mesmo tempo
        if (isLoading) return;
        isLoading = true;
        loadingSpinner.style.display = 'block'; // Mostra o spinner

        try {
            // Faz a requisição para a nossa API, passando a página e o limite
            const response = await fetch(`/api/posts?page=${currentPage}&limit=${postsPerPage}`);
            
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.statusText}`);
            }

            const posts = await response.json();

            // Se a API não retornar mais posts, para de tentar carregar
            if (posts.length === 0) {
                loadingSpinner.style.display = 'none'; // Esconde o spinner
                window.removeEventListener('scroll', handleScroll); // Para de ouvir o scroll
                return;
            }

            // Para cada post retornado, cria um card e adiciona ao container
            posts.forEach(post => {
                const postCard = criarPostCard(post);
                feedContainer.appendChild(postCard);
            });

            // Incrementa a página para a próxima requisição
            currentPage++;

        } catch (error) {
            console.error("Falha ao carregar posts:", error);
            // Poderíamos mostrar uma mensagem de erro na tela aqui
        } finally {
            // Garante que o estado de carregamento seja resetado e o spinner escondido
            isLoading = false;
            loadingSpinner.style.display = 'none';
        }
    }

    // Função para lidar com a rolagem infinita
    function handleScroll() {
        // Verifica se o usuário chegou perto do final da página
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop + clientHeight >= scrollHeight - 200) {
            carregarPosts();
        }
    }

    // Adiciona o "ouvinte" de scroll na janela
    window.addEventListener('scroll', handleScroll);

    // Carrega o primeiro lote de posts assim que a página abre
    carregarPosts();
});
