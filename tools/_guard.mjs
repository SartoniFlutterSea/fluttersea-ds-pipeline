/**
 * Verifica che il nodo scaricato sia davvero il componente chiesto.
 *
 * Serve perche' i due file Figma condividono gli identificativi: il B2B e' un
 * duplicato del B2C, quindi lo stesso nodeId esiste in entrambi e restituisce
 * componenti diversi senza che nulla lo segnali. Senza questo controllo,
 * `build-contract.mjs checkbox 5473-10855` scrive tranquillamente le 90
 * varianti di Button dentro il contratto di Checkbox.
 *
 * Il confronto e' sull'INSIEME delle parole, non sulla stringa: lo slug
 * `button-icon` corrisponde legittimamente al nodo "Icon Button".
 */
const words = s => new Set(
  String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(/\s+/).filter(Boolean)
);

export function assertNodeMatchesSlug(slug, nodeName, { ds, nodeId, force = false } = {}) {
  const a = words(slug), b = words(nodeName);
  const shared = [...a].filter(w => b.has(w)).length;
  const ok = shared > 0 && shared >= Math.min(a.size, b.size);
  if (ok) return;

  const msg = [
    '',
    '  ✖ Il nodo non corrisponde al componente chiesto.',
    '',
    `      slug richiesto   ${slug}`,
    `      nodo ottenuto    "${nodeName}"   (${ds} · ${nodeId})`,
    '',
    '    I due file Figma condividono gli identificativi: lo stesso nodeId',
    '    esiste in entrambi e restituisce componenti diversi. Controllare il',
    '    ds, oppure il nodeId.',
    '',
    '    Se la differenza e\' voluta, ripetere con --force in fondo.',
    '',
  ].join('\n');

  if (force) { console.warn(msg.replace('✖', '⚠')); return; }
  console.error(msg);
  process.exit(1);
}
