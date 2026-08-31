import {useEffect,useRef} from 'react';
import {ArrowDown,ArrowRight,CalendarDays,Check,Clock3,Flag,Plus,Sparkles} from 'lucide-react';
import {Brand} from '../components/Brand';

const steps=[
  ['01','Adicione','Registre atividades, provas, trabalhos e compromissos.',Plus],
  ['02','Priorize','Veja de relance o que pede atenção agora — e o que pode esperar.',Flag],
  ['03','Acompanhe','Encontre seus próximos prazos sem caçar informação por todo lado.',CalendarDays],
  ['04','Conclua','Marque o que avançou e enxergue o ritmo que você criou.',Check],
] as const;

export function Landing({onLogin}:{onLogin:()=>void}){
  const hero=useRef<HTMLElement>(null);
  useEffect(()=>{
    const node=hero.current;
    if(!node||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const move=(event:PointerEvent)=>{
      const x=(event.clientX/window.innerWidth-.5)*2;
      const y=(event.clientY/window.innerHeight-.5)*2;
      node.style.setProperty('--pointer-x',`${x}`);
      node.style.setProperty('--pointer-y',`${y}`);
    };
    window.addEventListener('pointermove',move,{passive:true});
    return()=>window.removeEventListener('pointermove',move);
  },[]);
  return <div className="public-site">
    <header className="public-nav">
      <a href="#inicio" aria-label="TaskFlow, início"><Brand compact/></a>
      <nav aria-label="Navegação principal">
        <a href="#como-funciona">Como funciona</a><a href="#recursos">Recursos</a>
      </nav>
      <button className="button button-ink button-small" onClick={onLogin}>Entrar <ArrowRight/></button>
    </header>

    <main>
      <section className="hero" id="inicio" ref={hero}>
        <div className="hero-copy reveal">
          <span className="kicker"><Sparkles/> Organização com vida própria</span>
          <h1>Faça suas<br/><em>tarefas</em> fluírem.</h1>
          <p>Um lugar claro e gostoso de usar para reunir prazos, decidir prioridades e seguir em frente.</p>
          <div className="hero-actions">
            <button className="button button-ink" onClick={onLogin}>Entrar no TaskFlow <ArrowRight/></button>
            <a className="text-link" href="#como-funciona">Descobrir como funciona <ArrowDown/></a>
          </div>
        </div>
        <div className="hero-stage" aria-label="Uma semana organizada no TaskFlow">
          <div className="orbit orbit-one"><CalendarDays/><span>28</span><small>AGO</small></div>
          <div className="orbit orbit-two"><Clock3/><span>09:30</span></div>
          <div className="hero-task task-main"><span className="check-box"><Check/></span><div><small>PRÓXIMA ENTREGA</small><strong>Apresentação de história</strong><span>amanhã · 10:00</span></div><b>!</b></div>
          <div className="hero-task task-note"><Flag/><div><small>PRIORIDADE</small><strong>Revisar capítulo 04</strong></div></div>
          <div className="scribble" aria-hidden="true">→</div>
          <span className="sticker">tudo no<br/><b>ritmo.</b></span>
        </div>
        <div className="hero-marquee" aria-hidden="true"><span>CLAREZA • MOVIMENTO • FOCO • CLAREZA • MOVIMENTO • FOCO •</span></div>
      </section>

      <section className="how" id="como-funciona">
        <div className="section-intro"><span className="kicker">Do caos ao concluído</span><h2>Quatro passos.<br/>Um fluxo mais leve.</h2><p>TaskFlow transforma o que está solto em uma sequência simples de decisões.</p></div>
        <div className="steps">{steps.map(([number,title,description,Icon])=><article className="step" key={number}><div className="step-top"><span>{number}</span><Icon/></div><h3>{title}</h3><p>{description}</p></article>)}</div>
      </section>

      <section className="product-story" id="recursos">
        <div className="product-copy"><span className="kicker">Seu próximo passo, visível</span><h2>Saiba o que merece sua atenção.</h2><p>Prazos, prioridade e progresso trabalham juntos — sem transformar seu dia em uma planilha.</p><button className="button button-coral" onClick={onLogin}>Começar agora <ArrowRight/></button></div>
        <div className="demo-board">
          <div className="demo-heading"><span>SEMANA 35</span><strong>3 tarefas pedem atenção</strong><div className="demo-progress"><i/></div></div>
          <article className="demo-feature"><span className="demo-date"><b>29</b> AGO</span><div><small>MAIS URGENTE</small><h3>Entrega do projeto final</h3><p>Design · Equipe Aurora</p></div><span className="tag tag-urgent">Urgente</span></article>
          <div className="demo-row"><article><Check/><span><b>Bibliografia revisada</b><small>Concluída hoje</small></span></article><article><Clock3/><span><b>Questionário online</b><small>Faltam 3 dias</small></span></article></div>
        </div>
      </section>

      <section className="benefits">
        <article className="benefit-big"><span>01</span><h2>Tudo em<br/>um só lugar.</h2><p>Menos abas abertas. Mais presença no que você está fazendo.</p></article>
        <article className="benefit-round"><Flag/><strong>Prioridades<br/>claras</strong></article>
        <article className="benefit-note"><span>HOJE</span><strong>Prazos que<br/>não somem.</strong><div className="note-line"/><div className="note-line short"/></article>
        <article className="benefit-progress"><span>75%</span><strong>Progresso que dá para enxergar.</strong><div><i/></div></article>
      </section>

      <section className="final-cta"><Brand/><div><span className="kicker">Seu mural está pronto</span><h2>O que importa<br/>já pode fluir.</h2></div><button className="button button-sun" onClick={onLogin}>Entrar no TaskFlow <ArrowRight/></button></section>
    </main>
    <footer><Brand compact/><p>Organização, movimento e clareza.</p><span>TaskFlow · 2026</span></footer>
  </div>;
}
