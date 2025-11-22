// script.js – versão corrigida e final
document.addEventListener('DOMContentLoaded', () => {

    const createPostBtn = document.getElementById('createPostBtn');
    const postModal = document.getElementById('postModal');
    const closePostModalBtn = document.getElementById('closePostModalBtn');
    const postForm = document.getElementById('postForm');

    // Abrir modal
    if (createPostBtn) {
        createPostBtn.addEventListener('click', () => {
            postModal.style.display = 'flex';
        });
    }

    // Fechar modal (botão X ou clicar fora)
    if (closePostModalBtn) {
        closePostModalBtn.addEventListener('click', () => {
            postModal.style.display = 'none';
        });
    }
    window.addEventListener('click', (e) => {
        if (e.target === postModal) {
            postModal.style.display = 'none';
        }
    });

    // Enviar formulário para a rota correta do Flask
    if (postForm) {
        postForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(postForm);

            try {
                const response = await fetch('/criar_post', {
                    method: 'POST',
                    body: formData
                });

                if (response.redirected) {
                    // Seu Flask faz redirect após sucesso → só seguir
                    window.location.href = response.url;
                } else {
                    const text = await response.text();
                    alert('Erro ao publicar. Verifique o console.');
                    console.error(text);
                }
            } catch (err) {
                console.error(err);
                alert('Erro de rede');
            }
        });
    }
});