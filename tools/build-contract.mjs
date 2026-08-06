#!/usr/bin/env node
/**
 * Livello 2 — contratto di componente, estratto da Figma.
 *
 * Sostituisce build-contract-from-metadata.mjs, che ricavava gli assi dalla
 * PROSA di `component.description` (e infatti sbagliava default e ordine).
 * Qui la sorgente è la property table reale più la geometria dei nodi.
 *
 * Due principi:
 *  · OUTPUT CANONICO — chiavi ordinate, float arrotondati, nessun timestamp
 *    dentro l'artefatto: ogni diff è un cambiamento vero, mai rumore.
 *  · NON PROMETTE PIÙ DI QUANTO HA MISURATO — ogni sezione dichiara su quante
 *    varianti è stata verificata.
 *
 *   node build-contract.mjs <slug> <nodeId>
 *   node build-contract.mjs button 5473-10855
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = `${ROOT}/data/contracts`;

/* Il file NON è più scritto qui dentro.
   I due DS condividono gli id dei nodi (il B2B è un duplicato del B2C), quindi
   lo stesso nodeId su file diversi restituisce componenti diversi: il ds deve
   essere esplicito, altrimenti si documenta il componente sbagliato. */
const CFG = JSON.parse(fs.readFileSync(`${ROOT}/config/figma-files.json`, 'utf8'));

const slug = process.argv[2] ?? 'button';
const nodeId = process.argv[3] ?? '5473-10855';
const ds = process.argv[4] ?? CFG.default;

if (!CFG.files[ds]) {
  console.error(`\n  ✖ ds sconosciuto: "${ds}" — attesi: ${Object.keys(CFG.files).join(', ')}\n`);
  process.exit(1);
}
const FILE = CFG.files[ds].fileKey;

const api = async u => {
  const r = await fetch(`https://api.figma.com/v1/${u}`, { headers: { 'X-Figma-Token': TOKEN } });
  if (!r.ok) throw new Error(`Figma HTTP ${r.status} — ${u}`);
  return r.json();
};

/* ── mappa variableId → nome, per tradurre i boundVariables ──────────────── */
const { meta: vmeta } = await api(`files/${FILE}/variables/local`);
const varName = id => vmeta.variables[id]?.name ?? null;

/* ── il component set ─────────────────────────────────────────────────────── */
const nodes = await api(`files/${FILE}/nodes?ids=${nodeId}`);
const doc = Object.values(nodes.nodes)[0].document;
const variants = doc.children ?? [];

/* ── 1. Assi: dalla property table, non dalla prosa ──────────────────────── */
const defs = doc.componentPropertyDefinitions ?? {};
const clean = n => n.split('#')[0].trim();          // "Show left icon#5615:73" → "Show left icon"
const camel = n => { const p = clean(n).split(/[\s_-]+/); return p[0].toLowerCase() + p.slice(1).map(w => w[0].toUpperCase() + w.slice(1)).join(''); };

const axes = [], booleans = [], texts = [], swaps = [];
for (const [rawName, d] of Object.entries(defs)) {
  const entry = { figmaProperty: clean(rawName), name: camel(rawName) };
  if (d.type === 'VARIANT') axes.push({ ...entry, values: [...d.variantOptions].sort() });
  else if (d.type === 'BOOLEAN') booleans.push({ ...entry, default: d.defaultValue });
  else if (d.type === 'TEXT') texts.push({ ...entry, default: d.defaultValue });
  else swaps.push({ ...entry, type: d.type });
}

/* ── 2. Il default: la PRIMA variante del set è il riferimento di Figma ──── */
const parseVariant = name => Object.fromEntries(
  name.split(',').map(s => s.split('=').map(x => x.trim())).filter(p => p.length === 2));
const firstCombo = variants.length ? parseVariant(variants[0].name) : {};

/* ── 3. Sizing e token: dai boundVariables dei nodi variante ─────────────── */
const round = n => typeof n === 'number' ? Math.round(n * 100) / 100 : n;

function surfacesOf(node) {
  const out = {};
  const bv = node.boundVariables ?? {};
  const fill = node.fills?.[0]?.boundVariables?.color?.id;
  const stroke = node.strokes?.[0]?.boundVariables?.color?.id;
  if (fill) out.bg = varName(fill);
  if (stroke) out.border = varName(stroke);
  // testo e icona stanno nei figli
  const walk = n => {
    for (const c of n.children ?? []) {
      const cf = c.fills?.[0]?.boundVariables?.color?.id;
      if (cf) { if (c.type === 'TEXT' && !out.text) out.text = varName(cf); else if (!out.icon) out.icon = varName(cf); }
      walk(c);
    }
  };
  walk(node);
  if (bv.strokeWeight) out._borderWidth = varName(bv.strokeWeight.id);
  return out;
}

function geometryOf(node) {
  const bv = node.boundVariables ?? {};
  const g = {};
  const map = { paddingTop: 'paddingVertical', paddingLeft: 'paddingHorizontal',
                itemSpacing: 'gap', strokeWeight: 'borderWidth' };
  for (const [k, label] of Object.entries(map)) if (bv[k]) g[label] = varName(bv[k].id);
  if (bv.bottomLeftRadius || bv.topLeftRadius)
    g.borderRadius = varName((bv.topLeftRadius ?? bv.bottomLeftRadius).id);
  g._measured = { height: round(node.absoluteBoundingBox?.height), layout: node.layoutMode ?? null };
  return g;
}

const sizeAxis = axes.find(a => /size/i.test(a.name));
const appearAxis = axes.find(a => /appear/i.test(a.name));
const hierAxis = axes.find(a => /hierarch/i.test(a.name));
const stateAxis = axes.find(a => /state/i.test(a.name));

const sizing = {}, tokens = {};
const coverage = { variantsTotal: variants.length, sizingFrom: 0, tokensFrom: 0 };

for (const v of variants) {
  const combo = parseVariant(v.name);
  // sizing: una volta per size, dalla combinazione di default degli altri assi
  const sz = sizeAxis && combo[sizeAxis.figmaProperty];
  if (sz && !sizing[sz]) { sizing[sz] = geometryOf(v); coverage.sizingFrom++; }

  // tokens: per ogni (appearance, hierarchy) × state
  if (appearAxis && hierAxis && stateAxis) {
    const key = `${combo[appearAxis.figmaProperty]}/${combo[hierAxis.figmaProperty]}`;
    const st = combo[stateAxis.figmaProperty];
    if (key.includes('undefined') || !st) continue;
    // solo dalla size di riferimento, per non moltiplicare
    if (sizeAxis && combo[sizeAxis.figmaProperty] !== firstCombo[sizeAxis.figmaProperty]) continue;
    (tokens[key] ??= {})[st] = surfacesOf(v);
    coverage.tokensFrom++;
  }
}

/* ── 4. Il contratto, in forma canonica ──────────────────────────────────── */
const sortKeys = o => Array.isArray(o) ? o.map(sortKeys)
  : (o && typeof o === 'object')
    ? Object.fromEntries(Object.keys(o).sort().map(k => [k, sortKeys(o[k])]))
    : o;

const contract = {
  id: `ds.${slug}`,
  name: doc.name,
  source: { ds, fileKey: FILE, fileName: CFG.files[ds].name, nodeId, nodeType: doc.type },

  props: axes.map(a => ({
    name: a.name,
    figmaProperty: a.figmaProperty,
    values: a.values,                                   // ordine: alfabetico, come Figma
    default: firstCombo[a.figmaProperty] ?? null,       // la prima variante del set
    _source: { values: 'figma', order: 'figma-alphabetical', default: 'figma-first-variant' },
  })),
  booleans, texts, swaps,

  sizing,
  tokens,

  _coverage: {
    variants: coverage.variantsTotal,
    sizingMeasuredOn: `${coverage.sizingFrom}/${sizeAxis?.values.length ?? 0} size`,
    tokensMeasuredOn: `${coverage.tokensFrom} combinazioni su ${(appearAxis?.values.length ?? 0) * (hierAxis?.values.length ?? 0) * (stateAxis?.values.length ?? 0)}`,
    note: 'I token sono misurati sulla sola size di riferimento: le superfici non variano con la size.',
  },
};

fs.mkdirSync(OUT, { recursive: true });
const dir = path.join(OUT, slug);
fs.mkdirSync(dir, { recursive: true });
const file = path.join(dir, 'contract.json');
fs.writeFileSync(file, JSON.stringify(sortKeys(contract), null, 2) + '\n');

/* ── Report ───────────────────────────────────────────────────────────────── */
const L = '─'.repeat(70);
console.log(`\n${L}\n  CONTRATTO da Figma — ${doc.name}\n${L}`);
console.log(`\n▸ NODO      ${doc.type} · ${variants.length} varianti`);
console.log(`\n▸ ASSI      (dalla property table, non dalla prosa)`);
for (const a of axes) console.log(`   ${a.name.padEnd(12)} figma="${a.figmaProperty}"  default=${firstCombo[a.figmaProperty] ?? '—'}\n      ${a.values.join(' | ')}`);
if (booleans.length) console.log(`\n▸ BOOLEAN   ${booleans.map(b => `${b.name}=${b.default}`).join(', ')}`);
if (texts.length) console.log(`▸ TEXT      ${texts.map(t => `${t.name}="${t.default}"`).join(', ')}`);
if (swaps.length) console.log(`▸ SWAP      ${swaps.map(s => s.name).join(', ')}`);
console.log(`\n▸ SIZING    ${Object.keys(sizing).join(', ')}`);
for (const [k, g] of Object.entries(sizing))
  console.log(`   ${k}: ${Object.entries(g).filter(([x]) => !x.startsWith('_')).map(([x, t]) => `${x}=${t}`).join(' · ') || '(nessun binding)'}  [h=${g._measured.height}]`);
console.log(`\n▸ TOKEN     ${Object.keys(tokens).length} combinazioni appearance/hierarchy`);
const sample = Object.entries(tokens)[0];
if (sample) {
  console.log(`   esempio "${sample[0]}":`);
  for (const [st, surf] of Object.entries(sample[1]))
    console.log(`      ${st.padEnd(9)} ${Object.entries(surf).filter(([k]) => !k.startsWith('_')).map(([k, v]) => `${k}=${v}`).join(' · ') || '—'}`);
}
console.log(`\n▸ COPERTURA ${JSON.stringify(contract._coverage, null, 0)}`);
console.log(`\n✅ scritto ${path.relative(ROOT, file)}`);
console.log(`${L}\n`);
