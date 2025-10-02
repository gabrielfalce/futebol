// Localização: telasHTML/STATIC/TelaLoading/script.js

// Espera o conteúdo da página carregar completamente
window.onload = function() {
    // Lê o tempo do atributo data-tempo-loading do body, ou usa 2000ms como padrão
    const tempoDeLoading = parseInt(document.body.getAttribute('data-tempo-loading')) || 2000;

    setTimeout(function() {
        // Redireciona para a tela inicial
        window.location.href = "../TelaInicial/TelaInicial.html";
    }, tempoDeLoading);
};
