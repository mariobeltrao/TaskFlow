import {expect,test,type Page} from '@playwright/test';

const emailField=(page:Page)=>page.getByRole('textbox',{name:'E-mail',exact:true});
const login=async(page:Page,email='admin.e2e@example.com')=>{
  await page.goto('/login');
  await emailField(page).fill(email);
  await page.getByLabel('Senha',{exact:true}).fill('password123');
  await page.getByRole('button',{name:'Entrar',exact:true}).click();
  await expect(page.getByRole('navigation',{name:'Área autenticada'})).toBeVisible();
};

test('login ADMIN abre dashboard',async({page})=>{
  await page.goto('/');
  await page.getByRole('button',{name:'Entrar',exact:true}).click();
  await emailField(page).fill('admin.e2e@example.com');
  await page.getByLabel('Senha',{exact:true}).fill('password123');
  await page.getByRole('button',{name:'Entrar',exact:true}).click();
  await expect(page.getByText('Admin E2E')).toBeVisible();
  await expect(page.getByText(/Olá, Admin/)).toBeVisible();
  await expect(page.getByRole('button',{name:'Integrações'})).toHaveCount(0);
  const integrationResponse=await page.request.get('/api/integrations/google-calendar/status');
  expect(integrationResponse.status()).toBe(404);
});

test('CRUD completo ADMIN',async({page})=>{
  await login(page);
  await page.getByRole('button',{name:/Nova tarefa/}).click();
  await page.getByLabel('Título').fill('Criada E2E');
  await page.getByLabel('Categoria').fill('Playwright');
  await page.getByLabel('Prazo').fill('2026-09-20');
  await page.getByRole('button',{name:'Salvar tarefa'}).click();
  await expect(page.getByText('Criada E2E')).toBeVisible();
  const card=page.locator('.task-card').filter({hasText:'Criada E2E'});
  await card.getByRole('button',{name:'Editar tarefa'}).click();
  await page.getByLabel('Título').fill('Editada E2E');
  await page.getByRole('button',{name:'Salvar tarefa'}).click();
  await expect(page.getByText('Editada E2E')).toBeVisible();
  const editedCard=page.locator('.task-card').filter({hasText:'Editada E2E'});
  await editedCard.getByRole('button',{name:'Concluir tarefa'}).click();
  await expect(editedCard.getByRole('button',{name:'Reabrir tarefa'})).toBeVisible();
  await editedCard.getByRole('button',{name:'Reabrir tarefa'}).click();
  page.on('dialog',dialog=>dialog.accept());
  await editedCard.getByRole('button',{name:'Excluir tarefa'}).click();
  await expect(page.getByText('Editada E2E')).toHaveCount(0);
});

test('MEMBER é estritamente somente leitura',async({page})=>{
  await login(page,'member.e2e@example.com');
  await expect(page.getByText('Tarefa compartilhada').first()).toBeVisible();
  await expect(page.getByRole('button',{name:/Nova tarefa/})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Editar tarefa'})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Excluir tarefa'})).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Integrações'})).toHaveCount(0);
});

test('primeiro acesso cria e autentica MEMBER',async({page})=>{
  await page.goto('/first-access');
  await page.getByLabel('Nome').fill('Novo Aluno');
  await emailField(page).fill('new-member.e2e@example.com');
  await page.getByLabel('Código de convite').fill('taskflow-e2e-invite-code-0000000000000001');
  await page.getByLabel('Senha',{exact:true}).fill('password123');
  await page.getByLabel('Confirmar senha').fill('password123');
  await page.getByRole('button',{name:/Criar acesso/}).click();
  await page.getByRole('button',{name:/Ir para o login/}).click();
  await emailField(page).fill('new-member.e2e@example.com');
  await page.getByLabel('Senha',{exact:true}).fill('password123');
  await page.getByRole('button',{name:'Entrar',exact:true}).click();
  await expect(page.getByText('Aluno',{exact:true})).toBeVisible();
});

test('logout protege novamente a área privada',async({page})=>{
  await login(page);
  await page.getByRole('button',{name:'Sair'}).click();
  await expect(page.getByRole('heading',{name:'Entre na sua conta'})).toBeVisible();
  await page.goto('/app');
  await expect(page.getByRole('heading',{name:'Entre na sua conta'})).toBeVisible();
});

test('sessão persiste após reload e não grava JWT no storage',async({page})=>{
  await login(page);
  await page.reload();
  await expect(page.getByText('Admin E2E')).toBeVisible();
  expect(await page.evaluate(()=>({local:localStorage.length,session:sessionStorage.length}))).toEqual({local:0,session:0});
});

test('cookie inválido volta ao login',async({page,context})=>{
  await context.addCookies([{name:'taskflow_session',value:'invalid-token',domain:'127.0.0.1',path:'/'}]);
  await page.goto('/app');
  await expect(page.getByRole('heading',{name:'Entre na sua conta'})).toBeVisible();
});
