// Aguarda o DOM carregar completamente
document.addEventListener('DOMContentLoaded', () => {

    // --- LÓGICA PARA O MODAL DE CRIAR PUBLICAÇÃO ---
    const createPostBtn = document.getElementById('createPostBtn');
    const postModal = document.getElementById('postModal');
    const closePostModalBtn = document.getElementById('closePostModalBtn');
    const postForm = document.getElementById('postForm');

    // Abre o modal ao clicar no botão de criar post
    if (createPostBtn && postModal) {
        createPostBtn.addEventListener('click', () => {
            postModal.style.display = 'flex';
        });
    }

    // Fecha o modal ao clicar no botão de fechar
    if (closePostModalBtn && postModal) {
        closePostModalBtn.addEventListener('click', () => {
            postModal.style.display = 'none';
        });
    }

    // Lida com o envio do formulário de postagem
    if (postForm) {
        postForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Impede o recarregamento da página

            const postContent = document.getElementById('postContent').value;
            const postImage = document.getElementById('postImage').files[0];

            // Ação temporária: exibe os dados no console.
            // No futuro, aqui você faria uma requisição `fetch` para o seu backend.
            console.log('Legenda:', postContent);
            console.log('Imagem:', postImage);

            alert('Publicação enviada! (Verifique o console para os dados)');
            postModal.style.display = 'none'; // Fecha o modal após o envio
            postForm.reset(); // Limpa o formulário
        });
    }
});