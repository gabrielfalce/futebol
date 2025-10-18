// Espera o conteúdo da página carregar completamente
window.onload = function() {
    console.log('Página de loading carregada. Iniciando temporizador...');

    // Lê o tempo do atributo data-tempo-loading do body, ou usa 5000ms como padrão
    const tempoDeLoading = parseInt(document.body.getAttribute('data-tempo-loading')) || 5000;

    // Verifica se há uma mensagem de sucesso (opcional, se implementado no backend)
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get('success');

    if (success === 'true') {
        console.log('Cadastro confirmado. Redirecionando para /inicio...');
        window.location.href = "/inicio";
    } else {
        // Temporizador como fallback
        setTimeout(function() {
            console.log('Tempo de loading expirado. Redirecionando para /inicio...');
            window.location.href = "/inicio";
        }, tempoDeLoading);
    }
};
