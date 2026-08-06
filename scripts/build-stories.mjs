#!/usr/bin/env node
/**
 * Genera le storie di Storybook dagli artefatti estratti da Figma.
 *
 * FONTE: data/contracts/<slug>/{contract,figma,intent}.json
 *   contract  i fatti fisici  — props, token, sizing, testi        (da b2b)
 *   intent    l'intento       — purpose, anti-pattern, behavior     (da b2c)
 *   figma     l'ancoraggio    — dove sta, su quale pagina, quando
 *
 * Un componente entra nel sito se ha ALMENO UNO dei tre file. Le storie in
 * storybook/generated/ sono derivate: si riscrivono a ogni esecuzione e non
 * vanno committate.
 *
 *   node scripts/build-stories.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.join(ROOT, 'data', 'contracts');
const OUT = path.join(ROOT, 'storybook', 'generated');
const REL = 'data/contracts';

const read = p => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } };
const safe = s => String(s).replace(/[/|]/g, '-').trim();
const titleCase = s => s.replace(/(^|[-_ ])(\w)/g, (_, a, b) => (a ? ' ' : '') + b.toUpperCase()).trim();

/* ── quali componenti esistono ────────────────────────────────────────────── */
if (!fs.existsSync(SRC)) {
  console.error(`\n  ✖ Nessun artefatto in ${REL}/`);
  console.error(`    Esegui prima l'estrazione (tools/build-contract.mjs e simili).\n`);
  process.exit(1);
}

/* Una cartella per componente: dentro, i tre artefatti. */
const KINDS = ['contract', 'figma', 'intent'];
const slugs = fs.readdirSync(SRC, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => d.name)
  .filter(s => KINDS.some(k => fs.existsSync(path.join(SRC, s, `${k}.json`))))
  .sort();

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const index = [];

for (const slug of slugs) {
  const at = k => path.join(SRC, slug, `${k}.json`);
  const has = Object.fromEntries(KINDS.map(k => [k, fs.existsSync(at(k))]));
  const contract = has.contract ? read(at('contract')) : null;
  const intent   = has.intent   ? read(at('intent'))   : null;
  const figma    = has.figma    ? read(at('figma'))    : null;

  const name = safe(contract?.name || intent?.componentName || titleCase(slug));

  index.push({
    slug, name, has,
    id: contract?.id || intent?.id || `ds.${slug}`,
    purpose: intent?.purpose ?? '',
    antiPatterns: intent?.antiPatterns?.length ?? 0,
    behaviorKeys: intent?.behavior ? Object.keys(intent.behavior).length : 0,
    props: (contract?.props?.length ?? 0) + (contract?.booleans?.length ?? 0)
         + (contract?.texts?.length ?? 0) + (contract?.swaps?.length ?? 0),
    variantCount: figma?.variantCount ?? 0,
    dsContract: contract?.source?.ds ?? null,
    dsIntent: intent?._source?.ds ?? null,
    lastModified: figma?.lastModified ?? null,
    reproducibility: intent?._reproducibility ?? null,
  });

  /* Import solo dei file che esistono: un import mancante rompe il build. */
  const imports = [
    has.contract && `import contract from '../../${REL}/${slug}/contract.json';`,
    has.intent   && `import intent   from '../../${REL}/${slug}/intent.json';`,
    has.figma    && `import figma    from '../../${REL}/${slug}/figma.json';`,
  ].filter(Boolean).join('\n');

  const args = [
    'slug: ' + JSON.stringify(slug),
    has.contract ? 'contract' : 'contract: null',
    has.intent   ? 'intent'   : 'intent: null',
    has.figma    ? 'figma'    : 'figma: null',
  ].join(', ');

  fs.writeFileSync(path.join(OUT, `${slug}.stories.tsx`), `// GENERATO da scripts/build-stories.mjs — non modificare a mano.
import { ComponentPage } from '../ComponentPage';
${imports}

export default {
  title: 'Componenti/${name}',
  component: ComponentPage,
};

export const Documentazione = { args: { ${args} } };
Documentazione.storyName = 'Documentazione';
`);
}

/* ── panoramica ───────────────────────────────────────────────────────────── */
index.sort((a, b) => a.name.localeCompare(b.name));
fs.writeFileSync(path.join(OUT, '_index.json'), JSON.stringify(index, null, 2) + '\n');

fs.writeFileSync(path.join(OUT, 'Panoramica.stories.tsx'),
  `// GENERATO da scripts/build-stories.mjs — non modificare a mano.
import { Overview } from '../Overview';
import index from './_index.json';

export default { title: 'Panoramica/Stato dell’estrazione', component: Overview };
export const Stato = { args: { index } };
Stato.storyName = 'Stato dell’estrazione';
`);

/* ── resoconto ────────────────────────────────────────────────────────────── */
const n = k => index.filter(x => x.has[k]).length;
console.log(`\n  componenti        ${index.length}   (${index.map(x => x.name).join(', ')})`);
console.log(`  con contract      ${n('contract')}`);
console.log(`  con intent        ${n('intent')}`);
console.log(`  con figma         ${n('figma')}`);
console.log(`  anti-pattern      ${index.reduce((s, x) => s + x.antiPatterns, 0)}`);
console.log(`  output            storybook/generated/\n`);
