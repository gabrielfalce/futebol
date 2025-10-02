// Localização: telasHTML/STATIC/TelaLoading/script.js

// Espera o conteúdo da página carregar completamente
window.onload = function() {
    // --- ALTERAÇÃO 1: Tempo de espera ajustado para 1.5 segundos ---
    const tempoDeLoading = 1500;

    // Função que será executada após o tempo de espera
    setTimeout(function() {
        // --- ALTERAÇÃO 2: Redireciona para a ROTA /inicio do Flask ---
        // Em vez de um arquivo, apontamos para a rota que renderiza a tela inicial.
        window.location.href = "/inicio";
    }, tempoDeLoading);
};
