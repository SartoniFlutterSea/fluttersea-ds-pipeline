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

const fromFile = p => {
  try { return fs.readFileSync(p, 'utf8').match(/^FIGMA_ACCESS_TOKEN=(.+)$/m)?.[1]?.trim() || null; }
  catch { return null; }
};

export const TOKEN = (() => {
  const env = process.env.FIGMA_TOKEN || process.env.FIGMA_ACCESS_TOKEN;
  if (env?.trim()) return env.trim();

  for (const p of [process.env.FIGMA_ENV_FILE, path.join(ROOT, '.env.local')].filter(Boolean)) {
    const t = fromFile(p);
    if (t) return t;
  }

  console.error([
    '',
    '  Token Figma non trovato. Una di queste:',
    '    export FIGMA_TOKEN=...',
    '    export FIGMA_ENV_FILE=/percorso/di/.env.local',
    '    creare .env.local nella radice con FIGMA_ACCESS_TOKEN=...',
    '',
  ].join('\n'));
  process.exit(1);
})();
