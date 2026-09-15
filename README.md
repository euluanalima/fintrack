# FinTrack Online

Aplicação web responsiva para controle financeiro pessoal.

Esta versão mantém a interface do FinTrack PRO e adiciona:

- cadastro de usuário
- login com e-mail e senha
- recuperação de senha
- dados sincronizados online
- PostgreSQL via Supabase
- Row Level Security (RLS)
- isolamento dos dados por usuário
- configuração para Streamlit Community Cloud

## Arquitetura

```text
Celular / PC / Tablet
        ↓
Streamlit Cloud
        ↓
Supabase Auth
        ↓
PostgreSQL + RLS
```

## Primeira configuração

1. Leia `CONFIGURAR-SUPABASE.md`
2. Execute `supabase_setup.sql` no Supabase
3. Rode `CONFIGURAR SUPABASE.bat`
4. Abra `ABRIR FINTRACK.bat`

## Publicação

Leia:

`DEPLOY-STREAMLIT.md`

## Segurança

O aplicativo usa somente a **Publishable key** do Supabase.

As tabelas possuem Row Level Security e cada registro pertence a um `user_id`.

Nunca coloque uma **Secret key** no aplicativo ou no GitHub.
