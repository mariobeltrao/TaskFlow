import {CalendarDays,Check,Cloud,Edit3,Trash2} from 'lucide-react';
import type {Task} from '../types';
import {deadlineLabel,formatDate} from '../utils/dates';

const labels={LOW:'Baixa',MEDIUM:'Média',HIGH:'Alta',URGENT:'Urgente'};

export function TaskCard({task,isAdmin,onEdit,onDelete,onComplete}:{task:Task;isAdmin:boolean;onEdit:(t:Task)=>void;onDelete:(id:number)=>void;onComplete:(t:Task)=>void}){
  const completed=task.status==='COMPLETED';
  return <article className={`task-card ${completed?'completed':''}`}>
    <div className={`priority-line ${task.priority.toLowerCase()}`}/>
    <div className="task-body"><div className="task-top"><span className="category">{task.category}</span><span className={`priority ${task.priority.toLowerCase()}`}>{labels[task.priority]}</span>{task.source==='GOOGLE_CALENDAR'&&<span className="external-source"><Cloud/> Google Calendar</span>}</div><h3>{task.title}</h3>{task.responsible&&<p className="muted">{task.responsible}</p>}<div className="task-meta"><span><CalendarDays size={15}/>{formatDate(task.due_date)}</span><strong className={deadlineLabel(task.due_date,completed).startsWith('Atrasada')?'danger':''}>{deadlineLabel(task.due_date,completed)}</strong></div></div>
    {isAdmin&&<div className="task-actions"><button aria-label={completed?'Reabrir tarefa':'Concluir tarefa'} title={completed?'Reabrir tarefa':'Concluir tarefa'} onClick={()=>onComplete(task)}><Check size={17}/></button><button aria-label="Editar tarefa" title="Editar tarefa" onClick={()=>onEdit(task)}><Edit3 size={17}/></button><button aria-label="Excluir tarefa" title="Excluir tarefa" onClick={()=>onDelete(task.id)}><Trash2 size={17}/></button></div>}
  </article>;
}
