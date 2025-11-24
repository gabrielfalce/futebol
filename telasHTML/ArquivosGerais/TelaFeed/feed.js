// telasHTML/ArquivosGerais/TelaFeed/feed.js

document.addEventListener('DOMContentLoaded', () => {
    const feedContainer = document.getElementById('container-feed');
    const loadingSpinner = document.getElementById('spinner-carregamento');

    // Pega as URLs injetadas pelo Flask no body
    const API_URL = document.body.dataset.apiUrl;
    const DEFAULT_AVATAR = document.body.dataset.defaultAvatar;

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
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error('Falha na resposta da API');
            const posts = await response.json();

            loadingSpinner.style.display = 'none';
            renderPosts(posts);

        } catch (error) {
            console.error('Erro ao carregar posts:', error);
            loadingSpinner.style.display = 'none';
            feedContainer.innerHTML = '<p style="text-align:center;color:#f44336;">Erro ao carregar o feed.</p>';
        }
    }

    function renderPosts(posts) {
        if (posts.length === 0) {
            feedContainer.innerHTML = '<p style="text-align:center;color:#aaa;">Nenhum post no feed ainda.</p>';
            return;
        }

        posts.forEach(post => {
            const avatarUrl = post.autor.profile_image_url || DEFAULT_AVATAR;

            const postElement = document.createElement('div');
            postElement.className = 'post-card';
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
            feedContainer.appendChild(postElement);
        });
    }

    loadPosts();
});