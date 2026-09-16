import {render,screen,waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {axe} from 'jest-axe';
import {beforeEach,describe,expect,it,vi} from 'vitest';
import {MemberFirstAccess} from './MemberFirstAccess';
import {member} from '../test/factories';
const mocks=vi.hoisted(()=>({registerMember:vi.fn()}));
vi.mock('../services/api',()=>({api:{registerMember:mocks.registerMember}}));
const fill=async(password='password123',confirmation=password)=>{await userEvent.type(screen.getByLabelText('Nome'),'Ana Lima');await userEvent.type(screen.getByLabelText('E-mail'),'ana@test.com');await userEvent.type(screen.getByLabelText('Código de convite'),'x'.repeat(32));await userEvent.type(screen.getByLabelText('Senha'),password);await userEvent.type(screen.getByLabelText('Confirmar senha'),confirmation)};
describe('MemberFirstAccess',()=>{
  beforeEach(()=>mocks.registerMember.mockReset().mockResolvedValue(member));
  it('renderiza acessível, valida limites e volta',async()=>{const back=vi.fn();const{container}=render(<MemberFirstAccess onBack={back} onComplete={vi.fn()}/>);expect(screen.getByRole('heading',{name:'Crie sua senha'})).toBeInTheDocument();expect(screen.getByLabelText('Nome')).toHaveAttribute('maxlength','100');expect(screen.getByLabelText('Código de convite')).toHaveAttribute('minlength','32');expect(await axe(container)).toHaveNoViolations();await userEvent.click(screen.getByRole('button',{name:'Voltar ao login'}));expect(back).toHaveBeenCalled()});
  it('não envia senhas diferentes',async()=>{render(<MemberFirstAccess onBack={vi.fn()} onComplete={vi.fn()}/>);await fill('password123','password456');await userEvent.click(screen.getByRole('button',{name:'Criar acesso de aluno'}));expect(await screen.findByRole('alert')).toHaveTextContent('As senhas não coincidem');expect(mocks.registerMember).not.toHaveBeenCalled()});
  it('registra sem role e conclui',async()=>{const complete=vi.fn();render(<MemberFirstAccess onBack={vi.fn()} onComplete={complete}/>);await fill();await userEvent.click(screen.getByRole('button',{name:'Criar acesso de aluno'}));await waitFor(()=>expect(mocks.registerMember).toHaveBeenCalledOnce());expect(mocks.registerMember.mock.calls[0][0]).toEqual({name:'Ana Lima',email:'ana@test.com',invite_code:'x'.repeat(32),password:'password123',password_confirmation:'password123'});expect(mocks.registerMember.mock.calls[0][0]).not.toHaveProperty('role');await userEvent.click(await screen.findByRole('button',{name:/Ir para o login/}));expect(complete).toHaveBeenCalled()});
});
