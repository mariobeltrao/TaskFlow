# TaskFlow

TaskFlow é um mural compartilhado para organizar atividades acadêmicas por prazo, prioridade, status e categoria. O backend usa FastAPI, SQLAlchemy 2, Alembic e SQLite; o frontend usa React, TypeScript e Vite.

## Funcionalidades

- Landing pública e login com identidade visual própria.
- Sessão JWT em cookie `HttpOnly` e papéis `ADMIN` e `MEMBER`.
- Cadastro de alunos exclusivamente por convite individual de uso único.
- Dashboard, busca, filtros, calendário, estatísticas e CRUD administrativo.
- Integração administrativa de leitura com calendários Google selecionados.
- Sincronização manual, incremental, webhook HTTPS e polling opcional.

## Instalação

Requisitos: Python 3.11+ e Node.js 20+.

```powershell
cd "C:\caminho\para\TaskFlow"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements-dev.txt
Copy-Item .env.example backend\.env
cd frontend
npm install
```

Gere as chaves antes de iniciar:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use a primeira como `SECRET_KEY` e a segunda como `GOOGLE_TOKEN_ENCRYPTION_KEY` em `backend/.env`. Não reutilize nem versione essas chaves.

## Banco de dados

```powershell
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

As migrations preservam usuários e tarefas existentes. Tarefas antigas passam a ter origem `MANUAL`.

## Usuários e autorização

Existem apenas dois papéis:

- `ADMIN`: administra tarefas, convites e a integração Google Calendar.
- `MEMBER`: aluno estritamente somente leitura.

O backend protege `POST`, `PATCH` e `DELETE` de tarefas com `admin_user`; esconder controles no frontend é apenas uma camada de experiência.

### Criar administrador

```powershell
cd backend
..\.venv\Scripts\python.exe -m app.cli create-admin `
  --email admin@exemplo.com `
  --name "Administrador"
```

Administradores nunca são criados pelo endpoint público.

### Convidar um aluno

```powershell
..\.venv\Scripts\python.exe -m app.cli create-member-invite `
  --email aluno@exemplo.com `
  --expires-days 7
```

Se houver mais de um administrador, é possível informar `--admin-email admin@exemplo.com`. O código original é exibido uma única vez; o banco guarda somente seu hash SHA-256. Entregue o código ao aluno por um canal apropriado.

O aluno acessa `http://localhost:5173/first-access` e informa nome, o mesmo e-mail do convite, código, senha e confirmação. O endpoint `POST /api/auth/register-member` não aceita `role` e sempre cria `MEMBER`.

## Execução local

Terminal do backend:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Terminal do frontend:

```powershell
cd frontend
npm run dev
```

- Aplicação: `http://localhost:5173`
- OpenAPI: `http://localhost:8000/docs`
- Saúde: `http://localhost:8000/api/health`

## Google Calendar

A integração pertence ao administrador do TaskFlow. Alunos não conectam calendários pessoais. O escopo solicitado é somente `https://www.googleapis.com/auth/calendar.readonly`.

### 1. Preparar o Google Cloud

1. Crie ou selecione um projeto no [Google Cloud Console](https://console.cloud.google.com/).
2. Ative a [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com).
3. Configure a tela de consentimento OAuth.
4. Crie credenciais OAuth do tipo **Aplicativo da Web**.
5. Durante o desenvolvimento, adicione exatamente esta URI de redirecionamento autorizada:

```text
http://localhost:8000/api/integrations/google-calendar/callback
```

6. Copie o client ID e client secret para `backend/.env`. Nunca use esses valores no frontend.

### 2. Variáveis de ambiente

```env
FRONTEND_URL=http://localhost:5173
APP_TIMEZONE=America/Fortaleza
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google-calendar/callback
GOOGLE_CALENDAR_WEBHOOK_URL=
GOOGLE_CALENDAR_WEBHOOK_TOKEN=
GOOGLE_TOKEN_ENCRYPTION_KEY=
GOOGLE_CALENDAR_SYNC_ENABLED=false
GOOGLE_CALENDAR_SYNC_INTERVAL_MINUTES=5
```

`GOOGLE_CALENDAR_WEBHOOK_TOKEN` deve ser aleatório e diferente das demais chaves. O refresh token é criptografado com Fernet antes de ser persistido e nunca é retornado pela API.

### 3. Conectar e selecionar calendários

1. Entre como `ADMIN`.
2. Abra **Integrações** na sidebar.
3. Clique em **Conectar Google Calendar** e conclua o OAuth.
4. Escolha explicitamente um calendário.
5. Defina matéria/categoria e, opcionalmente, professor.
6. Clique em **Adicionar fonte** e depois em **Sincronizar agora**.

O TaskFlow não importa automaticamente todos os calendários. A lista da conta apenas permite selecionar fontes autorizadas.

### Sincronização

Na primeira sincronização, eventos dos últimos 30 dias em diante são importados e o `nextSyncToken` é persistido. Nas sincronizações seguintes, apenas mudanças são solicitadas. Se o Google invalidar o token com HTTP 410, somente as tarefas importadas daquele calendário são reconstruídas; tarefas manuais não são tocadas.

```powershell
cd backend
..\.venv\Scripts\python.exe -m app.cli sync-google-calendar
```

Eventos cancelados removem apenas a tarefa com origem `GOOGLE_CALENDAR` e identificadores externos correspondentes. Remover uma fonte não apaga tarefas já importadas.

### Localhost, polling e webhooks

Webhooks do Google Calendar exigem uma URL HTTPS pública com certificado válido. Eles não funcionam diretamente em `localhost`.

No desenvolvimento, use **Sincronizar agora**, o comando CLI ou habilite polling para uma implantação simples de instância única:

```env
GOOGLE_CALENDAR_SYNC_ENABLED=true
GOOGLE_CALENDAR_SYNC_INTERVAL_MINUTES=5
```

Em produção, configure:

```env
GOOGLE_CALENDAR_WEBHOOK_URL=https://seu-dominio.com/api/integrations/google-calendar/webhook
GOOGLE_CALENDAR_WEBHOOK_TOKEN=token-aleatorio-forte
```

Ao criar uma fonte habilitada, o TaskFlow solicita um canal `watch`. O webhook valida token, channel ID e resource ID, responde rapidamente e executa sincronização incremental em segundo plano. Canais Google expiram; para recriar um canal no MVP, remova e adicione novamente a fonte. O polling pode permanecer como recuperação.

Referências oficiais: [OAuth para aplicações web](https://developers.google.com/identity/protocols/oauth2/web-server), [sincronização incremental](https://developers.google.com/workspace/calendar/api/guides/sync) e [push notifications](https://developers.google.com/workspace/calendar/api/guides/push).

## Endpoints principais

### Autenticação

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/auth/register-member`
- `POST /api/auth/member-invites` — `ADMIN`
- `GET /api/auth/member-invites` — `ADMIN`

### Google Calendar

- `GET /api/integrations/google-calendar/status`
- `GET /api/integrations/google-calendar/connect`
- `GET /api/integrations/google-calendar/callback`
- `GET /api/integrations/google-calendar/calendars`
- `POST /api/integrations/google-calendar/sources`
- `PATCH /api/integrations/google-calendar/sources/{id}`
- `DELETE /api/integrations/google-calendar/sources/{id}`
- `POST /api/integrations/google-calendar/sync`
- `POST /api/integrations/google-calendar/disconnect`
- `POST /api/integrations/google-calendar/webhook`

Todos os endpoints de configuração exigem `ADMIN`. O callback exige a sessão administrativa e um estado OAuth assinado. O webhook usa autenticação própria por headers e token.

## Qualidade

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
..\.venv\Scripts\python.exe -m ruff check .

cd ..\frontend
npm test
npm run lint
npm run build
```

Os testes Google usam um gateway simulado e não acessam a internet nem uma conta real.

## Limitações operacionais

- O polling embutido é adequado apenas a uma implantação simples de instância única.
- Renovação automática de canais `watch` ainda não é agendada; recrie a fonte antes/depois da expiração ou use polling.
- A integração mantém uma única conta Google administrativa por instalação.
- SQLite é adequado ao MVP; produção concorrente deve usar PostgreSQL e um worker/scheduler dedicado.
