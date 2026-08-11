#!/usr/bin/env node
/**
 * Unisce i due censimenti in un elenco solo.
 *
 * Nessuno dei due basta da solo:
 *   list-files      vede i file dei progetti a cui si ha accesso, ma non quelli
 *                   in progetti negati (DS B2B sta li')
 *   discover-files  vede i file da cui il design system dipende, anche se
 *                   invisibili nei progetti, ma non quelli scollegati
 *
 * L'unione dice anche COME ogni file e' stato visto: e' l'informazione che
 * distingue "non esiste" da "non ho accesso a quel progetto".
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from './_env.mjs';

const read = p => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } };
const T = read(path.join(ROOT, 'data', 'figma-teams-inventory.json'));
const R = read(path.join(ROOT, 'data', 'figma-inventory.json'));

if (!T && !R) { console.error('\n  ✖ nessun censimento da unire. Eseguire prima list-files e discover-files.\n'); process.exit(1); }

const files = new Map();
const add = (key, patch) => files.set(key, { ...(files.get(key) ?? { key, visto: [] }), ...patch });

for (const t of T?.teams ?? [])
  for (const p of t.projects)
    for (const f of p.files) {
      const cur = files.get(f.key) ?? { key: f.key, visto: [] };
      add(f.key, { nome: f.name, team: t.name, progetto: p.name,
                   lastModified: f.lastModified ?? null, visto: [...cur.visto, 'progetto'] });
    }

for (const [key, f] of Object.entries(R?.files ?? {})) {
  const cur = files.get(key) ?? { key, visto: [] };
  add(key, { nome: cur.nome ?? f.name, lastModified: cur.lastModified ?? f.lastModified ?? null,
             dipendenza: f.hop === 0 ? 'seme' : 'libreria', visto: [...cur.visto, 'riferimento'] });
}

const out = {
  totali: {
    file: files.size,
    daProgetti: [...files.values()].filter(f => f.visto.includes('progetto')).length,
    daRiferimenti: [...files.values()].filter(f => f.visto.includes('riferimento')).length,
    soloRiferimenti: [...files.values()].filter(f => !f.visto.includes('progetto')).length,
  },
  progettiNegati: [...(T?.errors ?? [])].map(e => ({ progetto: e.name ?? e.teamId, errore: e.error })),
  files: Object.fromEntries([...files.entries()].sort()),
};

fs.writeFileSync(path.join(ROOT, 'data', 'figma-censimento.json'), JSON.stringify(out, null, 2) + '\n');

const L = '─'.repeat(62);
console.log(`\n${L}`);
console.log(`  file totali          ${out.totali.file}`);
console.log(`  visti nei progetti   ${out.totali.daProgetti}`);
console.log(`  visti per riferimento ${out.totali.daRiferimenti}`);
console.log(`  SOLO per riferimento ${out.totali.soloRiferimenti}   ← invisibili nei progetti`);
for (const f of [...files.values()].filter(x => !x.visto.includes('progetto')))
  console.log(`     ${(f.nome ?? '?').padEnd(32)}${f.key}`);
if (out.progettiNegati.length) {
  console.log(`\n  progetti non leggibili:`);
  for (const p of out.progettiNegati) console.log(`     ${p.progetto}  ${p.errore}`);
}
console.log(`\n  scritto data/figma-censimento.json\n${L}\n`);
