import type {Summary,Task,User} from '../types';
export const admin:User={id:1,name:'Admin Teste',email:'admin@test.com',role:'ADMIN'};
export const member:User={id:2,name:'Aluno Teste',email:'member@test.com',role:'MEMBER'};
export const task=(overrides:Partial<Task>={}):Task=>({id:1,title:'Cálculo',description:'Lista 1',category:'Matemática',responsible:'Ada',due_date:'2026-09-20',priority:'MEDIUM',status:'PENDING',created_by:1,created_at:'2026-09-01T10:00:00Z',updated_at:'2026-09-01T10:00:00Z',source:'MANUAL',external_id:null,external_calendar_id:null,external_updated_at:null,...overrides});
export const summary=(overrides:Partial<Summary>={}):Summary=>({total_tasks:3,pending_tasks:2,completed_tasks:1,upcoming_tasks:1,overdue_tasks:1,by_priority:{MEDIUM:2,HIGH:1},by_category:{Matemática:2,Programação:1},...overrides});
