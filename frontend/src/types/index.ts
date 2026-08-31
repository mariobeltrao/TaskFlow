export type Role='ADMIN'|'MEMBER'; export type Priority='LOW'|'MEDIUM'|'HIGH'|'URGENT'; export type Status='PENDING'|'COMPLETED';
export interface User{id:number;name:string;email:string;role:Role}
export type TaskSource='MANUAL'|'GOOGLE_CALENDAR';
export interface Task{id:number;title:string;description:string|null;category:string;responsible:string|null;due_date:string;priority:Priority;status:Status;created_by:number;created_at:string;updated_at:string;source:TaskSource;external_id:string|null;external_calendar_id:string|null;external_updated_at:string|null}
export interface TaskPage{items:Task[];total:number;page:number;page_size:number}
export interface Summary{total_tasks:number;pending_tasks:number;completed_tasks:number;upcoming_tasks:number;overdue_tasks:number;by_priority:Record<string,number>;by_category:Record<string,number>}
export type TaskInput=Pick<Task,'title'|'description'|'category'|'responsible'|'due_date'|'priority'|'status'>;
export interface MemberRegistration{name:string;email:string;invite_code:string;password:string;password_confirmation:string}
export interface GoogleCalendarSource{id:number;calendar_id:string;calendar_name:string;subject_name:string;professor_name:string|null;enabled:boolean;last_synced_at:string|null;last_error:string|null;channel_expires_at:string|null}
export interface GoogleCalendarStatus{connected:boolean;configured:boolean;account_email:string|null;last_error:string|null;sources:GoogleCalendarSource[]}
export interface GoogleCalendarItem{id:string;name:string;primary:boolean}
export interface GoogleSourceInput{calendar_id:string;subject_name:string;professor_name:string;enabled:boolean}
export interface GoogleSyncResult{created:number;updated:number;deleted:number;skipped:number}
