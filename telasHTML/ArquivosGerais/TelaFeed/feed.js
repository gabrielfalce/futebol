
        document.addEventListener('DOMContentLoaded', () => {
            const feedContainer = document.getElementById('container-feed');
            const loadingSpinner = document.getElementById('spinner-carregamento');

            // Função para formatar a data (adicionada para uso)
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

            async function loadPosts() {
                try {
                    const response = await fetch('{{ url_for("api_posts") }}');
                    if (!response.ok) {
                        throw new Error('Falha ao carregar posts');
                    }
                    const posts = await response.json();
                    
                    loadingSpinner.style.display = 'none';
                    renderPosts(posts);
                    
                } catch (error) {
                    console.error('Erro:', error);
                    loadingSpinner.style.display = 'none';
                    feedContainer.innerHTML = '<p style="text-align: center; color: #f44336;">Erro ao carregar o feed. Tente novamente mais tarde.</p>';
                }
            }

            function renderPosts(posts) {
                if (posts.length === 0) {
                    feedContainer.innerHTML = '<p style="text-align: center; color: #aaa;">Nenhum post no feed ainda.</p>';
                    return;
                }
                
                posts.forEach(post => {
                    // =================== INÍCIO DAS ALTERAÇÕES ===================

                    // 1. Define uma imagem padrão segura se o autor não tiver avatar
                    const avatarUrl = post.autor.profile_image_url || '{{ url_for("inicio_assets", filename="iconeUser.png") }}';

                    const postElement = document.createElement('div');
                    // 2. Usa a classe 'post-card' do seu CSS para o estilo correto
                    postElement.className = 'post-card'; 
                    
                    // 3. Constrói o HTML com os nomes de campos CORRETOS e a estrutura do seu CSS
                    postElement.innerHTML = `
                        <div class="post-header">
                            <img src="${avatarUrl}" alt="Avatar de ${post.autor.nome}" class="author-avatar">
                            <div class="author-info">
                                <p class="author-name">${post.autor.nome}</p>
                                <p class="post-timestamp">${formatarData(post.created_at)}</p>
                            </div>
                        </div>
                        <div class="post-content">
                            <p>${post.legenda}</p>
                        </div>
                        ${post.imagem_url ? `<img src="${post.imagem_url}" alt="Imagem do post" class="post-image">` : ''}
                    `;
                    // 4. Removido o 'post-footer' com Likes e Comentários que causava "undefined"

                    // =================== FIM DAS ALTERAÇÕES ===================

                    feedContainer.appendChild(postElement);
                });
            }

            loadPosts();
        });
    