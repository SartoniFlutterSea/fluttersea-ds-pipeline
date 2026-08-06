#!/usr/bin/env node
/**
 * Livelli 0+1 — resolver completo della catena dei token.
 *
 * Segue gli alias attraverso PIÙ FILE Figma: dal token di componente fino al
 * valore letterale nella libreria condivisa a monte.
 *
 *   DS B2B: component → theme → brand
 *              └─→ ❖ Antares Foundations: theme → brand → core → primitive
 *
 * La prova: i valori risolti vengono confrontati con il CSS già committato.
 * Se coincidono, abbiamo riprodotto la pipeline di export.
 *
 *   node resolve-tokens.mjs [brand] [theme]
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, TOKEN } from './_env.mjs';

const OUT = `${ROOT}/data/tokens`;

const FILES = {
  b2b:         { key: 'AFsC1fNp7mYe6Qm4l2Cfin', name: '🏗️ DS B2B' },
  foundations: { key: 'S8U9Li374QCzYEtwFBnaaX', name: '❖ Antares Foundations' },
  mysisal:     { key: 'V1QcyELlWtJTnfrjrRJrfR', name: 'Library MySisal Business' },
};

const BRAND = process.argv[2] ?? 'sisal';
const THEME = process.argv[3] ?? 'light';
const CONTEXT = { brand: BRAND, theme: THEME, device: 'desktop', os: 'ios', direction: 'western' };

/* ── Caricamento ──────────────────────────────────────────────────────────── */
async function load(fileKey) {
  const r = await fetch(`https://api.figma.com/v1/files/${fileKey}/variables/local`,
    { headers: { 'X-Figma-Token': TOKEN } });
  if (!r.ok) return null;
  const { meta } = await r.json();
  const byId = meta.variables, byKey = {};
  for (const v of Object.values(meta.variables)) if (v.key) byKey[v.key] = v;
  return { byId, byKey, cols: meta.variableCollections };
}

const repos = {};
for (const [slug, f] of Object.entries(FILES)) {
  repos[slug] = await load(f.key);
  console.log(`${repos[slug] ? '✅' : '❌'}  ${f.name.padEnd(26)} ${repos[slug] ? Object.keys(repos[slug].byId).length + ' variabili' : 'non accessibile'}`);
}

/* ── Scelta del modo ──────────────────────────────────────────────────────
 * Le collezioni dichiarano la propria dimensione tramite i nomi dei modi.
 * Alcune usano modi COMPOSTI (es. "sisal-light"): vanno provati per primi.
 */
function pickMode(col) {
  const modes = col.modes;
  if (modes.length === 1) return modes[0].modeId;
  const names = modes.map(m => m.name.toLowerCase());

  const composite = `${CONTEXT.brand}-${CONTEXT.theme}`.toLowerCase();
  let i = names.indexOf(composite);
  if (i >= 0) return modes[i].modeId;

  for (const want of [CONTEXT.brand, CONTEXT.theme, CONTEXT.device, CONTEXT.os, CONTEXT.direction]) {
    i = names.indexOf(String(want).toLowerCase());
    if (i >= 0) return modes[i].modeId;
  }
  return modes[0].modeId;   // fallback dichiarato
}

/* ── Risoluzione attraverso i file ────────────────────────────────────────── */
const stats = { literal: 0, unresolved: 0, maxDepth: 0, crossFile: 0, missingKey: new Set() };

function lookup(refId, fromRepo) {
  if (refId.includes('/')) {                       // variabile importata
    const key = refId.replace('VariableID:', '').split('/')[0];
    for (const slug of ['foundations', 'mysisal', 'b2b']) {
      const hit = repos[slug]?.byKey?.[key];
      if (hit) { stats.crossFile++; return { v: hit, repo: repos[slug] }; }
    }
    stats.missingKey.add(key);
    return null;
  }
  const v = fromRepo.byId[refId];
  return v ? { v, repo: fromRepo } : null;
}

function resolve(v, repo, depth = 0, seen = new Set()) {
  if (depth > 16 || seen.has(v.id)) return null;
  seen.add(v.id);
  const col = repo.cols[v.variableCollectionId];
  if (!col) return null;
  const raw = v.valuesByMode[pickMode(col)];
  if (raw && typeof raw === 'object' && raw.type === 'VARIABLE_ALIAS') {
    const next = lookup(raw.id, repo);
    if (!next) return null;
    stats.maxDepth = Math.max(stats.maxDepth, depth + 1);
    return resolve(next.v, next.repo, depth + 1, seen);
  }
  return { value: raw, type: v.resolvedType, depth };
}

/* ── Formattazione CSS ────────────────────────────────────────────────────── */
// Match sui SEGMENTI del path, non come sottostringa: "order" non deve
// pescare "border-radius".
const UNITLESS = /(^|\/)(fontWeight|opacity|zIndex|order|flexGrow|flexShrink|ratio|multiplier)(\/|$)/i;
const hex2 = n => Math.round(n * 255).toString(16).padStart(2, '0');
function toCss(res, name) {
  if (!res || res.value === undefined || res.value === null) return null;
  const v = res.value;
  if (res.type === 'COLOR' && typeof v === 'object') {
    const a = v.a ?? 1;
    return a >= 0.999
      ? `#${(hex2(v.r) + hex2(v.g) + hex2(v.b)).toUpperCase()}`
      : `rgba(${Math.round(v.r * 255)}, ${Math.round(v.g * 255)}, ${Math.round(v.b * 255)}, ${+a.toFixed(4)})`;
  }
  if (res.type === 'FLOAT') return UNITLESS.test(name) ? String(v) : `${v}px`;
  return String(v);
}

/* ── Risolvi tutte le variabili del DS ────────────────────────────────────── */
const cssName = n => '--' + n.split('/').map(s => s.trim()).join('-');
const values = {}, catalog = [];
for (const v of Object.values(repos.b2b.byId)) {
  const col = repos.b2b.cols[v.variableCollectionId];
  const raw = v.valuesByMode[pickMode(col)];
  const res = resolve(v, repos.b2b);
  const name = cssName(v.name);
  const css = toCss(res, v.name);
  if (css === null) stats.unresolved++; else { stats.literal++; values[name] = css; }
  catalog.push({
    id: name.slice(2), name: v.name, type: v.resolvedType,
    level: col?.name ?? null,
    aliasOf: raw?.type === 'VARIABLE_ALIAS' ? raw.id : null,
    hops: res?.depth ?? 0,
  });
}

/* ── La prova: confronto col CSS committato ───────────────────────────────── */
const cssFile = `${B2B_DIR}/src/tokens/${BRAND}.${THEME}.css`;
const committed = {};
for (const m of fs.readFileSync(cssFile, 'utf8').matchAll(/(--[a-zA-Z0-9-]+)\s*:\s*([^;]+);/g))
  committed[m[1]] = m[2].trim();

const norm = s => String(s).toLowerCase().replace(/\s+/g, '');
let same = 0, differ = 0, absent = 0;
const diffs = [];
for (const [k, want] of Object.entries(committed)) {
  if (!(k in values)) { absent++; continue; }
  if (norm(values[k]) === norm(want)) same++;
  else { differ++; if (diffs.length < 12) diffs.push([k, want, values[k]]); }
}

/* ── Output ───────────────────────────────────────────────────────────────── */
fs.mkdirSync(`${OUT}/resolved`, { recursive: true });
fs.writeFileSync(`${OUT}/tokens.json`, JSON.stringify({ count: catalog.length, tokens: catalog.sort((a, b) => a.id.localeCompare(b.id)) }, null, 2));
fs.writeFileSync(`${OUT}/resolved/${BRAND}.${THEME}.json`, JSON.stringify({ brand: BRAND, theme: THEME, values: Object.fromEntries(Object.entries(values).sort()) }, null, 2));

const L = '─'.repeat(70);
console.log(`\n${L}\n  RESOLVER  ${BRAND} / ${THEME}\n${L}`);
console.log(`\n▸ RISOLUZIONE`);
console.log(`   variabili del DS       ${Object.keys(repos.b2b.byId).length}`);
console.log(`   risolte a un valore    ${stats.literal}`);
console.log(`   non risolte            ${stats.unresolved}`);
console.log(`   salti fra file         ${stats.crossFile}`);
console.log(`   profondità max catena  ${stats.maxDepth}`);
console.log(`   chiavi esterne mancanti ${stats.missingKey.size}`);
console.log(`\n▸ CONFRONTO CON ${BRAND}.${THEME}.css`);
console.log(`   token nel CSS          ${Object.keys(committed).length}`);
console.log(`   valore IDENTICO        ${same}   ${Math.round(100 * same / Object.keys(committed).length)}%`);
console.log(`   valore diverso         ${differ}`);
console.log(`   assenti                ${absent}`);
if (diffs.length) {
  console.log(`\n   scostamenti (token · committato · nostro):`);
  diffs.forEach(([k, a, b]) => console.log(`     ${k}\n        atteso ${a}\n        nostro ${b}`));
}
console.log(`\n${L}\n`);
