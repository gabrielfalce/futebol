<script type="module">
    import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

    const SUPABASE_URL = 'https://ulbaklykimxpsdrtkqet.supabase.co'
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVsYmFrbHlraW14cHNkcnRrcWV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjc0MjcsImV4cCI6MjA3MzkwMzQyN30.A3_WLF3cNstQtXcOr2Q3OJCvTYqBQe7wmmXHc_WCqAk'
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY )

    const CADASTRO_FUNCTION_URL = 'https://ulbaklykimxpsdrtkqet.supabase.co/functions/v1/cadastro';

    function showToast(message, isSuccess = false ) {
        const toast = document.getElementById("toast-notification");
        toast.textContent = message;
        toast.style.backgroundColor = isSuccess ? '#28a745' : '#dc3545';
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 4000);
    }

    document.getElementById('cadastro-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Cadastrando...';

        try {
            // ETAPA 1: Criar o usuário com supabase.auth.signUp
            const { data: authData, error: authError } = await supabase.auth.signUp({
                email: data.email,
                password: data.senha,
            });

            if (authError) throw authError;
            if (!authData.session) throw new Error("Falha ao criar sessão. Verifique seu email para confirmação.");

            // ETAPA 2: Chamar a Edge Function para criar o perfil
            // O token da sessão é enviado automaticamente pelo cliente Supabase
            const response = await fetch(CADASTRO_FUNCTION_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authData.session.access_token}` // Envia o token do novo usuário
                },
                body: JSON.stringify(data) // Envia os dados extras (nome, cidade, etc.)
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.error);

            showToast('Cadastro realizado com sucesso! Verifique seu email para confirmar.', true);
            form.reset();
            setTimeout(() => { window.location.href = '/index.html'; }, 3000);

        } catch (error) {
            showToast(error.message, false);
            submitButton.disabled = false;
            submitButton.textContent = 'Cadastrar';
        }
    });
</script>
