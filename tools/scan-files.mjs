#!/usr/bin/env node
/**
 * Censimento delle pagine dei file Figma:
 *   · lo STATO, che vive nel nome della pagina come emoji (🔴 ❌ ⚠️ …)
 *   · i FRAME DI DOCUMENTAZIONE (`Purpose & Usage`, `Behavior`)
 *
 * Gira su entrambi i DS: la domanda "esiste la documentazione in Figma?" ha
 * risposte diverse per i due file, e va misurata separatamente.
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = `${ROOT}/data`;

const FILES = [
  { ds: 'b2b', key: 'AFsC1fNp7mYe6Qm4l2Cfin' },
  { ds: 'b2c', key: 'QWM2EhgZmv2KKcqI0315fx' },
];

const DOC_RE = /purpose|usage|behavior|behaviour|anatomy|do\s*&|don'?t|guideline/i;
// gli emoji usati come marcatore di stato nel nome della pagina
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{25A0}-\u{25FF}]/gu;

const api = async u => {
  const r = await fetch(`https://api.figma.com/v1/${u}`, { headers: { 'X-Figma-Token': TOKEN } });
  if (!r.ok) throw new Error(`HTTP ${r.status} — ${u}`);
  return r.json();
};

const report = {};

for (const { ds, key } of FILES) {
  const file = await api(`files/${key}?depth=3`);
  const pages = [];
  for (const c of file.document.children ?? []) {
    const hits = [];
    (function w(ns) { for (const n of ns ?? []) { if (DOC_RE.test(n.name ?? '')) hits.push({ id: n.id, name: n.name, type: n.type }); w(n.children); } })(c.children);
    const marks = [...new Set((c.name.match(EMOJI) ?? []))].join('');
    pages.push({
      page: c.name,
      label: c.name.replace(EMOJI, '').trim(),
      status: marks || null,
      children: (c.children ?? []).length,
      docFrames: hits.length,
      frames: hits,          // tutti: troncarli faceva perdere frame reali
    });
  }
  report[ds] = { fileKey: key, fileName: file.name, lastModified: file.lastModified, pages };

  const withDoc = pages.filter(p => p.docFrames > 0);
  const withStatus = pages.filter(p => p.status);
  const L = '─'.repeat(72);
  console.log(`\n${L}\n  ${file.name}   (${ds})\n${L}`);
  console.log(`   pagine ${pages.length} · con documentazione ${withDoc.length} · frame totali ${pages.reduce((s, p) => s + p.docFrames, 0)}`);

  console.log(`\n▸ PAGINE CON DOCUMENTAZIONE`);
  if (!withDoc.length) console.log('   nessuna');
  for (const p of withDoc.slice(0, 25)) console.log(`   ${String(p.docFrames).padStart(3)}  ${p.page}`);
  if (withDoc.length > 25) console.log(`   … e altre ${withDoc.length - 25}`);

  console.log(`\n▸ MARCATORI DI STATO NEI NOMI DI PAGINA`);
  const byMark = {};
  for (const p of withStatus) (byMark[p.status] ??= []).push(p.label);
  for (const [m, list] of Object.entries(byMark).sort((a, b) => b[1].length - a[1].length))
    console.log(`   ${m}  ×${String(list.length).padStart(3)}   ${list.slice(0, 8).join(', ')}${list.length > 8 ? ` … +${list.length - 8}` : ''}`);
}

fs.mkdirSync(OUT, { recursive: true });
fs.writeFileSync(path.join(OUT, 'figma-pages.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`\n✅ scritto out/figma-pages.json\n`);
