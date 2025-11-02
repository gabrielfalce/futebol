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
        postForm.addEventListener('submit', async (event) => { // Adicionado 'async'
            event.preventDefault(); // Impede o recarregamento da página

            const postContent = document.getElementById('postContent').value;
            const postImage = document.getElementById('postImage').files[0];

            // ALTERAÇÃO: Substituído o console.log pela lógica de envio para o backend.
            
            // 1. Criar um objeto FormData para enviar texto e arquivo
            const formData = new FormData();
            formData.append('legenda', postContent);
            if (postImage) {
                formData.append('postImage', postImage);
            }

            try {
                // 2. Enviar os dados para a API usando fetch
                const response = await fetch('/api/posts', {
                    method: 'POST',
                    body: formData, // Não precisa de 'headers' quando se usa FormData
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    alert('Publicação criada com sucesso!');
                    // Recarrega a página para mostrar o novo post
                    window.location.reload(); 
                } else {
                    // Mostra o erro retornado pelo servidor
                    alert(`Erro ao criar publicação: ${result.error || 'Erro desconhecido'}`);
                }

            } catch (error) {
                console.error('Erro na requisição fetch:', error);
                alert('Ocorreu um erro de rede ao tentar publicar. Verifique o console.');
            } finally {
                // Independentemente do resultado, fecha o modal e limpa o formulário
                postModal.style.display = 'none';
                postForm.reset();
            }
        });
    }
});
