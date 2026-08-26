export const localDate=(iso:string)=>new Date(`${iso}T00:00:00`);
export const deadlineLabel=(iso:string,completed=false)=>{if(completed)return'Concluída';const today=new Date();today.setHours(0,0,0,0);const days=Math.round((localDate(iso).getTime()-today.getTime())/86400000);if(days===0)return'Hoje';if(days===1)return'Amanhã';if(days>1)return`Faltam ${days} dias`;if(days===-1)return'Atrasada há 1 dia';return`Atrasada há ${Math.abs(days)} dias`};
export const formatDate=(iso:string)=>localDate(iso).toLocaleDateString('pt-BR',{day:'2-digit',month:'short'});
