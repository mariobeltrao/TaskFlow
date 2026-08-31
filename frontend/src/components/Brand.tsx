import {Check} from 'lucide-react';

export function Brand({compact=false}:{compact?:boolean}){
  return <span className={`brand-lockup ${compact?'compact':''}`}>
    <span className="brand-mark" aria-hidden="true"><Check strokeWidth={3}/></span>
    <span>Task<span>Flow</span></span>
  </span>;
}
