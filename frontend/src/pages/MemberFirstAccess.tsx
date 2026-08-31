import {useState} from 'react';
import {ArrowLeft,ArrowRight,CheckCircle2,KeyRound} from 'lucide-react';
import {Brand} from '../components/Brand';
import {Footer} from '../components/Footer';
import {api} from '../services/api';

export function MemberFirstAccess({onBack,onComplete}:{onBack:()=>void;onComplete:()=>void}){
  const[name,setName]=useState('');const[email,setEmail]=useState('');const[inviteCode,setInviteCode]=useState('');
  const[password,setPassword]=useState('');const[confirmation,setConfirmation]=useState('');const[busy,setBusy]=useState(false);const[error,setError]=useState('');const[done,setDone]=useState(false);
  const submit=async(event:React.FormEvent)=>{event.preventDefault();setError('');if(password!==confirmation){setError('As senhas não coincidem.');return}setBusy(true);try{await api.registerMember({name,email,invite_code:inviteCode,password,password_confirmation:confirmation});setDone(true)}catch(err){setError(err instanceof Error?err.message:'Não foi possível concluir o primeiro acesso')}finally{setBusy(false)}};
  return <main className="first-access-page page-enter">
    <button className="login-back" onClick={onBack}><ArrowLeft/> Voltar ao login</button>
    <section className="first-access-intro"><Brand/><div><span className="kicker">Acesso exclusivo da turma</span><h1>Seu lugar no<br/>fluxo começa <em>aqui.</em></h1><p>Use o código individual entregue pelo administrador. Cada convite funciona uma única vez.</p></div><div className="invite-seal"><KeyRound/><span>CONVITE<br/>INDIVIDUAL</span></div></section>
    <section className="first-access-form-wrap">
      {done?<div className="registration-success"><CheckCircle2/><span className="kicker">Tudo certo</span><h2>Conta criada!</h2><p>Seu acesso foi configurado como aluno. Agora você já pode entrar no mural.</p><button className="button button-ink" onClick={onComplete}>Ir para o login <ArrowRight/></button></div>:<form className="login-card first-access-card" onSubmit={submit}><span className="kicker">Primeiro acesso de aluno</span><h2>Crie sua senha</h2><p className="login-helper">O e-mail precisa ser o mesmo usado no convite.</p><div className="form-grid"><div><label htmlFor="member-name">Nome</label><input id="member-name" required minLength={2} maxLength={100} autoComplete="name" value={name} onChange={e=>setName(e.target.value)}/></div><div><label htmlFor="member-email">E-mail</label><input id="member-email" type="email" required autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)}/></div></div><label htmlFor="invite-code">Código de convite</label><input id="invite-code" required minLength={32} maxLength={128} autoComplete="one-time-code" value={inviteCode} onChange={e=>setInviteCode(e.target.value.trim())}/><div className="form-grid"><div><label htmlFor="member-password">Senha</label><input id="member-password" type="password" required minLength={8} maxLength={128} autoComplete="new-password" value={password} onChange={e=>setPassword(e.target.value)}/></div><div><label htmlFor="member-confirmation">Confirmar senha</label><input id="member-confirmation" type="password" required minLength={8} maxLength={128} autoComplete="new-password" value={confirmation} onChange={e=>setConfirmation(e.target.value)}/></div></div>{error&&<p className="form-error" role="alert">{error}</p>}<button className="button button-ink login-button" disabled={busy}>{busy?'Criando acesso…':<>Criar acesso de aluno <ArrowRight/></>}</button></form>}
      <Footer compact className="login-footer"/>
    </section>
  </main>;
}
