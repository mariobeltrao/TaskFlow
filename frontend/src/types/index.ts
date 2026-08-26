export type Role='ADMIN'|'MEMBER'; export type Priority='LOW'|'MEDIUM'|'HIGH'|'URGENT'; export type Status='PENDING'|'COMPLETED';
export interface User{id:number;name:string;email:string;role:Role}
export interface Task{id:number;title:string;description:string|null;category:string;responsible:string|null;due_date:string;priority:Priority;status:Status;created_by:number;created_at:string;updated_at:string}
export interface TaskPage{items:Task[];total:number;page:number;page_size:number}
export interface Summary{total_tasks:number;pending_tasks:number;completed_tasks:number;upcoming_tasks:number;overdue_tasks:number;by_priority:Record<string,number>;by_category:Record<string,number>}
export type TaskInput=Pick<Task,'title'|'description'|'category'|'responsible'|'due_date'|'priority'|'status'>;
