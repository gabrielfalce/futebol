// Forçando o redeploy em 02/11/2025 - v2
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

Deno.serve(async (req ) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Pega a chave de serviço do cabeçalho da requisição
    const serviceKey = req.headers.get('Authorization')?.replace('Bearer ', '');
    if (!serviceKey) {
      throw new Error('Chave de serviço não fornecida.');
    }

    const { nome, email, senha, cidade, posicao, nascimento, numero_camisa, numero_telefone } = await req.json();

    if (!email || !senha || !nome) {
      throw new Error("Nome, email e senha são obrigatórios.");
    }

    // Cria um cliente Supabase NORMAL (sem admin)
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    );

    // 1. Cria o usuário
    const { data: { user }, error: authError } = await supabase.auth.admin.createUser({
      email: email,
      password: senha,
      email_confirm: true,
    });

    if (authError) throw authError;
    if (!user) throw new Error("Falha ao criar o usuário na autenticação.");

    // 2. Insere o perfil, passando a chave de serviço no cabeçalho
    const { error: profileError } = await supabase
      .from('profiles')
      .insert({
        id: user.id,
        nome_completo: nome,
        cidade: cidade,
        posicao: posicao,
        nascimento: nascimento,
        numero_camisa: numero_camisa,
        numero_telefone: numero_telefone,
      })
      // Passa a autorização explicitamente
      .rpc('service_role', {}, { headers: { Authorization: `Bearer ${serviceKey}` } });


    if (profileError) {
      await supabase.auth.admin.deleteUser(user.id, { headers: { Authorization: `Bearer ${serviceKey}` } });
      throw profileError;
    }

    return new Response(JSON.stringify({
      message: 'Cadastro realizado com sucesso! Verifique seu email.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 201,
    });

  } catch (error) {
    return new Response(JSON.stringify({
      error: error.message
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    });
  }
});
