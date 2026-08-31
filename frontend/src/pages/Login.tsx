import {useState} from 'react';
import {ArrowLeft,ArrowRight,CalendarDays,Check,LockKeyhole} from 'lucide-react';
import {Brand} from '../components/Brand';
import {api} from '../services/api';
import type {User} from '../types';

export function Login({onLogin,onBack}:{onLogin:(u:User)=>void;onBack:()=>void}){
  const[email,setEmail]=useState('');
  const[password,setPassword]=useState('');
  const[error,setError]=useState('');
  const[busy,setBusy]=useState(false);
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
        <label htmlFor="email">E-mail</label><input id="email" type="email" required autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="voce@exemplo.com"/>
        <label htmlFor="password">Senha</label><input id="password" type="password" required minLength={8} autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Sua senha"/>
        {error&&<p className="form-error" role="alert">{error}</p>}
        <button className="button button-ink login-button" disabled={busy}>{busy?'Entrando…':<>Entrar <ArrowRight/></>}</button>
      </form>
    </section>
  </main>;
}
