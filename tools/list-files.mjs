#!/usr/bin/env node
/**
 * Elenca i file Figma raggiungibili, partendo dai team.
 *
 * L'API Figma NON ha un endpoint "tutti i miei file": il percorso obbligato e'
 *   team  ->  /v1/teams/{id}/projects  ->  /v1/projects/{id}/files
 *
 * Gli identificativi dei team non sono ricavabili dall'API: stanno nell'URL di
 * Figma quando si apre un team.
 *   https://www.figma.com/files/team/1234567890123456789/...
 *                                    ^^^^^^^^^^^^^^^^^^^ questo
 *
 *   node tools/list-files.mjs <teamId> [<teamId> ...]
 *   node tools/list-files.mjs --config          legge config/figma-teams.json
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = path.join(ROOT, 'data', 'figma-teams-inventory.json');

async function api(url, tries = 4) {
  for (let i = 1; i <= tries; i++) {
    try {
      const r = await fetch(`https://api.figma.com/v1/${url}`, {
        headers: { 'X-Figma-Token': TOKEN }, signal: AbortSignal.timeout(60000),
      });
      if (r.ok) return r.json();
      if (r.status >= 500 || r.status === 429) { await new Promise(s => setTimeout(s, 2500 * i)); continue; }
      return { __err: `HTTP ${r.status}`, __body: (await r.text()).slice(0, 200) };
    } catch (e) { if (i === tries) return { __err: e.message }; await new Promise(s => setTimeout(s, 2500 * i)); }
  }
}

/* ── quali team ───────────────────────────────────────────────────────────── */
let teams = process.argv.slice(2).filter(a => !a.startsWith('--'));
if (process.argv.includes('--config')) {
  const p = path.join(ROOT, 'config', 'figma-teams.json');
  if (!fs.existsSync(p)) { console.error(`\n  ✖ manca ${p}\n`); process.exit(1); }
  teams = JSON.parse(fs.readFileSync(p, 'utf8')).teams.map(t => String(t.id));
}
if (!teams.length) {
  console.error(`
  Serve almeno un identificativo di team.

    node tools/list-files.mjs <teamId> [<teamId> ...]

  Dove trovarlo: apri il team su Figma e guarda l'URL.
    https://www.figma.com/files/team/1234567890123456789/Nome
                                     ^^^^^^^^^^^^^^^^^^^
`);
  process.exit(1);
}

/* ── raccolta ─────────────────────────────────────────────────────────────── */
const inventory = { teams: [], totals: { projects: 0, files: 0 }, errors: [] };

for (const teamId of teams) {
  process.stdout.write(`\n▸ team ${teamId}  `);
  const pr = await api(`teams/${teamId}/projects`);
  if (pr.__err) {
    console.log(`✖ ${pr.__err}`);
    inventory.errors.push({ teamId, error: pr.__err, body: pr.__body });
    continue;
  }
  const team = { id: teamId, name: pr.name ?? null, projects: [] };
  console.log(`"${pr.name ?? '—'}"  ·  ${(pr.projects ?? []).length} progetti`);

  for (const p of pr.projects ?? []) {
    const fl = await api(`projects/${p.id}/files`);
    if (fl.__err) {
      console.log(`    ✖ progetto ${p.name}: ${fl.__err}`);
      inventory.errors.push({ projectId: p.id, name: p.name, error: fl.__err });
      continue;
    }
    const files = (fl.files ?? []).map(f => ({
      key: f.key, name: f.name,
      lastModified: f.last_modified ?? null,
      thumbnail: !!f.thumbnail_url,
    }));
    team.projects.push({ id: p.id, name: p.name, files });
    inventory.totals.projects++;
    inventory.totals.files += files.length;
    console.log(`    ${String(files.length).padStart(3)} file  ${p.name}`);
  }
  inventory.teams.push(team);
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(inventory, null, 2) + '\n');

const L = '─'.repeat(64);
console.log(`\n${L}`);
console.log(`  team ${inventory.teams.length} · progetti ${inventory.totals.projects} · file ${inventory.totals.files}`);
if (inventory.errors.length) console.log(`  ⚠️  ${inventory.errors.length} errori, registrati nell'inventario`);
console.log(`  scritto data/figma-teams-inventory.json\n${L}\n`);
