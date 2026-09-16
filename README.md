# TaskFlow

TaskFlow é um mural acadêmico preparado como **PUBLIC ALPHA** em arquitetura same-origin: um único serviço entrega React e FastAPI no mesmo domínio.

## Arquitetura

```text
Browser ─HTTPS→ FastAPI ─┬─ /api/* → SQLAlchemy → PostgreSQL
                         ├─ /assets → frontend compilado
                         └─ demais rotas → React SPA
```

Em desenvolvimento, Vite (`localhost:5173`) encaminha `/api` ao FastAPI (`localhost:8000`). Em produção, FastAPI serve `frontend/dist`. Uma `/api/*` inexistente continua 404 JSON, nunca fallback SPA.

## Desenvolvimento local

Requisitos: Python 3.11+ e Node.js 20+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements-dev.txt
Copy-Item .env.example backend\.env
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Em outro terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Aplicação: `http://localhost:5173`; docs: `http://localhost:8000/docs`; saúde: `http://localhost:8000/api/health`. SQLite é permitido somente em desenvolvimento/testes e recusado em produção.

## Autenticação e banco

A sessão JWT fica exclusivamente no cookie `taskflow_session`: `HttpOnly`, `SameSite=Lax`, `path=/`, expiração configurável e `Secure` obrigatório em produção. Nada é salvo em `localStorage` ou `sessionStorage`. `ADMIN` administra tarefas/convites; `MEMBER` é somente leitura.

SQLAlchemy 2 usa SQLite local ou PostgreSQL com psycopg 3. O container executa `python -m alembic upgrade head` antes do servidor. Isso é adequado a uma instância; antes de escalar, mova migrations para uma etapa única de release.

Crie o primeiro administrador explicitamente:

```bash
python -m app.cli create-admin --email admin@exemplo.com --name "Administrador"
```

A senha é solicitada sem eco. `TASKFLOW_ADMIN_PASSWORD` deve ser usado apenas em automação controlada e nunca persistido.

## Testes

```powershell
cd backend
python -m pytest
python -m ruff check .
cd ..\frontend
npm test
npm run test:coverage
npm run lint
npm run build
npm run test:e2e
```

O E2E usa SQLite temporário e não acessa APIs Google.

## Produção local com PostgreSQL

Crie um `.env` local ignorado pelo Git:

```env
POSTGRES_PASSWORD=uma-senha-local-forte
SECRET_KEY=um-segredo-local-com-pelo-menos-32-caracteres
```

Execute `docker compose up --build`. A stack oferece PostgreSQL, migrations e aplicação completa em `http://localhost:8000`. O Compose usa configuração local (`ENVIRONMENT=development` e cookie sem `Secure`) apenas para permitir autenticação por HTTP; a imagem e a configuração documentada do Render continuam exigindo HTTPS e cookie seguro em produção.

## Produção

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://usuario:senha@host/banco
SECRET_KEY=<segredo aleatório forte>
COOKIE_SECURE=true
FRONTEND_URL=https://seu-dominio
CORS_ORIGINS=https://seu-dominio
ENABLE_GOOGLE_INTEGRATION=false
GOOGLE_CALENDAR_SYNC_ENABLED=false
```

URLs `postgresql://`/`postgres://` são normalizadas para psycopg. Gere o segredo com `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Produção recusa segredo padrão, SQLite, cookie inseguro, frontend sem HTTPS e CORS curinga; docs públicas e debug ficam desativados.

## Segurança do alpha

- Validação estrita de `Origin` presente em POST/PUT/PATCH/DELETE e CORS restritivo.
- Rate limit local por IP para login e cadastro por convite.
- CSP sem `unsafe-eval`, frame protection, `nosniff`, Referrer/Permissions Policy e HSTS em produção.
- `style-src 'unsafe-inline'` é a exceção documentada: React calcula larguras de barras/progresso via atributo `style`; scripts inline permanecem proibidos.
- O IP vem do Uvicorn; forwarded headers só são aceitos dos proxies configurados em `FORWARDED_ALLOW_IPS`.

O rate limit local não escala horizontalmente; use armazenamento compartilhado antes de adicionar instâncias.

## Deploy

O alvo é um Render Web Service Docker e Render PostgreSQL. Veja [DEPLOYMENT.md](DEPLOYMENT.md). O código não depende de `onrender.com` e aceita domínio próprio.

## Experimental / fora do escopo atual

Google Calendar e Classroom Bridge estão preservados, mas desligados por `ENABLE_GOOGLE_INTEGRATION=false`: rotas não são registradas, polling não inicia, sidebar não mostra integrações e secrets Google não são exigidos. Para desenvolvimento futuro da UI, compile também com `VITE_ENABLE_GOOGLE_INTEGRATION=true`.

## Limitações

- Rate limit e polling são locais à instância.
- Migrations rodam no startup.
- Compose não inclui proxy TLS.
- Google/Classroom permanecem experimentais e fora da primeira publicação.
