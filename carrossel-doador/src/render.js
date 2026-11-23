// Renderiza cada slide-XX.html em PNG @2x (2160x2700) e depois reduz para 1080x1350.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');

(async () => {
  const src = __dirname;
  const out = path.resolve(src, '..');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  for (let n = 1; n <= 8; n++) {
    const id = String(n).padStart(2, '0');
    await page.goto('file://' + path.join(src, `slide-${id}.html`));
    await page.evaluate(() => document.fonts.ready);
    const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => `${f.family} ${f.weight}`));
    const overflow = await page.evaluate(() => {
      const s = document.querySelector('.slide');
      return [...s.querySelectorAll('h1,h2,p,li,.tag,.logo-slot,.card')].filter(el => {
        const r = el.getBoundingClientRect();
        return r.left < 79 || r.right > 1001 || r.top < 79 || r.bottom > 1271;
      }).map(el => el.tagName + '.' + el.className + ' ' + JSON.stringify(el.getBoundingClientRect()));
    });
    const hi = path.join(src, `.hi-${id}.png`);
    await page.screenshot({ path: hi });
    execFileSync('python3', ['-c',
      `from PIL import Image;Image.open(${JSON.stringify(hi)}).convert('RGB').resize((1080,1350),Image.LANCZOS).save(${JSON.stringify(path.join(out, `slide-${id}.png`))})`]);
    console.log(id, 'fonts:', [...new Set(fonts)].join(', '), overflow.length ? '\n  FORA DA MARGEM: ' + overflow.join('\n  ') : '');
  }
  await browser.close();
})();
