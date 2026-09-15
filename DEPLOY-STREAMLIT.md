# Deploy no Streamlit Community Cloud

1. Crie/configure o projeto Supabase.
2. Execute `supabase_setup.sql` no SQL Editor.
3. No Streamlit Community Cloud, clique em **Criar aplicativo**.
4. Selecione:
   - Repositório: `euluanalima/fintrack`
   - Branch: `main`
   - Arquivo principal: `app.py`
5. Em **Advanced settings > Secrets**, adicione:

```toml
[supabase]
url = "https://SEU-PROJETO.supabase.co"
publishable_key = "sb_publishable_..."
```

6. Faça o deploy.

O arquivo real de secrets não deve ser commitado no GitHub.
