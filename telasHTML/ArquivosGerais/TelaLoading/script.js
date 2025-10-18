// Espera o conteúdo da página carregar completamente
window.onload = function() {
    console.log('Página de loading carregada. Iniciando temporizador...');

    // Lê o tempo do atributo data-tempo-loading do body, ou usa 2000ms como padrão
    const tempoDeLoading = parseInt(document.body.getAttribute('data-tempo-loading')) || 2000;

    setTimeout(function() {
        console.log('Tempo de loading expirado. Redirecionando para /inicio...');
        // Redireciona para a rota Flask /inicio, em vez de caminho relativo
        window.location.href = "/inicio";
    }, tempoDeLoading);
};
