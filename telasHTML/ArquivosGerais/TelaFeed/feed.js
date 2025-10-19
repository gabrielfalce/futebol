// Executa o código quando o HTML da página estiver totalmente carregado.
document.addEventListener('DOMContentLoaded', () => {
    
    // Pega as referências dos elementos HTML que vamos manipular.
    const feedContainer = document.getElementById('feed-container');
    const loadingSpinner = document.getElementById('loading-spinner');

    let currentPage = 1; // Controla qual página de posts estamos buscando.
    let isLoading = false; // Flag para evitar carregar várias páginas ao mesmo tempo.

    // Função para criar o HTML de um único post.
    function createPostElement(post) {
        const postCard = document.createElement('div');
        postCard.className = 'post-card';

        // Define o conteúdo HTML do cartão do post.
        postCard.innerHTML = `
            <div class="post-header">
                <img src="${post.autor.profile_image_url || '/TelaDeUsuario/imagens/user-icon-placeholder.png'}" alt="Avatar do autor" class="avatar">
                <strong>${post.autor.nome}</strong>
            </div>
            <img src="${post.imagem_url}" alt="Imagem do post" class="post-image">
            <div class="post-caption">
                <p>${post.legenda || ''}</p>
            </div>
        `;
        return postCard;
    }

    // Função assíncrona para buscar mais posts na nossa API.
    async function loadMorePosts() {
        if (isLoading) return; // Se já estiver carregando, sai da função.
        isLoading = true;
        loadingSpinner.style.display = 'block'; // Mostra a animação de carregamento.

        try {
            // Faz a requisição para a nossa API, passando a página atual.
            const response = await fetch(`/api/posts?page=${currentPage}&limit=5`);
            const posts = await response.json();

            if (posts && posts.length > 0) {
                // Se receber posts, cria e adiciona cada um na tela.
                posts.forEach(post => {
                    const postElement = createPostElement(post);
                    feedContainer.appendChild(postElement);
                });
                currentPage++; // Incrementa a página para a próxima busca.
            } else {
                // Se não vierem mais posts, remove o "ouvinte" de scroll.
                console.log("Fim dos posts.");
                window.removeEventListener('scroll', handleScroll);
                loadingSpinner.style.display = 'none'; // Esconde a animação.
            }
        } catch (error) {
            console.error("Erro ao carregar mais posts:", error);
            // Poderíamos mostrar uma mensagem de erro para o usuário aqui.
        } finally {
            isLoading = false; // Libera para o próximo carregamento.
            loadingSpinner.style.display = 'none'; // Esconde a animação.
        }
    }

    // Função que verifica se o usuário chegou ao final da página.
    function handleScroll() {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        // Se a soma da altura visível + o quanto já rolou for perto da altura total da página...
        if (clientHeight + scrollTop >= scrollHeight - 100) {
            loadMorePosts(); // ...carrega mais posts.
        }
    }

    // Adiciona o "ouvinte" de scroll na janela.
    window.addEventListener('scroll', handleScroll);

    // Carrega a primeira página de posts assim que o site abre.
    loadMorePosts();
});
