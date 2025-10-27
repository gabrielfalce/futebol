// Aguarda o DOM carregar completamente
document.addEventListener('DOMContentLoaded', () => {

    // --- LÓGICA PARA O BOTÃO DE CRIAR PUBLICAÇÃO ---
    const createPostBtn = document.getElementById('createPostBtn');

    if (createPostBtn) {
        createPostBtn.addEventListener('click', () => {
            // Ação temporária: exibe um alerta.
            // No futuro, isso pode abrir um modal ou redirecionar para uma página de criação.
            alert('Funcionalidade para criar/editar publicação será implementada aqui!');
        });
    }

    // --- LÓGICA PARA O MODAL DE CORTE DE IMAGEM (DA PÁGINA editar_perfil.html) ---
    // Esta parte do código só funcionará se os elementos existirem na página.
    // Seleção de elementos do DOM
    const openModalButton = document.getElementById('openModalButton'); // Este ID não existe nos arquivos, mantido por compatibilidade.
    const cropModal = document.getElementById('cropModal');
    const closeModalButton = document.getElementById('closeModalButton');
    const imageInput = document.getElementById('imageInput');
    const image = document.getElementById('image');
    const cropButton = document.getElementById('cropButton'); // Este ID não existe nos arquivos, mantido por compatibilidade.
    const preview = document.getElementById('preview');
    let cropper = null;

    // Função para abrir o modal
    function openModal() {
        if (cropModal) cropModal.style.display = 'flex';
    }

    // Função para fechar o modal e limpar estados
    function closeModal() {
        if (cropModal) cropModal.style.display = 'none';
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        if (image) image.src = '';
        if (cropButton) cropButton.style.display = 'none';
        if (imageInput) imageInput.value = '';
    }

    // Função para carregar e inicializar o Cropper.js
    function loadImage(event) {
        const file = event.target.files[0];
        if (file && image) {
            const reader = new FileReader();
            reader.onload = (e) => {
                image.src = e.target.result;
                image.style.display = 'block';
                if (cropButton) cropButton.style.display = 'block';

                if (cropper) cropper.destroy();
                
                cropper = new Cropper(image, {
                    aspectRatio: 1,
                    viewMode: 1,
                    autoCropArea: 0.8,
                    responsive: true,
                });
            };
            reader.readAsDataURL(file);
        }
    }

    // Função para cortar a imagem (se o botão existir)
    function cropImage() {
        if (cropper && preview) {
            const canvas = cropper.getCroppedCanvas({ width: 512, height: 512 });
            preview.src = canvas.toDataURL('image/jpeg');
            closeModal(); // Fecha o modal após o corte
        }
    }

    // Adiciona eventos apenas se os elementos existirem
    if (openModalButton) openModalButton.addEventListener('click', openModal);
    if (closeModalButton) closeModalButton.addEventListener('click', closeModal);
    if (imageInput) imageInput.addEventListener('change', loadImage);
    if (cropButton) cropButton.addEventListener('click', cropImage);
});