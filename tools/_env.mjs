/**
 * Radice della repo e token Figma, senza percorsi assoluti.
 *
 * Prima stavano scritti dentro ogni script come `C:/Users/<nome>/...`, il che
 * rendeva la pipeline inservibile fuori da quella macchina: su un runner
 * GitHub quei percorsi non esistono e l'estrazione muore alla prima riga.
 *
 * Il token si cerca in quest'ordine:
 *   1. FIGMA_TOKEN / FIGMA_ACCESS_TOKEN nell'ambiente   ← come lo passa la CI
 *   2. il file indicato da FIGMA_ENV_FILE
 *   3. .env.local nella radice della repo               ← mai committato
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

/* Nomi accettati, in ordine di preferenza. FIGMA_TOKEN_FULL e' il token con
   tutti gli scope, incluso projects:read che serve a elencare i file. */
const NAMES = ['FIGMA_TOKEN_FULL', 'FIGMA_ACCESS_TOKEN', 'FIGMA_TOKEN'];

const fromFile = p => {
  let txt;
  try { txt = fs.readFileSync(p, 'utf8'); } catch { return null; }
  for (const n of NAMES) {
    const m = txt.match(new RegExp(`^\s*${n}\s*=\s*(.+)$`, 'm'));
    if (m) { const v = m[1].trim().replace(/^["']|["']$/g, ''); if (v) return v; }
  }
  return null;
};

export const TOKEN = (() => {
  for (const n of NAMES) if (process.env[n]?.trim()) return process.env[n].trim();

  const candidates = [
    process.env.FIGMA_ENV_FILE,
    path.join(ROOT, 'credentials.env'),
    path.join(ROOT, '.env.local'),
  ].filter(Boolean);
  for (const p of candidates) {
    const t = fromFile(p);
    if (t) return t;
  }

  console.error([
    '',
    '  Token Figma non trovato. Cercato in:',
    '    variabili d ambiente  FIGMA_TOKEN_FULL, FIGMA_ACCESS_TOKEN, FIGMA_TOKEN',
    '    il file indicato da   FIGMA_ENV_FILE',
    '    credentials.env  e  .env.local  nella radice del progetto',
    '',
  ].join('\n'));
  process.exit(1);
})();
