// chat.js
// IMPORTANTE: As constantes SUPABASE_URL, SUPABASE_KEY, REMETENTE_ID, DESTINATARIO_ID são definidas no chat.html antes de carregar este script.

// Aguarda o DOM carregar completamente antes de executar o script
document.addEventListener('DOMContentLoaded', () => {

    // --- 1. INICIALIZAÇÃO E ELEMENTOS DO DOM ---
    const chatBody = document.getElementById('chat-body');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    
    // Inicializa o cliente Supabase com as credenciais
    // Depende do CDN ter sido carregado no HTML antes.
    const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    
    // --- 2. FUNÇÕES AUXILIARES ---
    
    /**
     * Cria e adiciona um balão de mensagem na tela.
     * @param {object} message - O objeto da mensagem vindo do Supabase.
     */
    function appendMessage(message) {
        // Remove a mensagem de "Carregando" se ainda estiver lá
        const loadingMessage = chatBody.querySelector('p');
        if (loadingMessage && loadingMessage.textContent.includes('Carregando')) {
            loadingMessage.remove();
        }

        const messageElement = document.createElement('div');
        const isSender = message.remetente_id === REMETENTE_ID;
        
        messageElement.classList.add('message', isSender ? 'sent' : 'received');
        
        const contentP = document.createElement('p');
        // CORREÇÃO: Usar 'conteudo' (Português) para ler da resposta do DB
        contentP.textContent = message.conteudo; 
        messageElement.appendChild(contentP);

        // Adicionar timestamp
        const timeSpan = document.createElement('span');
        // Usa `message.created_at` que deve vir do banco de dados (ISO string)
        const date = new Date(message.created_at);
        timeSpan.textContent = date.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
        timeSpan.classList.add('timestamp');
        messageElement.appendChild(timeSpan);
        
        chatBody.appendChild(messageElement);
        // Scroll automático para a mensagem mais recente
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    /**
     * Envia uma mensagem para o backend do Flask via API (POST).
     * @param {string} content - O conteúdo da mensagem.
     */
    async function sendMessage(content) {
        if (content.trim() === '') return;

        // Feedback imediato na tela do remetente (pré-confirmação)
        // CORREÇÃO: Usar 'conteudo' (Português) para a estrutura do objeto para ser consistente com appendMessage
        appendMessage({
            remetente_id: REMETENTE_ID,
            conteudo: content, // <-- ALTERADO DE 'content' PARA 'conteudo'
            created_at: new Date().toISOString() // Usa hora local para feedback instantâneo
        });

        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    destinatario_id: DESTINATARIO_ID,
                    content: content
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                console.error("Falha ao enviar mensagem:", data.error);
                alert("Erro ao enviar mensagem: " + data.error);
            }

        } catch (error) {
            console.error('Erro de rede ao enviar mensagem:', error);
            alert("Erro de comunicação com o servidor.");
        }
    }


    /**
     * Carrega o histórico de mensagens via API do Flask.
     */
    async function loadMessages() {
        try {
            const response = await fetch(`/chat/${DESTINATARIO_ID}`);

            const messages = await response.json();
            
            chatBody.innerHTML = ''; // Limpa "Carregando..."
            
            if (messages.length === 0) {
                chatBody.innerHTML = '<p style="text-align:center; color: #555;">Inicie uma nova conversa.</p>';
                return;
            }

            messages.forEach(appendMessage);

        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            chatBody.innerHTML = '<p style="text-align:center; color: red;">Não foi possível carregar o histórico de mensagens.</p>';
        }
    }
    
    // --- 3. LISTENERS DO DOM ---
    
    // Listener do formulário de envio de mensagem
    messageForm.addEventListener('submit', (e) => {
        e.preventDefault(); // Impede o recarregamento da página
        const content = messageInput.value.trim();
        
        if (content) {
            sendMessage(content); // Envia a mensagem via API Flask
            messageInput.value = ''; // Limpa o campo de texto
        }
    });

    // --- 4. CONFIGURAÇÃO REALTIME ---

    function subscribeToNewMessages() {
        // Cria um canal de chat único baseado nos IDs (menor_id_maior_id)
        const channelName = `chat_${Math.min(REMETENTE_ID, DESTINATARIO_ID)}_${Math.max(REMETENTE_ID, DESTINATARIO_ID)}`;
        
        const channel = supabaseClient.channel(channelName);
        
        // Ouve por novas mensagens na tabela 'mensagens'
        channel.on('postgres_changes', { 
            event: 'INSERT', 
            schema: 'public', 
            table: 'mensagens',
            // Filtra para receber apenas mensagens destinadas a esta sessão
            filter: `destinatario_id=eq.${REMETENTE_ID}` 
        }, (payload) => {
            const newMessage = payload.new;
            
            // Exibe apenas se o remetente for o usuário com quem estou conversando (DESTINATARIO_ID)
            if (newMessage.remetente_id === DESTINATARIO_ID) {
                appendMessage(newMessage);
            }
        }).subscribe();
            
        console.log('Subscrito ao canal de chat:', channelName);
    }


    // --- Inicialização ---
    // Remove qualquer canal anterior para evitar vazamento de memória
    supabaseClient.removeAllChannels(); 
    loadMessages(); // Carrega o histórico
    subscribeToNewMessages(); // Inicia a escuta Realtime
    
    // Desinscrever-se ao sair da página (boa prática)
    window.addEventListener('beforeunload', () => {
        supabaseClient.removeAllChannels();
    });
});