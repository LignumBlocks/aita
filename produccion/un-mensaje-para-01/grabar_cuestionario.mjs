// Graba el cuestionario de umbralio.com/es/score como lo ve un celular, para el cierre de la pieza.
// Adaptado de studio/pieces/el-claxon/pauta_herramientas/grabar_wizard_hd.mjs para el sandbox de Higgsfield.
// NO escribe nombre ni teléfono y NO envía: se queda en el paso 6 (el formulario). No hay forma de
// enseñar un resultado sin enviar (D45: se quitaron los adelantos). Bloquea GTM, GA4, Clarity, el
// Pixel, la CAPI, /api/leads y /api/validate-phone, para no ensuciar la medición.
// Quita « · One Stop Realty» de la firma de la página (regla de Nelson del 15-sep para lo grabado).
// Uso: node grabar_cuestionario.mjs <carpeta_salida>   → fotogramas + lista.txt (concat de ffmpeg)
import { chromium } from "/usr/local/lib/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const OUT = process.argv[2] || "cuestionario";
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({
  viewport: { width: 414, height: 736 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
  locale: "es-US",
  userAgent:
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1 UmbralioCaptura/un-mensaje-01",
});
const bloqueado = [];
await ctx.route("**/*", (route) => {
  const u = route.request().url();
  if (/googletagmanager|google-analytics|analytics\.google|doubleclick|googleadservices|connect\.facebook|facebook\.com\/tr|\/api\/meta\/|\/api\/leads|\/api\/validate-phone|clarity\.ms|hotjar/i.test(u)) {
    bloqueado.push(u.slice(0, 100));
    return route.abort();
  }
  return route.continue();
});
await ctx.addInitScript(() => {
  const limpiar = () => {
    if (!document.body) return;
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let t;
    while ((t = w.nextNode())) {
      if (t.nodeValue.includes("One Stop Realty")) t.nodeValue = t.nodeValue.replace(/\s*·\s*One Stop Realty/g, "").replace(/One Stop Realty\s*·?\s*/g, "");
    }
  };
  new MutationObserver(limpiar).observe(document, { subtree: true, childList: true, characterData: true });
  document.addEventListener("DOMContentLoaded", limpiar);
});
const page = await ctx.newPage();
const cdp = await ctx.newCDPSession(page);
await page.goto("https://umbralio.com/es/score", { waitUntil: "load", timeout: 60000 });
const opciones = page.locator("div.step.active div.opt[role=radio]");
await opciones.first().waitFor({ timeout: 30000 });
await page.waitForTimeout(1500);

let grabando = true;
const tiempos = [];
let n = 0;
const bucle = (async () => {
  while (grabando) {
    const t = performance.now() / 1000;
    const { data } = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 90, optimizeForSpeed: true, clip: { x: 0, y: 0, width: 414, height: 736, scale: 3 } });
    fs.writeFileSync(path.join(OUT, `f${String(n).padStart(5, "0")}.jpg`), Buffer.from(data, "base64"));
    tiempos.push(t);
    n++;
  }
})();

// Alguien que paga $2,200 de renta (el del episodio): hasta $350 mil · $10 a $25 mil ahorrados ·
// 6 a 12 meses · sin preaprobación · crédito 640 a 699.
const elecciones = [0, 2, 3, 0, 2];
const titulo = async () => (await page.locator("div.step.active h1").first().innerText().catch(() => "?")).replace(/\s+/g, " ");
const pasos = [];
await page.waitForTimeout(1200);
for (const idx of elecciones) {
  const antes = await titulo();
  pasos.push({ t: performance.now() / 1000, titulo: antes });
  await page.locator("div.step.active div.opt[role=radio]").nth(idx).tap();
  await page.waitForFunction((t) => {
    const h = document.querySelector("div.step.active h1");
    return h && h.innerText.replace(/\s+/g, " ") !== t;
  }, antes, { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(1300);
}
pasos.push({ t: performance.now() / 1000, titulo: await titulo() });
await page.waitForTimeout(2500);
const fin = performance.now() / 1000;
grabando = false;
await bucle;

const lineas = [];
for (let i = 0; i < n; i++) {
  const d = (i + 1 < n ? tiempos[i + 1] : fin) - tiempos[i];
  lineas.push(`file 'f${String(i).padStart(5, "0")}.jpg'`, `duration ${Math.max(0.001, d).toFixed(4)}`);
}
lineas.push(`file 'f${String(n - 1).padStart(5, "0")}.jpg'`);
fs.writeFileSync(path.join(OUT, "lista.txt"), lineas.join("\n"));
const t0 = tiempos[0];
console.log(JSON.stringify({
  fotogramas: n, segundos: +(fin - t0).toFixed(2), fps: +(n / (fin - t0)).toFixed(1),
  pasos: pasos.map((p) => ({ en: +(p.t - t0).toFixed(2), titulo: p.titulo })), bloqueados: bloqueado.length,
}));
await browser.close();
