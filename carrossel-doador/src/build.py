"""Gera slide-01.html ... slide-08.html (um arquivo por slide, CSS compartilhado em styles.css)."""
from pathlib import Path

OUT = Path(__file__).parent
TOTAL = 8

GOTA = '<svg viewBox="0 0 100 130" class="{cls}"><path d="M50 0C50 0 0 58 0 82a50 50 0 0 0 100 0C100 58 50 0 50 0Z"/></svg>'

I = {  # ícones de linha (viewBox 24)
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "peso": '<circle cx="12" cy="6" r="2.5"/><path d="M5 9h14l2 11H3z"/>',
    "doc": '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2.5"/><path d="M13 10h5M13 14h5"/>',
    "coracao": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "prancheta": '<rect x="5" y="4" width="14" height="17" rx="2"/><rect x="9" y="2" width="6" height="4" rx="1"/><path d="M9 11h6M9 15h4"/>',
    "pulso": '<path d="M2 12h4l2-5 4 10 2-5h8"/>',
    "gota": '<path d="M12 3s-6 7-6 11a6 6 0 0 0 12 0c0-4-6-11-6-11z"/>',
    "copo": '<path d="M6 4h12l-1.6 16H7.6z"/><path d="M6.5 9h11"/>',
    "arroba": '<circle cx="12" cy="12" r="4"/><path d="M16 12v1.5a2.5 2.5 0 0 0 5 0V12a9 9 0 1 0-3.5 7.1"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/>',
}
SETA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>'


def icone(nome):
    return f'<div class="icone"><svg viewBox="0 0 24 24">{I[nome]}</svg></div>'


def logo():
    return '<div class="logo-card"><img src="assets/logo-unipe-negativa.png" alt="UNIPÊ - Centro Universitário de João Pessoa"></div>'


def pagina(n, bg, conteudo, extra_css="", swipe=True):
    ponte_esq = GOTA.format(cls="ponte esq") if n > 1 else ""
    ponte_dir = GOTA.format(cls="ponte dir") if n < TOTAL else ""
    arraste = f'<div class="arraste">arraste {SETA}</div>' if swipe else ""
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Doador de Sangue — slide {n:02d}</title>
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
  <span class="tag">25 de novembro</span>
  <h1 class="capa-h1">Seu sangue pode ser o <span class="destaque">recomeço</span> de alguém<span class="cursor">_</span></h1>
  <div class="capa-base">
    <div class="capa-esq">
      <p class="capa-sub">Dia Nacional do Doador Voluntário de Sangue</p>
      {logo()}
    </div>
  </div>
  <img class="ilustra" src="assets/doador.svg" alt="">
""", extra_css="""
  .capa-h1{font-size:116px;max-width:900px;}
  .capa-base{margin-top:48px;height:520px;}
  .capa-esq{width:430px;display:flex;flex-direction:column;justify-content:flex-end;height:100%;gap:40px;}
  .capa-sub{font:700 42px/1.25 var(--f-corpo);}
  .ilustra{position:absolute;right:-70px;bottom:-30px;width:600px;height:600px;z-index:-1;}
  .slide .ponte.dir{top:390px;}
""")

# 2 — POR QUE DOAR
pagina(2, "bg-azul", """
  <span class="tag">Por que doar</span>
  <h2>Sangue não se <span class="destaque">fabrica</span><span class="cursor">_</span></h2>
  <p class="corpo" style="font-size:46px">Ele só chega a quem precisa porque <strong>alguém escolheu doar</strong>.</p>
  <p class="corpo" style="margin-top:32px;font-size:46px;color:var(--cinza)">Cirurgias, acidentes e tratamentos dependem desse gesto.</p>
""")

# 3 — QUEM PODE DOAR
pagina(3, "bg-azul", f"""
  <span class="tag">Quem pode doar</span>
  <h2>Você pode ser <span class="destaque">doador</span><span class="cursor">_</span></h2>
  <ul class="lista">
    <li class="item">{icone("cal")}<div class="item-txt">16 a 69 anos<small>Menores de 18, com autorização dos responsáveis</small></div></li>
    <li class="item">{icone("peso")}<div class="item-txt">50 kg ou mais</div></li>
    <li class="item">{icone("coracao")}<div class="item-txt">Bem de saúde e descansado</div></li>
    <li class="item">{icone("doc")}<div class="item-txt">Documento oficial com foto</div></li>
  </ul>
""", extra_css=".lista{gap:24px}.item{padding:22px 30px}")

# 4 — PROCESSO
pagina(4, "bg-azul", f"""
  <span class="tag">Como funciona</span>
  <h2>Simples assim<span class="cursor">_</span></h2>
  <ol class="lista passos">
    <li class="item">{icone("prancheta")}<div class="item-txt"><em>01</em> Cadastro<small>Leve seu documento com foto</small></div></li>
    <li class="item">{icone("pulso")}<div class="item-txt"><em>02</em> Triagem<small>Conversa e avaliação rápida</small></div></li>
    <li class="item">{icone("gota")}<div class="item-txt"><em>03</em> Coleta<small>Material estéril e descartável</small></div></li>
    <li class="item">{icone("copo")}<div class="item-txt"><em>04</em> Lanche<small>E pronto: missão cumprida</small></div></li>
  </ol>
""", extra_css=".lista{gap:24px}.item{padding:22px 30px}.item-txt em{font-style:normal;color:var(--amarelo);margin-right:12px}")

# 5 — IMPACTO
pagina(5, "bg-azul", f"""
  <span class="tag">Impacto</span>
  <p class="imp-a">1 doação</p>
  <p class="imp-b">até <span>4</span> vidas<span class="cursor">_</span></p>
  <div class="gotas">{"".join(GOTA.format(cls="g4") for _ in range(4))}</div>
  <p class="corpo">Do seu sangue saem componentes que ajudam <strong>pacientes diferentes</strong>.</p>
""", extra_css="""
  .imp-a{font:800 88px/1 var(--f-titulo);font-variation-settings:"opsz" 96;color:var(--cinza);}
  .imp-b{font:800 168px/1 var(--f-titulo);font-variation-settings:"opsz" 96;letter-spacing:-.03em;margin-top:8px;}
  .imp-b span:first-child{color:var(--amarelo);}
  .gotas{display:flex;gap:28px;margin:40px 0 48px;}
  .g4{width:70px;height:91px;} .g4 path{fill:var(--amarelo);}
""")

# 6 — MITOS
pagina(6, "bg-azul", """
  <span class="tag">Mito ou verdade</span>
  <h2>Sem medo de <span class="destaque">doar</span><span class="cursor">_</span></h2>
  <div class="cards">
    <div class="card"><span class="selo mito">Mito</span><p>“Quem doa uma vez precisa doar sempre.”</p></div>
    <div class="card"><span class="selo mito">Mito</span><p>“Doar sangue pode transmitir doenças.” Todo material é descartável.</p></div>
    <div class="card"><span class="selo verdade">Verdade</span><p>Há intervalo: homens a cada 2 meses, mulheres a cada 3.</p></div>
  </div>
""", extra_css="""
  .cards{display:flex;flex-direction:column;gap:24px;}
  .card{display:flex;align-items:center;gap:30px;background:rgba(255,255,255,.07);border-radius:20px;padding:28px 32px;}
  .card p{font:600 34px/1.3 var(--f-corpo);}
  .selo{flex:0 0 190px;text-align:center;font:800 26px/1 var(--f-corpo);letter-spacing:.14em;text-transform:uppercase;padding:18px 0;border-radius:999px;color:var(--azul);}
  .mito{background:var(--cinza);} .verdade{background:var(--amarelo);}
""")

# 7 — AGRADECIMENTO
pagina(7, "bg-claro", f"""
  <svg class="aspas" viewBox="0 0 120 90"><path d="M0 90V52C0 22 16 4 46 0v18C32 22 26 32 26 46h20v44zm68 0V52c0-30 16-48 46-52v18c-14 4-20 14-20 28h20v44z"/></svg>
  <h2 class="frase">A quem doa: <span class="sub">obrigado</span> por transformar um gesto simples em esperança<span class="cursor">_</span></h2>
  <p class="corpo assina">Hoje e todos os dias.</p>
  <div class="gotas7">{GOTA.format(cls="g7 a")}{GOTA.format(cls="g7 b")}{GOTA.format(cls="g7 c")}</div>
""", extra_css="""
  .aspas{width:120px;height:90px;fill:var(--azul);margin-bottom:40px;}
  .frase{font-size:100px;line-height:1.02;max-width:900px;}
  .frase .sub{background:var(--amarelo);padding:0 14px;border-radius:10px;box-decoration-break:clone;-webkit-box-decoration-break:clone;}
  .assina{font-weight:700;margin-top:24px;}
  .gotas7{position:absolute;right:40px;bottom:-10px;width:300px;height:220px;}
  .g7{position:absolute;} .g7 path{fill:var(--amarelo);stroke:var(--azul);stroke-width:4;}
  .g7.a{width:90px;height:117px;right:200px;bottom:30px;}
  .g7.b{width:130px;height:169px;right:40px;bottom:50px;}
  .g7.c{width:60px;height:78px;right:150px;bottom:180px;}
""")

# 8 — CTA
pagina(8, "bg-azul", f"""
  <span class="tag">Faça parte</span>
  <h1 class="cta-h1">Agora é a sua vez<span class="cursor">_</span></h1>
  <ul class="acoes">
    <li>{icone("cal")}<span><b>Agende sua doação</b> no hemocentro mais próximo</span></li>
    <li>{icone("arroba")}<span><b>Marque quem doa</b> e agradeça</span></li>
    <li>{icone("share")}<span><b>Compartilhe</b> e inspire mais gente</span></li>
  </ul>
  <div class="cta-base">{logo()}<span class="hash">#SouUNIPÊ</span></div>
""", swipe=False, extra_css="""
  .cta-h1{font-size:132px;max-width:880px;margin-bottom:56px;}
  .acoes{list-style:none;display:flex;flex-direction:column;gap:26px;}
  .acoes li{display:flex;align-items:center;gap:30px;background:rgba(255,255,255,.08);border-left:8px solid var(--amarelo);color:var(--branco);border-radius:20px;padding:24px 30px;}
  .acoes span{font:500 34px/1.25 var(--f-corpo);}
  .acoes b{font-weight:800;color:var(--amarelo);}
  .acoes .icone{flex-basis:84px;height:84px;}
  .cta-base{display:flex;align-items:center;justify-content:space-between;margin-top:56px;}
  .hash{color:var(--amarelo);font:800 40px/1 var(--f-titulo);font-variation-settings:"opsz" 96;}
""")

print("ok")
