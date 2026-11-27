"""Gera slide-01.html ... slide-07.html — Prova Integrada 2026.2 (CSS compartilhado em styles.css)."""
from pathlib import Path

OUT = Path(__file__).parent
TOTAL = 7

PONTE = '<svg viewBox="0 0 100 100" class="{cls}"><path d="M50 0a50 50 0 1 0 0.01 0Z"/></svg>'

I = {  # ícones de linha (viewBox 24)
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "relogio": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "doc": '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2.5"/><path d="M13 10h5M13 14h5"/>',
    "caneta": '<path d="M16 3l5 5L9 20l-6 1 1-6z"/><path d="M14 5l5 5"/>',
    "lanche": '<path d="M8 3h3v3l1.5 2v13h-6V8L8 6z"/><path d="M14 15a4 3 0 0 1 8 0z"/><path d="M14 15h8v3h-8z"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "celular": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M3 3l18 18"/>',
    "lupa": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    "porta": '<path d="M4 21V4a1 1 0 0 1 1-1h9v18"/><path d="M14 8h3a1 1 0 0 1 1 1v12"/><path d="M2 21h20M11 12v1"/>',
    "folha": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/>',
    "salvar": '<path d="M6 3h12v18l-6-4-6 4z"/>',
}
SETA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'


def icone(nome):
    return f'<div class="icone"><svg viewBox="0 0 24 24">{I[nome]}</svg></div>'


def logo():
    return '<div class="logo-card"><img src="assets/logo-unipe-negativa.png" alt="UNIPÊ - Centro Universitário de João Pessoa"></div>'


def pagina(n, bg, conteudo, extra_css="", swipe=True):
    ponte_esq = PONTE.format(cls="ponte esq") if n > 1 else ""
    ponte_dir = PONTE.format(cls="ponte dir") if n < TOTAL else ""
    arraste = f'<div class="arraste">arraste {SETA}</div>' if swipe else ""
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Prova Integrada 2026.2 — slide {n:02d}</title>
<link rel="stylesheet" href="styles.css">
<style>{extra_css}</style>
</head><body>
<main class="slide {bg}">
  {ponte_esq}{ponte_dir}
  <header class="topo"><span class="marca"><b>Medicina</b> · UNIPÊ</span><span class="contador">{n}/{TOTAL}</span></header>
  <section class="conteudo">{conteudo}</section>
  <footer class="rodape"><span class="tracejado"></span>{arraste}</footer>
</main>
</body></html>
"""
    (OUT / f"slide-{n:02d}.html").write_text(html, encoding="utf-8")


# 1 — CAPA
pagina(1, "bg-azul", f"""
  <span class="tag">NAPED | Coordenação de Medicina</span>
  <h1 class="capa-h1">Prova <span class="destaque">Integrada</span> 2026.2<span class="cursor">_</span></h1>
  <p class="capa-sub">Orientações aos alunos</p>
  <div class="capa-base">
    <div class="capa-esq">
      <div class="data">{icone("cal")}<span><b>28/11</b>sábado</span></div>
      {logo()}
    </div>
  </div>
  <img class="ilustra" src="assets/prova.svg" alt="">
""", extra_css="""
  .tag{font-size:22px;}
  .capa-h1{font-size:128px;max-width:900px;}
  .capa-sub{font:700 44px/1.2 var(--f-corpo);margin-top:28px;color:var(--cinza);}
  .capa-base{margin-top:40px;height:500px;}
  .capa-esq{width:430px;display:flex;flex-direction:column;justify-content:flex-end;height:100%;gap:48px;}
  .data{display:flex;align-items:center;gap:24px;}
  .data span{font:600 32px/1.1 var(--f-corpo);color:var(--cinza);}
  .data b{display:block;font:800 76px/1 var(--f-titulo);font-variation-settings:"opsz" 96;color:var(--amarelo);}
  .data .icone{flex-basis:100px;height:100px;}
  .ilustra{position:absolute;right:-70px;bottom:-30px;width:600px;height:600px;z-index:-1;}
  .slide .ponte.dir{top:420px;}
""")

# 2 — HORÁRIOS
horas = [("07h30", "Entrada dos alunos"), ("08h", "Início da prova"),
         ("08h10", "Limite de entrada"), ("12h", "Término da prova")]
pagina(2, "bg-azul", f"""
  <span class="tag">Horários</span>
  <h2>Fique de olho no <span class="destaque">relógio</span><span class="cursor">_</span></h2>
  <ul class="horas">{"".join(f'<li><span class="hora">{h}</span><span>{t}</span></li>' for h, t in horas)}</ul>
  <div class="notas">
    <div class="nota"><b>Permanência mínima:</b> 2 horas</div>
    <div class="nota"><b>PROAPE</b> (condições especiais): <b>08h às 13h</b></div>
  </div>
""", extra_css="""
  h2{font-size:88px;}
  .horas{list-style:none;display:flex;flex-direction:column;gap:22px;}
  .horas li{display:flex;align-items:center;gap:32px;font:600 40px/1.2 var(--f-corpo);}
  .hora{flex:0 0 220px;text-align:center;background:var(--amarelo);color:var(--azul);border-radius:999px;padding:14px 0;
    font:800 50px/1 var(--f-titulo);font-variation-settings:"opsz" 96;}
  .notas{display:flex;flex-direction:column;gap:18px;margin-top:44px;}
  .nota{background:rgba(255,255,255,.08);border-left:8px solid var(--amarelo);border-radius:0 20px 20px 0;padding:24px 30px;font:500 34px/1.3 var(--f-corpo);}
  .nota b{font-weight:800;color:var(--amarelo);}
""")

# 3 — LOCAL E SALAS
salas = [("P2A", "T450"), ("P2B", "S433"), ("P2C", "S422"), ("P4A", "T443"), ("P4B", "T446"), ("P4C", "T447"),
         ("P5A", "S437"), ("P5C", "S423"), ("P6A", "T444"), ("P6B", "T445"), ("P6C", "T448"), ("P6D", "T449"),
         ("P8A e P8B", "S420"), ("P8C", "S434"), ("P8D", "S425"), ("Sala especial", "S440")]
pagina(3, "bg-azul", f"""
  <span class="tag">Local da prova</span>
  <h2>Blocos <span class="destaque">S e T</span> do UNIPÊ<span class="cursor">_</span></h2>
  <p class="corpo sub">Confira a sala da sua turma:</p>
  <div class="grade">{"".join(f'<div class="sala"><span>{p}</span><b>{s}</b></div>' for p, s in salas)}</div>
""", extra_css="""
  .tag{margin-bottom:30px;}
  h2{font-size:80px;margin-bottom:20px;}
  .sub{font-size:34px;margin-bottom:28px;color:var(--cinza)!important;}
  .grade{display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(8,auto);gap:12px 20px;}
  .sala{display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.08);border-radius:14px;padding:13px 24px;}
  .sala span{font:700 31px/1.2 var(--f-corpo);}
  .sala b{font:800 38px/1 var(--f-titulo);font-variation-settings:"opsz" 96;color:var(--amarelo);}
""")

# 4 — O QUE LEVAR
pagina(4, "bg-azul", f"""
  <span class="tag">O que levar</span>
  <h2>Separe na <span class="destaque">véspera</span><span class="cursor">_</span></h2>
  <ul class="lista">
    <li class="item">{icone("doc")}<div class="item-txt"><span class="obrig">Obrigatório</span>Documento oficial de identificação original com foto<small>Sem ele, não poderá realizar a prova.</small></div></li>
    <li class="item">{icone("caneta")}<div class="item-txt">Caneta esferográfica azul ou preta<small>De corpo transparente</small></div></li>
    <li class="item">{icone("lanche")}<div class="item-txt">Garrafa de água transparente e lanche<small>Permitidos</small></div></li>
  </ul>
""", extra_css="""
  .item{align-items:flex-start;padding:30px 32px;}
  .item-txt{font-size:38px;}
  .item-txt small{font-size:30px;}
  .obrig{display:table;background:var(--amarelo);color:var(--azul);font:800 20px/1 var(--f-corpo);letter-spacing:.14em;text-transform:uppercase;padding:10px 14px;border-radius:6px;margin-bottom:14px;}
""")

# 5 — FOLHA DE RESPOSTAS
checks = ["Nome completo e legível, de preferência em <b>LETRA MAIÚSCULA</b>",
          "<b>RGM ou CPF</b>",
          "Turma e semestre <b>2026.2</b> no cabeçalho",
          "<b>Assinatura</b> no campo indicado"]
pagina(5, "bg-claro", f"""
  <span class="tag">Atenção</span>
  <h2>Folha de respostas<span class="cursor">_</span></h2>
  <p class="corpo intro">Preencha todos os campos corretamente:</p>
  <ul class="checks">{"".join(f'<li>{icone("check")}<span>{c}</span></li>' for c in checks)}</ul>
  <div class="faixa">Marque as respostas com caneta azul ou preta, <b>SEM RASURAS.</b></div>
""", extra_css="""
  h2{font-size:92px;margin-bottom:28px;}
  .intro{font-weight:700;font-size:36px;margin-bottom:28px;}
  .checks{list-style:none;display:flex;flex-direction:column;gap:20px;}
  .checks li{display:flex;align-items:center;gap:26px;font:500 36px/1.25 var(--f-corpo);}
  .checks b{font-weight:800;}
  .checks .icone{flex-basis:64px;height:64px;background:var(--azul);}
  .checks .icone svg{stroke:var(--amarelo);width:38px;height:38px;stroke-width:3.2;}
  .faixa{margin-top:44px;background:var(--azul);color:var(--branco);border-radius:20px;padding:30px 34px;font:600 36px/1.3 var(--f-corpo);}
  .faixa b{color:var(--amarelo);font-weight:800;}
""")

# 6 — LEMBRETES
pagina(6, "bg-azul", f"""
  <span class="tag">Lembretes</span>
  <h2>Antes e durante a <span class="destaque">prova</span><span class="cursor">_</span></h2>
  <ul class="lista">
    <li class="item">{icone("celular")}<div class="item-txt">Desligue o celular e retire dispositivos eletrônicos<small>Inclusive relógios e óculos inteligentes</small></div></li>
    <li class="item">{icone("lupa")}<div class="item-txt">Confira os materiais recebidos antes de iniciar a prova</div></li>
    <li class="item">{icone("porta")}<div class="item-txt">Não saia da sala com o caderno de prova</div></li>
    <li class="item">{icone("folha")}<div class="item-txt">Rascunho do gabarito: só ao término da prova<small>Entregue antes da devolução da folha de respostas preenchida aos fiscais de sala</small></div></li>
  </ul>
""", extra_css="""
  h2{font-size:84px;margin-bottom:36px;}
  .lista{gap:20px;}
  .item{padding:22px 28px;gap:26px;}
  .item-txt{font-size:32px;line-height:1.2;}
  .item-txt small{font-size:26px;}
  .icone{flex-basis:80px;height:80px;}
  .icone svg{width:44px;height:44px;}
""")

# 7 — ENCERRAMENTO / CTA
pagina(7, "bg-azul", f"""
  <span class="tag">28/11 · sábado</span>
  <h1 class="cta-h1">Boa <span class="destaque">prova!</span><span class="cursor">_</span></h1>
  <p class="corpo resumo">Entrada às <strong>07h30</strong> nos <strong>Blocos S e T</strong>. Não esqueça o documento com foto.</p>
  <ul class="acoes">
    <li>{icone("salvar")}<span><b>Salve este post</b> para consultar sua sala</span></li>
    <li>{icone("share")}<span><b>Compartilhe</b> com sua turma</span></li>
  </ul>
  <div class="cta-base">{logo()}<span class="hash">#SouUNIPÊ</span></div>
""", swipe=False, extra_css="""
  .cta-h1{font-size:160px;}
  .resumo{margin:36px 0 48px;font-size:40px;}
  .acoes{list-style:none;display:flex;flex-direction:column;gap:22px;}
  .acoes li{display:flex;align-items:center;gap:30px;background:rgba(255,255,255,.08);border-left:8px solid var(--amarelo);border-radius:20px;padding:24px 30px;}
  .acoes span{font:500 34px/1.25 var(--f-corpo);}
  .acoes b{font-weight:800;color:var(--amarelo);}
  .acoes .icone{flex-basis:84px;height:84px;}
  .cta-base{display:flex;align-items:center;justify-content:space-between;margin-top:56px;}
  .hash{color:var(--amarelo);font:800 40px/1 var(--f-titulo);font-variation-settings:"opsz" 96;}
""")

print("ok")
