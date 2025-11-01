// Aguarda o DOM estar completamente carregado para executar o script
document.addEventListener('DOMContentLoaded', () => {

    // Seleciona os elementos principais da página
    const feedContainer = document.getElementById('feed-container');
    const loadingSpinner = document.getElementById('loading-spinner');

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
        // O backend já garante que 'post.autor' existe.
        const avatarUrl = post.autor.profile_image_url || '{{ url_for("inicio_assets", filename="iconeUser.png") }}'; // Usando url_for para uma imagem padrão segura

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
                <!-- ALTERAÇÃO: Trocado 'post.conteudo' por 'post.legenda' para corresponder ao backend -->
                <p>${post.legenda}</p>
            </div>
            ${post.imagem_url ? `<img src="${post.imagem_url}" alt="Imagem do post" class="post-image">` : ''}
        `;
        // A linha acima adiciona a tag <img> apenas se a 'imagem_url' existir

        return card;
    }

    // Função principal para carregar os posts da API
    async function carregarPosts() {
        loadingSpinner.style.display = 'block'; // Mostra o spinner

        try {
            // ALTERAÇÃO: Simplificado o fetch para buscar todos os posts de uma vez, sem paginação,
            // que é o que o backend atual suporta.
            const response = await fetch('/api/posts'); 
            
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.statusText}`);
            }

            const posts = await response.json();

            // Esconde o spinner depois que os dados chegam
            loadingSpinner.style.display = 'none';

            // Se a API não retornar posts, mostra uma mensagem.
            if (posts.length === 0) {
                feedContainer.innerHTML = '<p style="text-align: center; color: #aaa;">Nenhum post no feed ainda. Seja o primeiro a publicar!</p>';
                return;
            }

            // Para cada post retornado, cria um card e adiciona ao container
            posts.forEach(post => {
                const postCard = criarPostCard(post);
                feedContainer.appendChild(postCard);
            });

        } catch (error) {
            console.error("Falha ao carregar posts:", error);
            loadingSpinner.style.display = 'none'; // Esconde o spinner em caso de erro
            feedContainer.innerHTML = '<p style="text-align: center; color: #f44336;">Erro ao carregar o feed. Tente novamente mais tarde.</p>';
        }
    }

    // Carrega os posts assim que a página abre
    carregarPosts();
});
