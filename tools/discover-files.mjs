#!/usr/bin/env node
/**
 * Scopre i file Figma raggiungibili partendo da quelli noti.
 *
 * PERCHE' NON SI USA L'ELENCO DEI TEAM
 * L'endpoint /v1/teams/{id}/projects richiede di appartenere al team. Chi fa
 * parte della sola organizzazione non ci accede. Ma i file si possono scoprire
 * seguendo i riferimenti, che e' anche piu' utile: trova esattamente i file da
 * cui il design system dipende, non tutti quelli che esistono.
 *
 * COME
 *   1. si legge il manifest dei componenti di un file  (?depth=3)
 *   2. per ogni chiave: GET /v1/components/{key} -> meta.file_key
 *   3. ogni file_key mai visto e' un file nuovo, da esplorare a sua volta
 *
 * Il risultato e' un GRAFO: chi dipende da chi.
 *
 *   node tools/discover-files.mjs [--depth N] [fileKey ...]
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = path.join(ROOT, 'data', 'figma-inventory.json');
const MAX_HOPS = Number((process.argv.find(a => a.startsWith('--depth=')) ?? '--depth=3').split('=')[1]);
const CONC = 6;

let calls = 0;
async function api(url, tries = 4) {
  for (let i = 1; i <= tries; i++) {
    try {
      calls++;
      const r = await fetch(`https://api.figma.com/v1/${url}`, {
        headers: { 'X-Figma-Token': TOKEN }, signal: AbortSignal.timeout(90000),
      });
      if (r.ok) return r.json();
      if (r.status >= 500 || r.status === 429) { await new Promise(s => setTimeout(s, 3000 * i)); continue; }
      return { __err: `HTTP ${r.status}` };
    } catch (e) { if (i === tries) return { __err: e.message }; await new Promise(s => setTimeout(s, 3000 * i)); }
  }
}

/* piccola pozza di lavoro: evita di sommergere l'API */
async function pool(items, worker, size = CONC) {
  const out = []; let i = 0;
  await Promise.all(Array.from({ length: Math.min(size, items.length) }, async () => {
    while (i < items.length) { const n = i++; out[n] = await worker(items[n], n); }
  }));
  return out;
}

/* ── semi ─────────────────────────────────────────────────────────────────── */
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, 'config', 'figma-files.json'), 'utf8'));
const fromArgs = process.argv.slice(2).filter(a => !a.startsWith('--'));
const seeds = fromArgs.length ? fromArgs : Object.values(cfg.files).map(f => f.fileKey);

const files = new Map();          // fileKey -> { name, lastModified, hop, viaComponents }
const edges = [];                 // { from, to, componentKey, componentName }
const queue = seeds.map(k => ({ key: k, hop: 0 }));
const seen = new Set(seeds);

console.log(`\n  semi: ${seeds.length}   profondita' massima: ${MAX_HOPS}\n`);

while (queue.length) {
  const { key, hop } = queue.shift();

  const meta = await api(`files/${key}?depth=1`);
  const name = meta.__err ? `(${meta.__err})` : meta.name;
  files.set(key, { name, lastModified: meta.lastModified ?? null, hop, role: hop === 0 ? 'seme' : 'libreria' });
  console.log(`${'  '.repeat(hop)}▸ ${name}   ${key}${meta.__err ? '' : ''}`);
  if (meta.__err || hop >= MAX_HOPS) continue;

  /* manifest dei componenti: serve depth>=3, con depth=1 torna vuoto */
  const tree = await api(`files/${key}?depth=3`);
  if (tree.__err) { console.log(`${'  '.repeat(hop)}    ✖ manifest: ${tree.__err}`); continue; }

  const comps = [
    ...Object.entries(tree.components ?? {}),
    ...Object.entries(tree.componentSets ?? {}),
  ].map(([nodeId, c]) => ({ nodeId, key: c.key, name: c.name })).filter(c => c.key);

  const uniq = [...new Map(comps.map(c => [c.key, c])).values()];
  process.stdout.write(`${'  '.repeat(hop)}    ${uniq.length} componenti da risolvere… `);

  const found = new Map();
  await pool(uniq, async c => {
    const r = await api(`components/${c.key}`);
    const fk = r?.meta?.file_key;
    if (!fk || fk === key) return;
    if (!found.has(fk)) found.set(fk, []);
    found.get(fk).push(c);
    edges.push({ from: key, to: fk, componentKey: c.key, componentName: c.name });
  });

  console.log(`${found.size} file collegati`);
  for (const [fk, via] of found) {
    if (seen.has(fk)) continue;
    seen.add(fk);
    queue.push({ key: fk, hop: hop + 1 });
  }
  for (const [fk, via] of found) {
    const f = files.get(fk); if (f) f.viaComponents = (f.viaComponents ?? 0) + via.length;
  }
}

/* ── risultato ────────────────────────────────────────────────────────────── */
const inventory = {
  discoveredAt: null,                       // stampato fuori: l'artefatto resta canonico
  seeds,
  maxHops: MAX_HOPS,
  files: Object.fromEntries([...files.entries()].sort()),
  edges: edges.sort((a, b) => (a.from + a.to + a.componentKey).localeCompare(b.from + b.to + b.componentKey)),
  totals: { files: files.size, edges: edges.length, apiCalls: calls },
};
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(inventory, null, 2) + '\n');

const L = '─'.repeat(66);
console.log(`\n${L}`);
console.log(`  file scoperti  ${files.size}`);
console.log(`  collegamenti   ${edges.length}`);
console.log(`  chiamate API   ${calls}`);
for (const [k, f] of [...files.entries()].sort((a, b) => a[1].hop - b[1].hop)) {
  console.log(`   ${String(f.hop)}  ${f.name.padEnd(34).slice(0, 34)}  ${k}${f.viaComponents ? `   ←${f.viaComponents} comp.` : ''}`);
}
console.log(`\n  scritto data/figma-inventory.json\n${L}\n`);
