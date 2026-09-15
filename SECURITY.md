# Segurança

## Dados e autenticação

O FinTrack utiliza Supabase Auth para autenticação e PostgreSQL para persistência.

As tabelas financeiras usam Row Level Security (RLS), vinculando registros ao `user_id` autenticado.

## Credenciais

Nunca publique:

- `.streamlit/secrets.toml`
- Secret keys do Supabase
- `service_role`
- senhas
- tokens de sessão

A aplicação deve utilizar somente a Publishable key.

## Senhas

O formulário de cadastro do FinTrack exige:

- mínimo de 12 caracteres;
- pelo menos uma letra minúscula;
- pelo menos uma letra maiúscula;
- pelo menos um número;
- pelo menos um símbolo.

## Capturas de tela

Antes de adicionar imagens ao repositório, remova ou substitua:

- e-mails pessoais;
- valores financeiros reais;
- nomes que identifiquem pessoas;
- senhas;
- tokens ou chaves.

## Relato de vulnerabilidades

Se este projeto evoluir para uso por terceiros em produção, adicione um canal privado de contato para relatos de segurança em vez de abrir detalhes sensíveis em Issues públicas.
