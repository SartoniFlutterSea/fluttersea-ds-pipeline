#!/usr/bin/env node
/**
 * Livello 2b - estrazione della documentazione dai frame Figma.
 *
 * Ogni componente ha DUE frame affiancati, e servono entrambi:
 *
 *   Purpose & Usage   perche' esiste, quando usarlo, anti-pattern di SCELTA
 *                     "Nome pattern" + "1.1 How and when to use it (Do)"
 *                     "1.N Anti-pattern (Don't)" -> Rule / Why it's wrong / Use instead
 *
 *   Behavior          come si comporta, anti-pattern di COMPOSIZIONE
 *                     "template behavior" + "Interaction" per piattaforma:
 *                     Interactive elements / Position / Animation / Size /
 *                     Conditional logic / Copy & truncation
 *                     piu' coppie Do / Don't con mockup e didascalia
 *
 * Due accorgimenti che senza si sbaglia:
 *  - la DIDASCALIA di un Do/Don't sta a profondita' MINORE del mockup, ed e'
 *    l'unico modo per non confondere la spiegazione col testo finto dentro
 *    lo screenshot;
 *  - gli apostrofi vanno NORMALIZZATI: Figma usa quello tipografico e un
 *    confronto letterale su "Don't" fallisce silenziosamente.
 *
 *   node extract-docs.mjs <slug> <pagina>
 *   node extract-docs.mjs button Button
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = `${ROOT}/data/contracts`;
const B2C = 'QWM2EhgZmv2KKcqI0315fx';

const slug = process.argv[2] ?? 'button';
const pageFilter = process.argv[3] ?? null;

/* Solo GET: questo script non scrive mai su Figma. */
async function api(url, tries = 4) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(`https://api.figma.com/v1/${url}`,
        { headers: { 'X-Figma-Token': TOKEN }, signal: AbortSignal.timeout(90000) });
      if (r.ok) return r.json();
      if (r.status >= 500 || r.status === 429) { await new Promise(s => setTimeout(s, 2500 * i)); continue; }
      throw new Error(`HTTP ${r.status}`);
    } catch (e) { if (i === tries) throw e; await new Promise(s => setTimeout(s, 2500 * i)); }
  }
}

/* Normalizza gli apostrofi tipografici: Figma usa U+2019, il codice U+0027. */
const AP = /[\u2018\u2019\u02BC\u00B4`]/g;
const norm = s => (s ?? '').replace(AP, "'");
const key = s => norm(s).toLowerCase().replace(/[^a-z0-9]/g, '');

/* Lookup strutturale: il nome del componente sta in un frame con nome noto. */
function findByName(root, re) {
  let hit = null;
  (function w(n) { if (hit) return; if (re.test(n.name ?? '')) { hit = n; return; } (n.children ?? []).forEach(w); })(root);
  return hit;
}
function firstText(node) {
  let hit = null;
  (function w(n) { if (hit) return; if (n.type === 'TEXT' && n.characters?.trim()) { hit = n.characters.trim(); return; } (n.children ?? []).forEach(w); })(node ?? {});
  return hit;
}

/* TEXT con la profondita': serve a separare didascalia e mockup. */
function textNodes(root) {
  const out = [];
  (function w(n, d) {
    if (n.type === 'TEXT' && n.characters?.trim()) out.push({ t: norm(n.characters.trim()), d });
    for (const c of n.children ?? []) w(c, d + 1);
  })(root, 0);
  return out;
}

/* ---- Purpose & Usage ---------------------------------------------------- */
const HEAD_DO = /^\d+\.\d+\s+How and when to use it/i;
const HEAD_ANTI = /^\d+\.\d+\s+Anti-pattern/i;
const USED_IN = /^In which component/i;
const LBL = { "rule": 'scenario', "why it's wrong": 'reason', "use instead": 'alternative' };

function parsePurpose(doc) {
  const T = textNodes(doc), t = T.map(x => x.t);
  const name = firstText(findByName(doc, /^Nome pattern$/i))
            ?? (() => { const h = t.findIndex(x => HEAD_DO.test(x) || HEAD_ANTI.test(x)); return h > 0 ? t[h - 1] : null; })();
  const dos = [], antis = [];
  for (let i = 0; i < t.length;) {
    if (HEAD_DO.test(t[i])) {
      // Fra la descrizione e "In which component…" c'e' il contenuto finto dei
      // mockup: non si puo' assumere una posizione fissa, va cercata l'etichetta.
      const usedIn = []; let j = i + 2;
      while (j < t.length && !HEAD_DO.test(t[j]) && !HEAD_ANTI.test(t[j]) && !USED_IN.test(t[j])) j++;
      if (USED_IN.test(t[j] ?? '')) {
        j++;
        while (j < t.length && !HEAD_DO.test(t[j]) && !HEAD_ANTI.test(t[j])) usedIn.push(t[j++]);
      }
      dos.push({ section: t[i].match(/^\d+\.\d+/)[0], description: t[i + 1] ?? '', usedIn });
      i = j;
    } else if (HEAD_ANTI.test(t[i])) {
      // R12 di CLAUDE.md: sotto UNA intestazione possono stare PIU' terzine
      // Rule / Why it's wrong / Use instead. Ogni "Rule" apre un anti-pattern.
      const base = t[i].match(/^\d+\.\d+/)[0];
      let j = i + 1, n = 0, cur = null;
      const flush = () => { if (cur?.scenario) antis.push(cur); cur = null; };
      while (j < t.length && !HEAD_DO.test(t[j]) && !HEAD_ANTI.test(t[j])) {
        const k = LBL[t[j].toLowerCase()];
        if (k === 'scenario' && t[j + 1]) {
          flush();
          cur = { section: `${base}${n ? `.${n}` : ''}`, origin: 'purpose', scenario: t[j + 1] };
          n++; j += 2;
        } else if (k && cur && t[j + 1]) { cur[k] = t[j + 1]; j += 2; }
        else j++;
      }
      flush();
      i = j;
    } else i++;
  }
  return { name, dos, antis };
}

/* ---- Behavior ------------------------------------------------------------ */
const SPEC = /^(Interactive elements|Position|Animation|Size|Conditional logic|Copy & truncation|Copy|States?)\s*:?$/i;
const PLATFORM = /^(iOS Liquid Glass|iOS \/ Android|iOS|Android|Mobile|Desktop)([\s/]|$)/i;
const IS_DO = s => /^do$/i.test(s);
const IS_DONT = s => /^don'?t$/i.test(s);          // apostrofo gia' normalizzato

function parseBehavior(doc) {
  const T = textNodes(doc);
  const name = firstText(findByName(doc, /^template behavior$/i));

  const spec = {}; let platform = null;
  for (let i = 0; i < T.length; i++) {
    if (PLATFORM.test(T[i].t) && T[i].t.length < 30) { platform = T[i].t; continue; }
    const m = T[i].t.match(SPEC);
    if (m && T[i + 1]) {
      // camelCase vero: "Copy & truncation" -> copyAndTruncation
      const k = m[1].replace(/&/g, ' and ').split(/\s+/).filter(Boolean)
        .map((w, n) => n === 0 ? w.toLowerCase() : w[0].toUpperCase() + w.slice(1).toLowerCase()).join('');
      (spec[platform ?? 'default'] ??= {})[k] = T[i + 1].t;
      i++;
    }
  }

  // La didascalia e' il primo TEXT a profondita' <= all'etichetta, prima
  // dell'etichetta successiva. Il mockup sta piu' in profondita' e viene saltato.
  const pairs = [];
  for (let i = 0; i < T.length; i++) {
    const isDo = IS_DO(T[i].t), isDont = IS_DONT(T[i].t);
    if (!isDo && !isDont) continue;
    let caption = null;
    for (let j = i + 1; j < T.length; j++) {
      if (IS_DO(T[j].t) || IS_DONT(T[j].t)) break;
      if (T[j].d <= T[i].d) { caption = T[j].t; break; }
    }
    if (caption) pairs.push({ kind: isDo ? 'do' : 'dont', caption });
  }
  return { name, spec, pairs };
}

/* ---- i frame del componente --------------------------------------------- */
const pages = JSON.parse(fs.readFileSync(`${ROOT}/data/figma-pages.json`, 'utf8')).b2c.pages;
const frames = pages
  .filter(p => p.docFrames > 0 && (!pageFilter || p.label.toLowerCase().includes(pageFilter.toLowerCase())))
  .flatMap(p => p.frames.map(f => ({ ...f, page: p.label })));

console.log(`> ${frames.length} frame da leggere sulla pagina "${pageFilter}"\n`);

const purposes = [], behaviors = [];
for (const f of frames) {
  const doc = Object.values((await api(`files/${B2C}/nodes?ids=${f.id}`)).nodes)[0].document;
  if (/purpose/i.test(f.name)) {
    const p = parsePurpose(doc); purposes.push({ ...f, ...p });
    console.log(`   Purpose   ${(p.name ?? '-').padEnd(16)} ${p.dos.length} do  ${p.antis.length} anti`);
  } else if (/behavior/i.test(f.name)) {
    const b = parseBehavior(doc); behaviors.push({ ...f, ...b });
    const n = Object.values(b.spec).reduce((s, o) => s + Object.keys(o).length, 0);
    const nd = b.pairs.filter(x => x.kind === 'do').length, nn = b.pairs.filter(x => x.kind === 'dont').length;
    console.log(`   Behavior  ${(b.name ?? '-').padEnd(16)} ${n} spec  ${nd} do / ${nn} don't`);
  }
}

const pick = (arr) => arr.find(x => key(x.name) === key(slug)) ?? arr.find(x => key(x.name).includes(key(slug)));
const P = pick(purposes), B = pick(behaviors);

/* ---- unione -------------------------------------------------------------- */
const intent = {
  id: `ds.${slug}`,
  componentName: P?.name ?? B?.name ?? null,
  purpose: P?.dos?.[0]?.description ?? null,
  usedIn: P?.dos?.flatMap(d => d.usedIn) ?? [],
  commonPatterns: [
    ...(P?.dos ?? []).map(d => ({ origin: 'purpose', section: d.section, description: d.description })),
    ...(B?.pairs ?? []).filter(p => p.kind === 'do').map((p, i) => ({ origin: 'behavior', section: `B.do.${i + 1}`, description: p.caption })),
  ],
  antiPatterns: [
    ...(P?.antis ?? []),
    ...(B?.pairs ?? []).filter(p => p.kind === 'dont').map((p, i) => ({ origin: 'behavior', section: `B.dont.${i + 1}`, scenario: p.caption })),
  ],
  behavior: B?.spec ?? {},
  _source: {
    ds: 'b2c', fileKey: B2C,
    purposeFrame: P ? { id: P.id, page: P.page } : null,
    behaviorFrame: B ? { id: B.id, page: B.page } : null,
    confidence: 'human-authored',
  },
};

const metaPath = `${ROOT}/components/${slug}/docs/metadata.json`;
if (fs.existsSync(metaPath)) {
  const m = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  intent._reproducibility = {
    antiPatterns: { figma: intent.antiPatterns.length, metadata: (m.usage?.antiPatterns ?? []).length },
    commonPatterns: { figma: intent.commonPatterns.length, metadata: (m.usage?.commonPatterns ?? []).length },
    behaviorKeys: { figma: Object.values(intent.behavior).reduce((s, o) => s + Object.keys(o).length, 0),
                    metadata: Object.keys(m.behavior?.interactions ?? {}).length },
    contentBlock: { figma: Object.values(intent.behavior).some(o => o.copyAndTruncation) ? 1 : 0,
                    metadata: Object.keys(m.content ?? {}).length },
  };
}

const sortKeys = o => Array.isArray(o) ? o.map(sortKeys)
  : (o && typeof o === 'object') ? Object.fromEntries(Object.keys(o).sort().map(k => [k, sortKeys(o[k])])) : o;
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, slug), { recursive: true });
fs.writeFileSync(path.join(OUT, slug, 'intent.json'), JSON.stringify(sortKeys(intent), null, 2) + '\n');

const L = '-'.repeat(72);
console.log(`\n${L}\n  INTENTO UNIFICATO - ${intent.componentName}\n${L}`);
console.log(`\n> PURPOSE\n   ${(intent.purpose ?? '-').slice(0, 150)}...`);
console.log(`\n> BEHAVIOR`);
for (const [plat, o] of Object.entries(intent.behavior)) {
  console.log(`   [${plat}]`);
  for (const [k, v] of Object.entries(o)) console.log(`      ${k.padEnd(22)} ${v.replace(/\n/g, ' ').slice(0, 74)}...`);
}
console.log(`\n> ANTI-PATTERN  ${intent.antiPatterns.length}`);
for (const a of intent.antiPatterns) console.log(`   [${a.origin}] ${(a.scenario ?? '').slice(0, 80)}`);
console.log(`\n> PATTERN D'USO  ${intent.commonPatterns.length}`);
for (const c of intent.commonPatterns) console.log(`   [${c.origin}] ${(c.description ?? '').replace(/\n/g, ' ').slice(0, 80)}`);
if (intent._reproducibility) {
  console.log(`\n> RIPRODUCIBILITA'   Figma  vs  metadata.json scritto a mano`);
  for (const [k, v] of Object.entries(intent._reproducibility))
    console.log(`   ${k.padEnd(16)} ${String(v.figma).padStart(3)}  vs ${String(v.metadata).padStart(3)}`);
}
console.log(`\nOK  data/contracts/${slug}/intent.json\n${L}\n`);
