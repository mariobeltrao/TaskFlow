import {useState} from 'react';
import {ArrowLeft,ArrowRight,CalendarDays,Check,GraduationCap,LockKeyhole,ShieldCheck} from 'lucide-react';
import {Brand} from '../components/Brand';
import {Footer} from '../components/Footer';
import {api} from '../services/api';
import type {User} from '../types';

export function Login({onLogin,onBack,onFirstAccess}:{onLogin:(u:User)=>void;onBack:()=>void;onFirstAccess:()=>void}){
  const[email,setEmail]=useState('');
  const[password,setPassword]=useState('');
  const[error,setError]=useState('');
  const[busy,setBusy]=useState(false);
  const[accessType,setAccessType]=useState<'student'|'admin'>('student');
  const submit=async(e:React.FormEvent)=>{
    e.preventDefault();setError('');setBusy(true);
    try{onLogin(await api.login(email,password))}catch(err){setError(err instanceof Error?err.message:'Falha no login')}finally{setBusy(false)}
  };
  return <main className="login-page page-enter">
    <button className="login-back" onClick={onBack}><ArrowLeft/> Voltar ao início</button>
    <section className="login-visual">
      <Brand/>
      <div><span className="kicker">Bem-vindo de volta</span><h1>Seu fluxo<br/>continua <em>aqui.</em></h1><p>Entre para ver o que merece sua atenção hoje.</p></div>
      <div className="login-paper"><CalendarDays/><span><small>HOJE · 09:30</small><b>Revisar apresentação</b></span><i><Check/></i></div>
      <span className="login-sticker">um passo<br/>de cada vez</span>
    </section>
    <section className="login-form-wrap">
      <form className="login-card" onSubmit={submit}>
        <span className="login-icon"><LockKeyhole/></span><span className="kicker">Acesso ao mural</span><h2>Entre na sua conta</h2><p className="login-helper">Use suas credenciais para continuar.</p>
        <div className="access-type" aria-label="Tipo de acesso"><button type="button" className={accessType==='student'?'active':''} onClick={()=>setAccessType('student')}><GraduationCap/> Entrar como aluno</button><button type="button" className={accessType==='admin'?'active':''} onClick={()=>setAccessType('admin')}><ShieldCheck/> Administrador</button></div>
        <p className="access-note">{accessType==='student'?'Acesso de consulta ao mural da turma.':'Acesso administrativo conforme o papel salvo na sua conta.'}</p>
        <label htmlFor="email">E-mail</label><input id="email" type="email" required autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="voce@exemplo.com"/>
        <label htmlFor="password">Senha</label><input id="password" type="password" required minLength={8} autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Sua senha"/>
        {error&&<p className="form-error" role="alert">{error}</p>}
        <button className="button button-ink login-button" disabled={busy}>{busy?'Entrando…':<>Entrar <ArrowRight/></>}</button>
        <button type="button" className="first-access-link" onClick={onFirstAccess}>Primeiro acesso de aluno <ArrowRight/></button>
      </form>
      <Footer compact className="login-footer"/>
    </section>
  </main>;
}
