import React from 'react';

/**
 * Pagina di un componente, costruita dai tre artefatti estratti da Figma.
 *
 *   contract   i fatti fisici: props, token, sizing, testi
 *   intent     l'intento: purpose, anti-pattern, behavior
 *   figma      l'ancoraggio: dove sta, su quale pagina, quando è cambiato
 *
 * Ogni sezione si nasconde se il dato manca: una pagina con solo il contratto
 * mostra l'API e tace sul resto, invece di stampare caselle vuote.
 */

type Json = any;

const isEmpty = (v: Json): boolean =>
  v === undefined || v === null || v === '' ||
  (Array.isArray(v) && !v.length) ||
  (typeof v === 'object' && !Array.isArray(v) && !Object.keys(v).length);

/* I token e le sizing sono alberi profondi: appiattirli in percorso → valore
   li rende scansionabili, mentre annidarli produce una scala illeggibile. */
function flatten(obj: Json, prefix: string[] = []): Array<[string[], string]> {
  const out: Array<[string[], string]> = [];
  for (const [k, v] of Object.entries(obj ?? {})) {
    if (v && typeof v === 'object' && !Array.isArray(v)) out.push(...flatten(v, [...prefix, k]));
    else if (!isEmpty(v)) out.push([[...prefix, k], String(v)]);
  }
  return out;
}

function Rows({ data }: { data: Json }) {
  const rows = flatten(data);
  if (!rows.length) return null;
  return (
    <div className="cp-scroll">
      <table className="cp-tbl">
        <tbody>
          {rows.map(([p, v], i) => (
            <tr key={i}>
              <td className="cp-path">{p.map((s, j) => (
                <span key={j}>{j > 0 && <em>›</em>}{s}</span>
              ))}</td>
              <td className="cp-val"><code>{v}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Section({ title, count, children }: { title: string; count?: number; children: React.ReactNode }) {
  return (
    <section className="cp-sec">
      <h2>{title}{count !== undefined && <span className="cp-n">{count}</span>}</h2>
      {children}
    </section>
  );
}

/* Le property arrivano da quattro liste distinte del contratto ma per chi legge
   sono una cosa sola: l'API del componente. */
function Api({ contract }: { contract: Json }) {
  const groups: Array<[string, Json[]]> = [
    ['variante', contract.props ?? []],
    ['booleana', contract.booleans ?? []],
    ['testo', contract.texts ?? []],
    ['slot icona', contract.swaps ?? []],
  ];
  const total = groups.reduce((s, [, l]) => s + l.length, 0);
  if (!total) return null;

  return (
    <Section title="Property" count={total}>
      <div className="cp-scroll">
        <table className="cp-tbl cp-tbl--api">
          <thead>
            <tr><th>Nome</th><th>Tipo</th><th>Valori</th><th>Default</th><th>In Figma</th></tr>
          </thead>
          <tbody>
            {groups.flatMap(([kind, list]) =>
              (list ?? []).map((p: Json, i: number) => (
                <tr key={`${kind}-${i}`}>
                  <td><b>{p.name}</b></td>
                  <td><span className="cp-kind">{kind}</span></td>
                  <td>{Array.isArray(p.values)
                    ? <span className="cp-vals">{p.values.map((v: string) => <code key={v}>{v}</code>)}</span>
                    : p.type ? <code>{p.type}</code> : <span className="cp-dim">—</span>}</td>
                  <td>{p.default !== undefined && p.default !== ''
                    ? <code>{String(p.default)}</code> : <span className="cp-dim">—</span>}</td>
                  <td className="cp-dim">{p.figmaProperty ?? '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

export function ComponentPage({ slug, contract, intent, figma }: {
  slug: string; contract: Json; intent: Json; figma: Json;
}) {
  const name = contract?.name ?? intent?.componentName ?? slug;
  const id = contract?.id ?? intent?.id;
  const antis = intent?.antiPatterns ?? [];
  const behavior = intent?.behavior ?? {};
  const patterns = intent?.commonPatterns ?? [];
  const repro = intent?._reproducibility;

  const figmaUrl = (fileKey: string, node: string) =>
    `https://www.figma.com/design/${fileKey}/?node-id=${String(node).replace(':', '-')}`;

  return (
    <div className="cp">
      <style>{CSS}</style>

      <header className="cp-head">
        <div className="cp-kick">
          {id && <code>{id}</code>}
          {figma?.variantCount ? <span>{figma.variantCount} varianti</span> : null}
          {figma?.nodeType && <span>{figma.nodeType}</span>}
        </div>
        <h1>{name}</h1>
        {intent?.purpose && <p className="cp-lead">{intent.purpose}</p>}

        {/* Da dove viene ogni pezzo: è l'informazione che dice quanto fidarsi. */}
        <div className="cp-prov">
          <span className={contract ? 'on' : 'off'}>
            contratto{contract?.source?.ds ? ` · ${contract.source.ds}` : ''}
          </span>
          <span className={intent ? 'on' : 'off'}>
            intento{intent?._source?.ds ? ` · ${intent._source.ds}` : ''}
          </span>
          <span className={figma ? 'on' : 'off'}>
            ancoraggio{figma?.lastModified ? ` · ${figma.lastModified.slice(0, 10)}` : ''}
          </span>
        </div>
      </header>

      {antis.length > 0 && (
        <Section title="Anti-pattern" count={antis.length}>
          <div className="cp-stack">
            {antis.map((a: Json, i: number) => (
              <div className="cp-anti" key={i}>
                <p className="cp-anti-t">{a.scenario}</p>
                {a.reason && <p><span className="cp-k">Perché è sbagliato</span>{a.reason}</p>}
                {a.alternative && <p><span className="cp-k">Cosa usare invece</span>{a.alternative}</p>}
                <div className="cp-anti-m">
                  {a.origin && <span>{a.origin}</span>}
                  {a.section && <span>{a.section}</span>}
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {!isEmpty(behavior) && (
        <Section title="Comportamento">
          {Object.entries(behavior).map(([platform, spec]) => (
            <div className="cp-plat" key={platform}>
              <h3>{platform}</h3>
              <dl className="cp-dl">
                {Object.entries(spec as Json).filter(([, v]) => !isEmpty(v)).map(([k, v]) => (
                  <div key={k}>
                    <dt>{k.replace(/([a-z])([A-Z])/g, '$1 $2')}</dt>
                    <dd>{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          ))}
        </Section>
      )}

      {patterns.length > 0 && (
        <Section title="Pattern ricorrenti" count={patterns.length}>
          <div className="cp-stack">
            {patterns.map((p: Json, i: number) => (
              <div className="cp-item" key={i}>
                {p.name && <b>{p.name}</b>}
                <span>{p.description ?? (typeof p === 'string' ? p : '')}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {contract && <Api contract={contract} />}

      {contract && !isEmpty(contract.sizing) && (
        <Section title="Dimensioni"><Rows data={contract.sizing} /></Section>
      )}

      {contract && !isEmpty(contract.tokens) && (
        <Section title="Token" count={flatten(contract.tokens).length}>
          <p className="cp-hint">
            Sempre per nome, mai per valore: i colori cambiano per brand alla compilazione.
          </p>
          <Rows data={contract.tokens} />
        </Section>
      )}

      {repro && (
        <Section title="Qualità dell’estrazione">
          <p className="cp-hint">
            Confronto fra ciò che la pipeline ha letto da Figma e ciò che era scritto a mano.
          </p>
          <div className="cp-scroll">
            <table className="cp-tbl cp-tbl--api">
              <thead><tr><th>Campo</th><th>Da Figma</th><th>Scritto a mano</th></tr></thead>
              <tbody>
                {Object.entries(repro).filter(([, v]) => v && typeof v === 'object').map(([k, v]: [string, Json]) => (
                  <tr key={k}>
                    <td><b>{k.replace(/([a-z])([A-Z])/g, '$1 $2')}</b></td>
                    <td className={v.figma >= v.metadata ? 'cp-win' : ''}>{v.figma}</td>
                    <td className={v.metadata > v.figma ? 'cp-win' : ''}>{v.metadata}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {contract?._coverage && (
        <Section title="Cosa è stato misurato">
          <Rows data={contract._coverage} />
        </Section>
      )}

      {(figma?.fileKey || intent?._source) && (
        <Section title="Su Figma">
          <div className="cp-links">
            {figma?.fileKey && figma?.nodes && Object.entries(figma.nodes).map(([k, v]) => (
              <a key={k} href={figmaUrl(figma.fileKey, v as string)} target="_blank" rel="noreferrer">
                {figma.fileName ?? k} · componente →
              </a>
            ))}
            {intent?._source?.fileKey && intent?._source?.purposeFrame && (
              <a href={figmaUrl(intent._source.fileKey, intent._source.purposeFrame.id)} target="_blank" rel="noreferrer">
                Purpose &amp; Usage →
              </a>
            )}
            {intent?._source?.fileKey && intent?._source?.behaviorFrame && (
              <a href={figmaUrl(intent._source.fileKey, intent._source.behaviorFrame.id)} target="_blank" rel="noreferrer">
                Behavior →
              </a>
            )}
          </div>
        </Section>
      )}
    </div>
  );
}

const CSS = `
.cp {
  --b: #14161b; --b2: #474d58; --b3: #7b828f;
  --line: #e3e5ea; --soft: #f7f8fa; --acc: #1e3fcc; --warn: #b3341f; --ok: #1d6b4a;
  background: #fff; color: var(--b2); min-height: 100%;
  font: 15px/1.62 ui-sans-serif, "Segoe UI", system-ui, sans-serif;
  padding: 2.3rem clamp(1.2rem, 5vw, 3.2rem) 5rem; max-width: 64rem; margin: 0 auto;
}
.cp * { box-sizing: border-box; }
.cp-head { border-bottom: 2px solid var(--b); padding-bottom: 1.2rem; }
.cp-kick { display: flex; flex-wrap: wrap; gap: .45rem .9rem; margin-bottom: .6rem; }
.cp-kick > * {
  font: .69rem/1 ui-monospace, Consolas, monospace; letter-spacing: .08em;
  text-transform: uppercase; color: var(--b3); border: 1px solid var(--line);
  border-radius: 2px; padding: .3rem .5rem; background: none;
}
.cp h1 { font: 600 clamp(1.9rem, 4.6vw, 2.7rem)/1.08 inherit; color: var(--b); margin: 0 0 .6rem; letter-spacing: -.015em; }
.cp-lead { margin: 0 0 1rem; font-size: 1.04rem; max-width: 62ch; }
.cp-prov { display: flex; flex-wrap: wrap; gap: .4rem; }
.cp-prov span {
  font: .7rem/1 ui-monospace, Consolas, monospace; padding: .32rem .55rem; border-radius: 2px;
}
.cp-prov .on  { background: #e6f0ea; color: var(--ok); }
.cp-prov .off { background: var(--soft); color: var(--b3); text-decoration: line-through; }
.cp-sec { padding: 1.7rem 0; border-bottom: 1px solid var(--line); }
.cp-sec:last-child { border-bottom: 0; }
.cp h2 {
  font: 600 .73rem/1 ui-monospace, Consolas, monospace; letter-spacing: .13em;
  text-transform: uppercase; color: var(--b3); margin: 0 0 .9rem;
  display: flex; align-items: center; gap: .5rem;
}
.cp-n { background: var(--b); color: #fff; border-radius: 9px; padding: .1rem .44rem; font-size: .68rem; letter-spacing: 0; }
.cp-hint { font-size: .88rem; color: var(--b3); margin: -.4rem 0 .9rem; max-width: 62ch; }
.cp-stack { display: grid; gap: .7rem; }
.cp-item { padding-left: .9rem; border-left: 2px solid var(--line); display: grid; gap: .12rem; }
.cp-item b { color: var(--b); }
.cp-anti { background: var(--soft); border-left: 3px solid var(--warn); border-radius: 0 3px 3px 0; padding: .85rem 1.05rem; }
.cp-anti p { margin: 0 0 .5rem; }
.cp-anti-t { font-weight: 600; color: var(--b); }
.cp-k { display: block; font: .65rem/1 ui-monospace, Consolas, monospace; letter-spacing: .11em; text-transform: uppercase; color: var(--b3); margin-bottom: .2rem; }
.cp-anti-m { display: flex; gap: .4rem; }
.cp-anti-m span { font: .64rem/1 ui-monospace, Consolas, monospace; color: var(--b3); border: 1px solid var(--line); border-radius: 2px; padding: .2rem .38rem; background: #fff; }
.cp-plat + .cp-plat { margin-top: 1.2rem; }
.cp h3 { font: 600 .95rem/1 inherit; color: var(--b); margin: 0 0 .5rem; }
.cp-dl { margin: 0; display: grid; gap: .6rem; }
.cp-dl > div { display: grid; grid-template-columns: 11rem minmax(0, 1fr); gap: 0 1.2rem; }
.cp-dl dt { font-weight: 600; color: var(--b); font-size: .88rem; text-transform: capitalize; }
.cp-dl dd { margin: 0; white-space: pre-line; }
@media (max-width: 640px) { .cp-dl > div { grid-template-columns: 1fr; gap: .15rem; } }
.cp-scroll { overflow-x: auto; }
.cp-tbl { border-collapse: collapse; width: 100%; font-size: .88rem; }
.cp-tbl td, .cp-tbl th { padding: .42rem .8rem .42rem 0; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
.cp-tbl th { font: 400 .66rem/1 ui-monospace, Consolas, monospace; letter-spacing: .1em; text-transform: uppercase; color: var(--b3); border-bottom: 1px solid var(--b3); white-space: nowrap; }
.cp-tbl--api { min-width: 34rem; }
.cp-tbl b { color: var(--b); }
.cp-path { font: .8rem/1.5 ui-monospace, Consolas, monospace; color: var(--b2); white-space: nowrap; }
.cp-path em { color: var(--b3); font-style: normal; margin: 0 .3rem; }
.cp-val code, .cp-tbl code {
  font: .8em/1.4 ui-monospace, Consolas, monospace; background: var(--soft);
  border: 1px solid var(--line); border-radius: 2px; padding: .08em .34em; color: var(--b);
  overflow-wrap: anywhere;
}
.cp-vals { display: flex; flex-wrap: wrap; gap: .25rem; }
.cp-kind { font: .68rem/1 ui-monospace, Consolas, monospace; color: var(--b3); }
.cp-dim { color: var(--b3); }
.cp-win { color: var(--ok); font-weight: 600; }
.cp-links { display: flex; flex-wrap: wrap; gap: .45rem; }
.cp-links a {
  font: .8rem/1 ui-monospace, Consolas, monospace; color: var(--acc); text-decoration: none;
  border: 1px solid var(--acc); border-radius: 2px; padding: .45rem .65rem;
}
.cp-links a:hover, .cp-links a:focus-visible { background: var(--acc); color: #fff; }
`;
