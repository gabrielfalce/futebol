// Importa a função para criar o cliente Supabase
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// =======================
// CONFIGURAÇÃO
// =======================
const SUPABASE_URL = 'https://ulbaklykimxpsdrtkqet.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVsYmFrbHlraW14cHNkcnRrcWV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjc0MjcsImV4cCI6MjA3MzkwMzQyN30.A3_WLF3cNstQtXcOr2Q3OJCvTYqBQe7wmmXHc_WCqAk'
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY )
const CADASTRO_FUNCTION_URL = 'https://ulbaklykimxpsdrtkqet.supabase.co/functions/v1/cadastro';

// =======================
// FUNÇÕES DE UTILIDADE
// =======================
function showToast(message, isSuccess = false ) {
    const toast = document.getElementById("toast-notification");
    if (!toast) return; // Não faz nada se o elemento toast não existir
    toast.textContent = message;
    toast.style.backgroundColor = isSuccess ? '#28a745' : '#dc3545';
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 5000); // Aumentado o tempo para 5s
}

// =======================
// LÓGICA PRINCIPAL DO FORMULÁRIO
// =======================
// Garante que o código só roda depois que a página carregou completamente
document.addEventListener('DOMContentLoaded', () => {
    const cadastroForm = document.getElementById('cadastro-form');
    if (!cadastroForm) return; // Para a execução se o formulário não for encontrado

    cadastroForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const submitButton = form.querySelector('button[type="submit"]');
        
        submitButton.disabled = true;
        submitButton.textContent = 'Cadastrando...';

        try {
            // -----------------------------------------------------------------
            // ETAPA 1: Criar o usuário no sistema de autenticação da Supabase
            // -----------------------------------------------------------------
            const { data: authData, error: authError } = await supabase.auth.signUp({
                email: data.email,
                password: data.senha,
            });

            if (authError) {
                // Se o erro for "User already registered", mostra uma mensagem amigável
                if (authError.message.includes("User already registered")) {
                    throw new Error("Este email já está cadastrado.");
                }
                throw authError;
            }
            
            if (!authData.user) {
                 throw new Error("Não foi possível criar o usuário. Verifique os dados e tente novamente.");
            }
            
            // Pega o token de acesso da sessão. É ESSENCIAL para a próxima etapa.
            const accessToken = authData.session?.access_token;

            // Se a confirmação de email estiver ativa, o `accessToken` pode ser nulo.
            // Nesse caso, o usuário foi criado, mas não podemos criar o perfil ainda.
            if (!accessToken) {
                showToast('Usuário criado! Verifique seu email para confirmar a conta antes de fazer login.', true);
                setTimeout(() => { window.location.href = '/index.html'; }, 4000);
                return; // Encerra a função aqui.
            }

            // -----------------------------------------------------------------
            // ETAPA 2: Chamar a Edge Function para criar o perfil do usuário
            // -----------------------------------------------------------------
            const response = await fetch(CADASTRO_FUNCTION_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // A LINHA MAIS IMPORTANTE: Envia o token de autorização
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify(data) // Envia os dados extras (nome, cidade, etc.)
            });

            const result = await response.json();
            if (!response.ok) {
                // Se a função retornar um erro, lança para o bloco catch
                throw new Error(result.error || `Erro no servidor: ${response.status}`);
            }

            showToast('Cadastro e perfil criados com sucesso! Redirecionando...', true);
            form.reset();
            setTimeout(() => { window.location.href = '/index.html'; }, 2000);

        } catch (error) {
            showToast(error.message, false);
            submitButton.disabled = false;
            submitButton.textContent = 'Cadastrar';
        }
    });
});
