// Localização: telasHTML/ArquivosGerais/TelaAvisoManuteção/scriptManu.js

document.addEventListener('DOMContentLoaded', () => {
    const backButton = document.getElementById('backButton');

    if (backButton) {
        // Adiciona um evento de clique ao botão para voltar à página anterior no histórico do navegador.
        backButton.addEventListener('click', () => {
            window.history.back();
        });
    }
});