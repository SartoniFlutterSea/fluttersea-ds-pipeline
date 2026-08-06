import React from 'react';

/**
 * Stato dell'estrazione.
 *
 * Non è un indice: è la misura di quanto della documentazione è già agganciata
 * a Figma. Per ogni componente si vede quali dei tre artefatti esistono — e
 * quindi quanto di quella pagina si aggiorna da solo quando il design cambia.
 */

type Row = {
  slug: string; name: string; id: string;
  has: { contract: boolean; figma: boolean; intent: boolean };
  purpose: string; antiPatterns: number; behaviorKeys: number; props: number;
  variantCount: number; dsContract: string | null; dsIntent: string | null;
  lastModified: string | null;
  reproducibility: Record<string, { figma: number; metadata: number }> | null;
};

export function Overview({ index }: { index: Row[] }) {
  const full = index.filter(r => r.has.contract && r.has.intent && r.has.figma).length;
  const antis = index.reduce((s, r) => s + r.antiPatterns, 0);

  /* Quanto l'estrazione trova in più rispetto a ciò che era scritto a mano. */
  const gains = index.flatMap(r =>
    Object.entries(r.reproducibility ?? {})
      .filter(([, v]) => v && typeof v === 'object' && v.figma > v.metadata)
      .map(([k, v]) => ({ name: r.name, field: k, figma: v.figma, meta: v.metadata }))
  );

  return (
    <div className="ov">
      <style>{CSS}</style>

      <header className="ov-head">
        <h1>Stato dell’estrazione</h1>
        <p className="ov-lead">
          Ogni pagina è costruita da tre artefatti letti da Figma: il{' '}
          <b>contratto</b> (props, token, dimensioni), l’<b>intento</b> (scopo,
          anti-pattern, comportamento) e l’<b>ancoraggio</b> (dove sta e quando
          è cambiato). Quello che vedi qui è quanti componenti li hanno già.
        </p>
      </header>

      <div className="ov-stats">
        <div className="ov-s"><b>{index.length}</b><span>componenti estratti</span></div>
        <div className="ov-s"><b>{full}</b><span>con tutti e tre</span></div>
        <div className="ov-s"><b>{antis}</b><span>anti-pattern</span></div>
        <div className="ov-s"><b>{index.reduce((s, r) => s + r.props, 0)}</b><span>property</span></div>
      </div>

      <div className="ov-note">
        Questa è una <b>prova del meccanismo</b>, non la copertura finale: i
        componenti documentati in Figma sono molti di più. Il passo successivo è
        far girare l’estrazione su tutti.
      </div>

      <section>
        <h2>Componenti</h2>
        <div className="ov-scroll">
          <table>
            <thead>
              <tr>
                <th>Componente</th><th>Artefatti</th>
                <th className="n">Varianti</th><th className="n">Property</th>
                <th className="n">Anti-pattern</th><th>Aggiornato</th>
              </tr>
            </thead>
            <tbody>
              {index.map(r => (
                <tr key={r.slug}>
                  <td>
                    <b>{r.name}</b>
                    <span className="ov-id">{r.id}</span>
                    {r.purpose && <span className="ov-d">{r.purpose.slice(0, 110)}{r.purpose.length > 110 ? '…' : ''}</span>}
                  </td>
                  <td>
                    <div className="ov-dots">
                      <i className={r.has.contract ? 'on' : ''} title="contratto">C</i>
                      <i className={r.has.intent ? 'on' : ''} title="intento">I</i>
                      <i className={r.has.figma ? 'on' : ''} title="ancoraggio">A</i>
                    </div>
                    <span className="ov-src">
                      {r.dsContract && `contratto ${r.dsContract}`}
                      {r.dsContract && r.dsIntent && ' · '}
                      {r.dsIntent && `intento ${r.dsIntent}`}
                    </span>
                  </td>
                  <td className="n">{r.variantCount || <span className="z">—</span>}</td>
                  <td className="n">{r.props || <span className="z">—</span>}</td>
                  <td className="n">{r.antiPatterns || <span className="z">—</span>}</td>
                  <td className="ov-when">{r.lastModified?.slice(0, 10) ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {gains.length > 0 && (
        <section>
          <h2>Dove l’estrazione trova più della documentazione scritta a mano</h2>
          <p className="ov-sub">
            È la ragione per cui la pipeline esiste: legge dai frame Figma cose
            che non erano mai state riportate.
          </p>
          <div className="ov-scroll">
            <table>
              <thead><tr><th>Componente</th><th>Campo</th><th className="n">Da Figma</th><th className="n">A mano</th><th className="n">Differenza</th></tr></thead>
              <tbody>
                {gains.map((g, i) => (
                  <tr key={i}>
                    <td><b>{g.name}</b></td>
                    <td>{g.field.replace(/([a-z])([A-Z])/g, '$1 $2')}</td>
                    <td className="n ok">{g.figma}</td>
                    <td className="n">{g.meta}</td>
                    <td className="n ok">+{g.figma - g.meta}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

const CSS = `
.ov {
  --b: #14161b; --b2: #474d58; --b3: #7b828f;
  --line: #e3e5ea; --soft: #f7f8fa; --ok: #1d6b4a; --warn: #b3341f;
  background: #fff; color: var(--b2); min-height: 100%;
  font: 15px/1.62 ui-sans-serif, "Segoe UI", system-ui, sans-serif;
  padding: 2.3rem clamp(1.2rem, 5vw, 3.2rem) 5rem; max-width: 68rem; margin: 0 auto;
}
.ov * { box-sizing: border-box; }
.ov-head { border-bottom: 2px solid var(--b); padding-bottom: 1.2rem; }
.ov h1 { font: 600 clamp(1.9rem, 4.5vw, 2.6rem)/1.1 inherit; color: var(--b); margin: 0 0 .5rem; letter-spacing: -.015em; }
.ov-lead { margin: 0; max-width: 64ch; }
.ov-lead b { color: var(--b); }
.ov-stats { display: flex; flex-wrap: wrap; gap: 2.4rem; padding: 1.4rem 0; border-bottom: 1px solid var(--line); }
.ov-s { display: grid; gap: .1rem; }
.ov-s b { font: 600 1.9rem/1 inherit; color: var(--b); font-variant-numeric: tabular-nums; }
.ov-s span { font: .7rem/1 ui-monospace, Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--b3); }
.ov-note { background: var(--soft); border-left: 3px solid var(--b3); padding: .8rem 1rem; margin: 1.3rem 0 0; border-radius: 0 3px 3px 0; font-size: .93rem; max-width: 64ch; }
.ov-note b { color: var(--b); }
.ov section { padding-top: 2.2rem; }
.ov h2 { font: 600 .73rem/1.5 ui-monospace, Consolas, monospace; letter-spacing: .13em; text-transform: uppercase; color: var(--b3); margin: 0 0 .8rem; }
.ov-sub { font-size: .9rem; color: var(--b3); margin: -.4rem 0 .9rem; max-width: 62ch; }
.ov-scroll { overflow-x: auto; }
.ov table { border-collapse: collapse; width: 100%; min-width: 44rem; font-size: .9rem; }
.ov th { text-align: left; font: 400 .66rem/1 ui-monospace, Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--b3); padding: .5rem .8rem .5rem 0; border-bottom: 1px solid var(--b3); white-space: nowrap; }
.ov td { padding: .65rem .8rem .65rem 0; border-bottom: 1px solid var(--line); vertical-align: top; }
.ov td b { color: var(--b); display: block; }
.ov-id { display: block; font: .7rem/1.5 ui-monospace, Consolas, monospace; color: var(--b3); }
.ov-d { display: block; font-size: .82rem; color: var(--b3); margin-top: .2rem; max-width: 42ch; }
.ov-dots { display: flex; gap: .25rem; }
.ov-dots i {
  font: 600 .66rem/1.5rem ui-monospace, Consolas, monospace; font-style: normal;
  width: 1.5rem; height: 1.5rem; text-align: center; border-radius: 2px;
  background: var(--soft); color: var(--b3); border: 1px solid var(--line);
}
.ov-dots i.on { background: #e6f0ea; color: var(--ok); border-color: #bcd8c8; }
.ov-src { display: block; font: .68rem/1.5 ui-monospace, Consolas, monospace; color: var(--b3); margin-top: .3rem; }
.ov .n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.ov .z { color: var(--b3); }
.ov .ok { color: var(--ok); font-weight: 600; }
.ov-when { font: .78rem/1.5 ui-monospace, Consolas, monospace; color: var(--b3); white-space: nowrap; }
`;
