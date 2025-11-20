**Arquivo Alterado: telasHTML\ArquivosGerais\TelaChat\chat.js**
```javascript
// chat.js
// Aguarda o DOM carregar completamente antes de executar o script
document.addEventListener('DOMContentLoaded', () => {

        // --- 1. INICIALIZAÇÃO E ELEMENTOS DO DOM ---
        const chatBody = document.getElementById('chat-body');
        const messageForm = document.getElementById('message-form');
        const messageInput = document.getElementById('message-input');
    
        // Inicializa o cliente Supabase com as credenciais passadas pelo Flask
        // As constantes (SUPABASE_URL, SUPABASE_KEY, REMETENTE_ID, DESTINATARIO_ID) são definidas no bloco <script> do chat.html
        // CORREÇÃO: Usar o objeto global 'supabase' (fornecido pelo CDN) para criar o cliente
        const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    
        // --- 2. FUNÇÕES AUXILIARES ---
    
        /**
         * Cria e adiciona um balão de mensagem na tela.
         * @param {object} message - O objeto da mensagem vindo do Supabase.
         */
        function addMessageToScreen(message) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('message-wrapper');
    
            // Define se a mensagem foi 'sent' (enviada) ou 'received' (recebida)
            // remetente_id deve ser um número, por isso usamos ===
            if (message.remetente_id === REMETENTE_ID) {
                wrapper.classList.add('sent');
            } else {
                wrapper.classList.add('received');
            }
    
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.textContent = message.conteudo;
    
            wrapper.appendChild(messageDiv);
            chatBody.appendChild(wrapper);
    
            // Rola a tela para a última mensagem
            chatBody.scrollTop = chatBody.scrollHeight;
        }
    
        /**
         * Carrega o histórico de mensagens da API do Flask.
         */
        async function loadMessageHistory() {
            try {
                // Chama a API que criamos no app.py para buscar o histórico ordenado
                const response = await fetch(`/api/chat/historico/${DESTINATARIO_ID}`);
                if (!response.ok) {
                    throw new Error('Falha ao carregar histórico: ' + response.statusText);
                }
                const messages = await response.json();
                
                // Limpa o chat antes de adicionar o histórico
                chatBody.innerHTML = ''; 
                
                // Adiciona cada mensagem do histórico na tela
                messages.forEach(addMessageToScreen);
                
                // Garante que a rolagem final ocorra após carregar todas as mensagens
                chatBody.scrollTop = chatBody.scrollHeight;
    
            } catch (error) {
                console.error('Erro ao carregar histórico:', error);
                chatBody.innerHTML = '<p style="text-align:center; color: #ff4d4d; padding: 20px;">Não foi possível carregar as mensagens. Verifique a API do Flask e as chaves Supabase.</p>';
            }
        }
    
        /**
         * Envia uma nova mensagem para o banco de dados do Supabase.
         * @param {string} content - O texto da mensagem a ser enviada.
         */
        async function sendMessage(content) {
            // Objeto da mensagem que será inserido no banco
            const message = {
                remetente_id: REMETENTE_ID,
                destinatario_id: DESTINATARIO_ID,
                conteudo: content
            };
    
            // Usa o cliente Supabase para inserir a nova mensagem na tabela 'mensagens'
            // CORREÇÃO: Usar o cliente local 'supabaseClient'
            const { error } = await supabaseClient.from('mensagens').insert([message]);
    
            if (error) {
                console.error('Erro ao enviar mensagem:', error);
                alert('Não foi possível enviar a mensagem. Verifique a permissão de INSERT no Supabase.');
            } else {
                // Se o insert for bem-sucedido, adicione a mensagem à sua tela
                // (a tela do outro usuário será atualizada pelo Realtime)
                addMessageToScreen(message);
            }
        }
    
    
        // --- 3. EVENT LISTENERS E EXECUÇÃO INICIAL ---
    
        // Listener para o envio do formulário
        messageForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Impede o recarregamento da página
            const content = messageInput.value.trim(); // Pega o texto e remove espaços em branco
    
            if (content) {
                sendMessage(content); // Envia a mensagem
                messageInput.value = ''; // Limpa o campo de texto
            }
        });
    
        // --- 4. CONFIGURAÇÃO REALTIME ---
    
        // Listener do Supabase Realtime: "ouve" por novas inserções na tabela 'mensagens'
        // O filtro: escutar apenas mensagens onde EU sou o destinatário (REMETENTE_ID)
        supabaseClient.channel('chat-conversas') 
            .on('postgres_changes', { 
                event: 'INSERT', 
                schema: 'public', 
                table: 'mensagens',
                // Filtra para receber apenas mensagens destinadas a esta sessão
                filter: `destinatario_id=eq.${REMETENTE_ID}` 
            }, (payload) => {
                const newMessage = payload.new;
    
                // Verifica se o remetente é o usuário com quem estou conversando (DESTINATARIO_ID)
                // Apenas exibe se a mensagem for do OUTRO usuário
                if (newMessage.remetente_id === DESTINATARIO_ID) {
                    addMessageToScreen(newMessage); // Adiciona a nova mensagem na tela em tempo real
                }
            })
            .subscribe(); // Inicia a "escuta"
    
        // Carrega o histórico de mensagens assim que a página é aberta
        loadMessageHistory();
    
    // Desinscrever-se ao sair da página (boa prática)
    window.addEventListener('beforeunload', () => {
        supabaseClient.removeAllChannels();
    });
});