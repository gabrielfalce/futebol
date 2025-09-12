// Seleção de elementos do DOM
const openModalButton = document.getElementById('openModalButton');
const cropModal = document.getElementById('cropModal');
const closeModalButton = document.getElementById('closeModalButton');
const imageInput = document.getElementById('imageInput');
const image = document.getElementById('image');
const cropButton = document.getElementById('cropButton');
const preview = document.getElementById('preview');
let cropper = null;

// Função para abrir o modal
function openModal() {
    cropModal.style.display = 'flex';
}

// Função para fechar o modal e limpar estados
function closeModal() {
    cropModal.style.display = 'none';
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    image.src = '';
    cropButton.style.display = 'none';
    imageInput.value = '';
    // Não limpe o preview aqui!
}

// Função para carregar e inicializar o Cropper.js
function loadImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            image.src = e.target.result;
            image.style.display = 'block';
            cropButton.style.display = 'block';

            // Inicializa o Cropper.js
            if (cropper) {
                cropper.destroy();
            }
            cropper = new Cropper(image, {
                aspectRatio: 1, // Proporção quadrada (como no WhatsApp)
                viewMode: 1, // Restringe o corte dentro da imagem
                autoCropArea: 0.8, // Define a área inicial de corte
                responsive: true,
                zoomable: true,
                scalable: true,
                movable: true,
            });
        };
        reader.readAsDataURL(file);
    }
}

// Função para cortar a imagem
function cropImage() {
    if (cropper) {
        // Obtém a imagem cortada como um canvas
        const canvas = cropper.getCroppedCanvas({
            width: 512, // Define a largura da imagem cortada
            height: 512, // Define a altura da imagem cortada
        });

        // Exibe a imagem cortada na prévia
        preview.src = canvas.toDataURL('image/jpeg');
        preview.style.display = 'block';

        // Destroi o cropper após o corte
        cropper.destroy();
        cropper = null;
        cropButton.style.display = 'none';
    }
}

// Adiciona eventos
openModalButton.addEventListener('click', openModal);
closeModalButton.addEventListener('click', closeModal);
imageInput.addEventListener('change', loadImage);
cropButton.addEventListener('click', cropImage);