# TaskFlow

TaskFlow é um mural compartilhado para organizar atividades acadêmicas por prazo, prioridade, status e categoria. O protótipo CLI original foi preservado na raiz; o MVP full stack está em `backend/` e `frontend/`.

## Funcionalidades

- Login seguro com papéis `ADMIN` e `MEMBER`.
- CRUD administrativo; membros possuem acesso somente de leitura.
- Dashboard, busca, filtros, ordenação por urgência, calendário e estatísticas.
- Indicadores dinâmicos de prazo e layout escuro responsivo.

## Arquitetura

O backend usa FastAPI, SQLAlchemy 2, Pydantic, Alembic e SQLite. Rotas, schemas, modelos, repositórios, serviços e segurança ficam separados em `backend/app`. O frontend usa React, TypeScript e Vite.

Datas de prazo são `date`; timestamps são UTC. A ordenação centralizada prioriza pendentes atrasadas, menor prazo, maior prioridade e criação mais antiga.

## Requisitos e instalação

- Python 3.11+
- Node.js 20+

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements-dev.txt
Copy-Item .env.example .env
cd frontend
npm install
```

Defina uma `SECRET_KEY` aleatória e longa no `.env`.

## Banco e dados iniciais

A partir de `backend/`:

```powershell
alembic upgrade head
python -m app.cli create-admin --email admin@exemplo.com --name "Administrador"
python -m app.cli seed
```

O primeiro comando administrativo solicita a senha sem exibi-la. Para automação local, use temporariamente `TASKFLOW_ADMIN_PASSWORD`; nunca versione esse valor.

## Execução

Em dois terminais:

```powershell
cd backend
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm run dev
```

Acesse `http://localhost:5173`; a API documentada fica em `http://localhost:8000/docs`.

## Testes e qualidade

```powershell
cd backend
pytest
ruff check .
```

```powershell
cd frontend
npm test
npm run lint
npm run build
```

## Estrutura

```text
backend/app/       API, domínio, persistência, serviços e segurança
backend/alembic/   migrations versionadas
backend/tests/     testes de API e regras críticas
frontend/src/      interface React organizada por responsabilidade
models/, services/ protótipo CLI original preservado
```

## Segurança e limitações

Senhas usam Argon2id e nunca saem da API. A sessão JWT fica em cookie `HttpOnly`, `SameSite=Lax` e deve usar `Secure=true` em produção. RBAC é validado no backend. Segredos e bancos locais são ignorados pelo Git.

O MVP não inclui permissões por tarefa, notificações, integrações externas, uploads, OAuth ou sincronização offline. Para produção, use HTTPS, CORS explícito, uma chave forte e PostgreSQL.
