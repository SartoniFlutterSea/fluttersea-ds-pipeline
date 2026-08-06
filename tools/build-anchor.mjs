#!/usr/bin/env node
/**
 * Livello 2 — figma.json: l'ANCORAGGIO.
 *
 * È l'input dell'estrazione, non il suo output: serve per sapere cosa andare a
 * prendere. Per questo è un file a sé e non un blocco dentro contract.json —
 * cambia solo quando un nodo si sposta, mentre il contratto cambia a ogni
 * pubblicazione.
 *
 * Cerca anche i FRAME DI DOCUMENTAZIONE nel file: è la misura di PA-19, che
 * non era mai stata fatta.
 *
 *   node build-anchor.mjs <slug> <nodeId>
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = `${ROOT}/data/contracts`;

/* Vedi nota in figma-files.json: gli id sono condivisi fra i due file, il ds
   deve essere esplicito. */
const CFG = JSON.parse(fs.readFileSync(`${ROOT}/config/figma-files.json`, 'utf8'));

const slug = process.argv[2] ?? 'button';
const nodeId = process.argv[3] ?? '5473-10855';
const ds = process.argv[4] ?? CFG.default;

if (!CFG.files[ds]) {
  console.error(`\n  ✖ ds sconosciuto: "${ds}" — attesi: ${Object.keys(CFG.files).join(', ')}\n`);
  process.exit(1);
}
const FILE = CFG.files[ds].fileKey;

/* Su B2C un componente ha un nodo per piattaforma: si leggono dal metadata,
   se esiste. Su B2B la piattaforma è una sola. */
let platformNodes = { default: nodeId };
try {
  const m = JSON.parse(fs.readFileSync(`${ROOT}/components/${slug}/docs/metadata.json`, 'utf8'));
  if (m.figmaNodeIds && ds === 'b2c') {
    const { propertyTable, ...plat } = m.figmaNodeIds;
    if (Object.keys(plat).length) platformNodes = plat;
  }
} catch { /* nessun metadata: si resta al nodo passato a riga di comando */ }

const api = async u => {
  const r = await fetch(`https://api.figma.com/v1/${u}`, { headers: { 'X-Figma-Token': TOKEN } });
  if (!r.ok) throw new Error(`HTTP ${r.status} — ${u}`);
  return r.json();
};

/* ── il nodo ──────────────────────────────────────────────────────────────── */
const nodes = await api(`files/${FILE}/nodes?ids=${nodeId}`);
const entry = Object.values(nodes.nodes)[0];
const doc = entry.document;

/* ── i frame di documentazione esistono? (PA-19) ─────────────────────────── */
const DOC_RE = /purpose|usage|behavior|behaviour|anatomy|do\s*&|don'?t|guideline|spec|documentation|linee guida/i;
const file = await api(`files/${FILE}?depth=3`);
const found = [];
const canvases = file.document.children ?? [];
(function walk(nodes, page, depth = 0) {
  for (const n of nodes ?? []) {
    if (depth > 0 && DOC_RE.test(n.name ?? '')) found.push({ page, id: n.id, name: n.name, type: n.type });
    walk(n.children, page, depth + 1);
  }
})(canvases.flatMap(c => (c.children ?? []).map(x => ({ ...x, _page: c.name }))), null, 1);

// rifatto in modo leggibile: per pagina
const byPage = [];
for (const c of canvases) {
  const hits = [];
  (function w(ns) { for (const n of ns ?? []) { if (DOC_RE.test(n.name ?? '')) hits.push({ id: n.id, name: n.name, type: n.type }); w(n.children); } })(c.children);
  byPage.push({ page: c.name, id: c.id, children: (c.children ?? []).length, docFrames: hits });
}

/* ── lo stato, dal marcatore nel nome della pagina ───────────────────────── */
const STATUS = JSON.parse(fs.readFileSync(
  `${ROOT}/config/figma-status.json`, 'utf8'));
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{25A0}-\u{25FF}]/gu;

// la pagina che contiene il nodo. `depth=3` può non arrivare al nodo, quindi
// se la ricerca nell'albero fallisce si rilegge il file più in profondità.
const wanted = nodeId.replace('-', ':');
const contains = c => { let hit = false; (function w(ns) { for (const n of ns ?? []) { if (n.id === wanted) hit = true; w(n.children); } })(c.children); return hit; };
let ownerPage = canvases.find(contains);
if (!ownerPage) {
  const deep = await api(`files/${FILE}?depth=5`);
  ownerPage = (deep.document.children ?? []).find(contains);
}
const marker = ownerPage ? [...new Set((ownerPage.name.match(EMOJI) ?? []))].join('') : null;
const map = STATUS[/DS B2B/.test(file.name) ? 'b2b' : 'b2c'] ?? {};

const anchor = {
  id: `ds.${slug}`,
  fileKey: FILE,
  fileName: file.name,
  ds,
  nodes: platformNodes,                    // b2c: un nodo per piattaforma · b2b: uno solo
  nodeType: doc.type,
  nodeName: doc.name,
  variantCount: (doc.children ?? []).length,
  parts: {},                               // sotto-nodi, se e quando servono
  page: ownerPage ? {
    id: ownerPage.id,
    name: ownerPage.name,
    label: ownerPage.name.replace(EMOJI, '').trim(),
    marker: marker || null,
    status: marker ? (map[marker] ?? 'unknown') : null,
  } : null,
  documentation: byPage.filter(p => p.docFrames.length)
    .map(p => ({ page: p.page, frames: p.docFrames })),
  lastModified: file.lastModified,
};

fs.mkdirSync(OUT, { recursive: true });
const dir = path.join(OUT, slug);
fs.mkdirSync(dir, { recursive: true });
const out = path.join(dir, 'figma.json');
fs.writeFileSync(out, JSON.stringify(anchor, null, 2) + '\n');

const L = '─'.repeat(70);
console.log(`\n${L}\n  ANCORAGGIO — ${doc.name}\n${L}`);
console.log(`\n   file      "${file.name}"  ${FILE}`);
console.log(`   nodo      ${nodeId}  ${doc.type}  ·  ${anchor.variantCount} varianti`);
console.log(`   modificato ${file.lastModified}`);
console.log(`\n▸ PAGINE DEL FILE (${canvases.length})`);
for (const p of byPage) console.log(`   ${String(p.children).padStart(4)} figli  ${p.page}${p.docFrames.length ? `   ← ${p.docFrames.length} frame di doc` : ''}`);
const total = byPage.reduce((s, p) => s + p.docFrames.length, 0);
console.log(`\n▸ FRAME DI DOCUMENTAZIONE  (misura di PA-19)`);
console.log(`   trovati: ${total}`);
for (const p of byPage.filter(x => x.docFrames.length)) {
  console.log(`   — ${p.page}`);
  p.docFrames.slice(0, 8).forEach(f => console.log(`        ${f.type.padEnd(14)} ${f.name}`));
}
if (!total) console.log(`   ⚠️  nessun frame con nomi tipo Purpose / Usage / Behavior / Anatomy / Do & Don't`);
console.log(`\n✅ scritto data/contracts/${slug}/figma.json\n${L}\n`);
