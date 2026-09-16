import {render,screen,waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {axe} from 'jest-axe';
import {beforeEach,describe,expect,it,vi} from 'vitest';
import {Login} from './Login';
import {admin} from '../test/factories';
const mocks=vi.hoisted(()=>({login:vi.fn()}));
vi.mock('../services/api',()=>({api:{login:mocks.login}}));
describe('Login',()=>{
  beforeEach(()=>mocks.login.mockReset().mockResolvedValue(admin));
  const submit=async()=>{await userEvent.type(screen.getByLabelText('E-mail'),'x@y.com');await userEvent.type(screen.getByLabelText('Senha'),'password123');await userEvent.click(screen.getByRole('button',{name:'Entrar'}))};
  it('renderiza formulário acessível e alterna tipo visual',async()=>{const{container}=render(<Login onLogin={vi.fn()} onBack={vi.fn()} onFirstAccess={vi.fn()}/>);expect(screen.getByRole('heading',{name:'Entre na sua conta'})).toBeInTheDocument();expect(screen.getByLabelText('E-mail')).toHaveAttribute('type','email');expect(screen.getByLabelText('Senha')).toHaveAttribute('type','password');await userEvent.click(screen.getByRole('button',{name:/Administrador/}));expect(screen.getByText(/papel salvo/)).toBeInTheDocument();expect(await axe(container)).toHaveNoViolations()});
  it('autentica e limpa senha após sucesso',async()=>{const onLogin=vi.fn();render(<Login onLogin={onLogin} onBack={vi.fn()} onFirstAccess={vi.fn()}/>);await submit();await waitFor(()=>expect(mocks.login).toHaveBeenCalledWith('x@y.com','password123'));expect(onLogin).toHaveBeenCalledWith(admin);expect(screen.getByLabelText('Senha')).toHaveValue('')});
});
