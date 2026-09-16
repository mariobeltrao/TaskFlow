import {useCallback,useEffect,useMemo,useState} from 'react';
import {ArrowUpRight,BarChart3,CalendarDays,CheckCircle2,ChevronLeft,ChevronRight,Clock3,LayoutDashboard,Link2,ListTodo,LogOut,Menu,Plus,Search,TrendingUp,X} from 'lucide-react';
import {Brand} from './components/Brand';
import {TaskCard} from './components/TaskCard';
import {TaskForm} from './components/TaskForm';
import {Landing} from './pages/Landing';
import {Login} from './pages/Login';
import {MemberFirstAccess} from './pages/MemberFirstAccess';
import {GoogleCalendarIntegration} from './pages/GoogleCalendarIntegration';
import {api} from './services/api';
import type {Summary,Task,TaskInput,User} from './types';
import {formatDate,localDate} from './utils/dates';

type View='overview'|'all'|'upcoming'|'completed'|'calendar'|'stats'|'integrations';
const nav:[View,string,React.ElementType][]=[['overview','Visão Geral',LayoutDashboard],['all','Todas as Tarefas',ListTodo],['upcoming','Próximas',Clock3],['completed','Concluídas',CheckCircle2],['calendar','Calendário',CalendarDays],['stats','Estatísticas',BarChart3]];
const googleIntegrationEnabled=import.meta.env.VITE_ENABLE_GOOGLE_INTEGRATION==='true';
const go=(path:string)=>{history.pushState({},'',path);window.dispatchEvent(new PopStateEvent('popstate'))};

export default function App(){
  const[user,setUser]=useState<User|null>(null);const[loading,setLoading]=useState(true);const[path,setPath]=useState(location.pathname);
  const[tasks,setTasks]=useState<Task[]>([]);const[summary,setSummary]=useState<Summary|null>(null);const[view,setView]=useState<View>(()=>new URLSearchParams(location.search).get('view')==='integrations'?'integrations':'overview');
  const[search,setSearch]=useState('');const[editing,setEditing]=useState<Task|null|undefined>(undefined);const[menu,setMenu]=useState(false);const[month,setMonth]=useState(()=>new Date());const[error,setError]=useState('');
  const load=useCallback(async()=>{if(!user)return;const suffix=view==='upcoming'?'?upcoming=true':view==='completed'?'?status=COMPLETED':'';try{const[t,s]=await Promise.all([api.tasks(suffix),api.summary()]);setTasks(t.items);setSummary(s);setError('')}catch(e){setError(e instanceof Error?e.message:'Erro ao carregar')}},[user,view]);
  useEffect(()=>{const update=()=>setPath(location.pathname);window.addEventListener('popstate',update);return()=>window.removeEventListener('popstate',update)},[]);
  useEffect(()=>{api.me().then(u=>{setUser(u);if(location.pathname==='/'||location.pathname==='/login')go('/app')}).catch(()=>setUser(null)).finally(()=>setLoading(false))},[]);
  useEffect(()=>{const expire=()=>{setUser(null);go('/login')};window.addEventListener('taskflow:unauthorized',expire);return()=>window.removeEventListener('taskflow:unauthorized',expire)},[]);
  // A troca de visualização sincroniza os dados remotos exibidos no mural.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(()=>{void load()},[load]);
  const shown=useMemo(()=>tasks.filter(t=>t.title.toLowerCase().includes(search.toLowerCase())),[tasks,search]);
  const isAdmin=user?.role==='ADMIN';
  const activeView:View=(!isAdmin||!googleIntegrationEnabled)&&view==='integrations'?'overview':view;
  const visibleNav:[View,string,React.ElementType][]=isAdmin&&googleIntegrationEnabled?[...nav,['integrations','Integrações',Link2]]:nav;
  const save=async(data:TaskInput)=>{if(editing)await api.update(editing.id,data);else await api.create(data);await load()};
  const remove=async(id:number)=>{if(confirm('Excluir esta tarefa?'))try{await api.remove(id);await load()}catch(caught){setError(caught instanceof Error?caught.message:'Erro ao excluir')}};
  const complete=async(t:Task)=>{try{await api.update(t.id,{status:t.status==='COMPLETED'?'PENDING':'COMPLETED'});await load()}catch(caught){setError(caught instanceof Error?caught.message:'Erro ao atualizar')}};
  if(loading)return <div className="splash"><Brand/><span>Preparando seu fluxo…</span></div>;
  if(!user){if(path==='/first-access')return <MemberFirstAccess onBack={()=>go('/login')} onComplete={()=>go('/login')}/>;if(path==='/login'||path.startsWith('/app'))return <Login onLogin={u=>{setUser(u);go('/app')}} onBack={()=>go('/')} onFirstAccess={()=>go('/first-access')}/>;return <Landing onLogin={()=>go('/login')}/>}

  const pending=shown.find(t=>t.status==='PENDING');
  const today=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'});
  return <div className="app-shell">
    <aside className={menu?'open':''}>
      <div className="sidebar-brand"><Brand compact/><button className="mobile-close icon-button" aria-label="Fechar menu" onClick={()=>setMenu(false)}><X/></button></div>
      <div className="sidebar-label">Seu espaço</div>
      <nav aria-label="Área autenticada">{visibleNav.map(([key,label,Icon])=><button key={key} className={activeView===key?'active':''} onClick={()=>{setView(key);setMenu(false)}}><Icon/>{label}{activeView===key&&<span/>}</button>)}</nav>
      <div className="sidebar-note"><span>FLUXO DA SEMANA</span><strong>{summary?.completed_tasks??0} concluídas</strong><div><i style={{width:`${summary?.total_tasks?summary.completed_tasks/summary.total_tasks*100:0}%`}}/></div></div>
      <div className="profile"><div className="avatar">{user.name.slice(0,2).toUpperCase()}</div><div><b>{user.name}</b><small>{isAdmin?'Administrador':'Aluno'}</small></div><button className="icon-button" aria-label="Sair" title="Sair" onClick={async()=>{try{await api.logout()}finally{setUser(null);go('/login')}}}><LogOut/></button></div>
    </aside>
    {menu&&<button className="menu-scrim" aria-label="Fechar menu" onClick={()=>setMenu(false)}/>} 
    <main className="content">
      <header className="app-header"><button className="menu-button icon-button" aria-label="Abrir menu" onClick={()=>setMenu(true)}><Menu/></button><div><span className="eyebrow">{today}</span><h1>{activeView==='overview'?<>Olá, {user.name.split(' ')[0]}.</>:visibleNav.find(n=>n[0]===activeView)?.[1]??'Visão Geral'}</h1></div>{isAdmin&&activeView!=='integrations'&&<button className="button button-ink" onClick={()=>setEditing(null)}><Plus/> Nova tarefa</button>}</header>
      {error&&<div className="error-banner" role="alert">{error}<button aria-label="Fechar aviso" onClick={()=>setError('')}>×</button></div>}
      {activeView==='overview'&&<Overview summary={summary} pending={pending}/>}
      {activeView==='integrations'&&isAdmin?<GoogleCalendarIntegration/>:activeView==='calendar'?<Calendar tasks={shown} month={month} setMonth={setMonth}/>:activeView==='stats'?<Statistics summary={summary}/>:<section className="tasks-section">
        <div className="section-head"><div><span className="eyebrow">{activeView==='overview'?'Organize sua semana':'Seu mural'}</span><h2>{activeView==='overview'?'Próximas entregas':visibleNav.find(n=>n[0]===activeView)?.[1]}</h2></div><label className="search"><Search/><input aria-label="Buscar tarefa" placeholder="Buscar uma tarefa…" value={search} onChange={e=>setSearch(e.target.value)}/></label></div>
        <div className="task-list">{shown.length?shown.slice(0,activeView==='overview'?6:100).map(t=><TaskCard key={t.id} task={t} isAdmin={isAdmin} onEdit={setEditing} onDelete={remove} onComplete={complete}/>):<div className="empty"><CheckCircle2/><h3>Tudo limpo por aqui.</h3><p>Nenhuma tarefa corresponde a esta visualização.</p></div>}</div>
      </section>}
    </main>
    {editing!==undefined&&<TaskForm task={editing} onClose={()=>setEditing(undefined)} onSave={save}/>} 
  </div>;
}

function Overview({summary,pending}:{summary:Summary|null;pending:Task|undefined}){
  const total=summary?.total_tasks??0;const completed=summary?.completed_tasks??0;const percentage=total?Math.round(completed/total*100):0;
  return <>
    <section className="dashboard-lead"><div><span className="kicker">O que merece sua atenção</span><h2>{summary?.pending_tasks??0} tarefas<br/><em>em movimento.</em></h2><p>Você tem {summary?.upcoming_tasks??0} prazo(s) chegando nos próximos sete dias.</p></div><div className="progress-orbit"><span>{percentage}%</span><small>do mural<br/>concluído</small><svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="52"/><circle cx="60" cy="60" r="52" pathLength="100" style={{strokeDasharray:`${percentage} 100`}}/></svg></div></section>
    <section className="dashboard-grid">
      {pending?<article className="spotlight"><span className="spotlight-label">PRÓXIMO PRAZO <ArrowUpRight/></span><div><span className="spotlight-date"><b>{localDate(pending.due_date).getDate()}</b>{localDate(pending.due_date).toLocaleDateString('pt-BR',{month:'short'})}</span><div><h3>{pending.title}</h3><p>{pending.category} · {pending.responsible||'Sem responsável'}</p></div></div><span className={`priority ${pending.priority.toLowerCase()}`}>{pending.priority==='URGENT'?'Urgente':pending.priority==='HIGH'?'Alta prioridade':'Em andamento'}</span></article>:<article className="spotlight empty-spotlight"><CheckCircle2/><h3>Sem prazos pendentes</h3></article>}
      <article className="metric-card metric-coral"><span>PENDENTES</span><strong>{summary?.pending_tasks??0}</strong><small>No mural agora</small></article>
      <article className="metric-card metric-sun"><span>ATRASADAS</span><strong>{summary?.overdue_tasks??0}</strong><small>Pedem atenção</small></article>
      <article className="metric-card metric-mint"><TrendingUp/><span>CONCLUÍDAS</span><strong>{completed}</strong><small>Progresso acumulado</small></article>
    </section>
  </>;
}

function Statistics({summary}:{summary:Summary|null}){return <section className="stats-panel"><div className="section-head"><div><span className="eyebrow">Uma visão do todo</span><h2>Distribuição das tarefas</h2></div><BarChart3/></div><h3>Por prioridade</h3>{Object.entries(summary?.by_priority??{}).map(([key,value])=><Bar key={key} label={key} value={value} total={summary?.total_tasks}/>) }<h3>Por categoria</h3>{Object.entries(summary?.by_category??{}).map(([key,value])=><Bar key={key} label={key} value={value} total={summary?.total_tasks}/>)}</section>}
function Bar({label,value,total=1}:{label:string;value:number;total?:number}){return <div className="bar-row"><span>{label}</span><div><i style={{width:`${Math.max(5,value/(total||1)*100)}%`}}/></div><b>{value}</b></div>}

function Calendar({tasks,month,setMonth}:{tasks:Task[];month:Date;setMonth:(d:Date)=>void}){
  const first=new Date(month.getFullYear(),month.getMonth(),1);const count=new Date(month.getFullYear(),month.getMonth()+1,0).getDate();const days=Array.from({length:first.getDay()+count},(_,i)=>i<first.getDay()?null:i-first.getDay()+1);const now=new Date();
  return <section className="calendar-panel"><div className="calendar-head"><button className="icon-button" aria-label="Mês anterior" onClick={()=>setMonth(new Date(month.getFullYear(),month.getMonth()-1))}><ChevronLeft/></button><div><span className="eyebrow">Planeje com calma</span><h2>{month.toLocaleDateString('pt-BR',{month:'long',year:'numeric'})}</h2></div><button className="icon-button" aria-label="Próximo mês" onClick={()=>setMonth(new Date(month.getFullYear(),month.getMonth()+1))}><ChevronRight/></button></div><div className="calendar-grid">{'DSTQQSS'.split('').map((d,i)=><b key={i}>{d}</b>)}{days.map((day,i)=>{const dayTasks=day?tasks.filter(t=>{const d=localDate(t.due_date);return d.getFullYear()===month.getFullYear()&&d.getMonth()===month.getMonth()&&d.getDate()===day}):[];const isToday=day===now.getDate()&&month.getMonth()===now.getMonth()&&month.getFullYear()===now.getFullYear();return <div key={i} className={`${!day?'blank':''} ${isToday?'today':''} ${dayTasks.length?'has-tasks':''}`}><span>{day}</span>{dayTasks.map(t=><small key={t.id} title={`${t.title} — ${formatDate(t.due_date)}`}>{t.title}</small>)}</div>})}</div></section>;
}
