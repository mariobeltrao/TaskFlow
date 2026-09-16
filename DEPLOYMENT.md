# Deploy manual no Render

O resultado é um Web Service público único e um PostgreSQL separado. O navegador acessa somente o domínio do Web Service. Revise custos antes de criar recursos e nunca salve secrets no Git.

## Procedimento

1. No dashboard Render, escolha **New > PostgreSQL**, defina nome/região/plano conscientemente e copie sua URL interna.
2. Escolha **New > Web Service** e conecte `mariobeltrao/TaskFlow`.
3. Selecione runtime **Docker**, `Dockerfile` e contexto na raiz. Build/start já estão na imagem.
4. Configure health check `/api/health`.
5. Cadastre:

   ```env
   ENVIRONMENT=production
   DATABASE_URL=<URL interna do PostgreSQL>
   SECRET_KEY=<segredo forte>
   COOKIE_SECURE=true
   FRONTEND_URL=https://URL_REAL_DO_TASKFLOW
   CORS_ORIGINS=https://URL_REAL_DO_TASKFLOW
   ENABLE_GOOGLE_INTEGRATION=false
   GOOGLE_CALENDAR_SYNC_ENABLED=false
   FORWARDED_ALLOW_IPS=<proxy confiável conforme documentação da plataforma>
   ```

6. Gere `SECRET_KEY` fora do Render: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Não configure secrets Google.
7. Conecte `DATABASE_URL` à URL interna fornecida pelo banco.
8. Confirme novamente o health check `/api/health`.
9. Autorize manualmente o primeiro deploy.
10. Nos logs, confirme `alembic upgrade head` e o startup do Uvicorn, sem dados sensíveis.
11. Acesse `/api/health`; deve retornar `{"status":"ok"}`.
12. Abra `/`, `/login` e atualize `/app` diretamente. `/api/inexistente` deve ser 404 JSON.
13. No Shell do serviço, crie o ADMIN:

    ```bash
    python -m app.cli create-admin --email admin@seu-dominio.com --name "Administrador"
    ```

14. Teste o login com uma senha forte informada sem eco.
15. Crie convite: `python -m app.cli create-member-invite --email aluno@exemplo.com --expires-days 7`.
16. Entregue o código por canal seguro e cadastre o MEMBER em `/first-access`.
17. Como ADMIN, teste criar, editar, concluir e excluir tarefas.
18. Como MEMBER, confirme leitura e ausência/bloqueio de todas as mutações.

Confira que Integrações não aparece e não existem chamadas Google. O primeiro alpha pode usar `*.onrender.com`. Para domínio próprio, configure DNS/TLS no serviço e atualize `FRONTEND_URL` e `CORS_ORIGINS` para a origem HTTPS definitiva.

## Limites operacionais

O alpha pressupõe uma instância. Antes de escalar, execute Alembic em etapa única de release e mova o rate limit para Redis ou equivalente. Logs nunca devem conter senha, JWT, cookies, SECRET_KEY, DATABASE_URL, código completo de convite ou tokens Google.
