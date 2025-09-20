import { createClient } from '@supabase/supabase-js';

// As variáveis de ambiente são acessadas de forma diferente dependendo do seu framework (Next.js, React, etc.)
// Para Next.js, por exemplo, seria process.env.NEXT_PUBLIC_SUPABASE_URL
// Certifique-se de que o prefixo `NEXT_PUBLIC_` esteja correto para o seu ambiente Vercel/framework
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Verifique se as variáveis foram carregadas corretamente
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Erro: Variáveis de ambiente do Supabase não configuradas corretamente.');
  // Em um ambiente de produção, você pode querer lançar um erro ou ter um fallback
}

// Inicializa o cliente Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
